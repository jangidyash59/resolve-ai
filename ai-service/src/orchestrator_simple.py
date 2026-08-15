"""
Simplified orchestrator using Groq SDK directly (no CrewAI)
Uses Google Gemini for embeddings (reliable, free, production-ready)
"""
import json
import os
import re
from pathlib import Path

import faiss
import numpy as np
from dotenv import load_dotenv
from groq import Groq
from google import genai

from src.models import FinalResolution, TicketInput

load_dotenv()

# Configure Gemini API with new client
gemini_api_key = os.getenv("GEMINI_API_KEY")
gemini_client = None
if gemini_api_key:
    gemini_client = genai.Client(api_key=gemini_api_key)

groq_client = None
MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
EMBEDDING_MODEL = "gemini-embedding-001"  # Gemini embedding model (768-dim)

PROJECT_DIRECTORY = Path(__file__).resolve().parent.parent
POLICIES_DIRECTORY = PROJECT_DIRECTORY / "data" / "policies"
configured_faiss_directory = Path(os.getenv("VECTOR_STORE_PATH", "faiss_store"))
FAISS_DIRECTORY = configured_faiss_directory if configured_faiss_directory.is_absolute() else PROJECT_DIRECTORY / configured_faiss_directory
FAISS_INDEX_PATH = FAISS_DIRECTORY / "index.faiss"
FAISS_METADATA_PATH = FAISS_DIRECTORY / "metadata.json"

faiss_index = None
indexed_policies = []

def get_groq_client():
    global groq_client
    if groq_client is None:
        groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return groq_client

def safe_json(text, fallback):
    try:
        return json.loads(text)
    except:
        match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except:
                pass
        return fallback

def chat(prompt, temperature=0.3):
    client = get_groq_client()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    text = response.choices[0].message.content or ""
    return re.sub(r"```(?:json)?", "", text).replace("```", "").strip()

def load_and_chunk_policy_documents():
    all_policy_chunks = []
    policy_files = list(POLICIES_DIRECTORY.glob("*.md"))
    for policy_file in policy_files:
        print(f"Reading: {policy_file.name}")
        with open(policy_file, "r") as f:
            content = f.read()
        sections = []
        current_heading = "Introduction"
        current_lines = []
        for line in content.split("\n"):
            if line.startswith("#"):
                if current_lines:
                    sections.append((current_heading, "\n".join(current_lines)))
                current_heading = line.strip("# ")
                current_lines = []
            else:
                current_lines.append(line)
        if current_lines:
            sections.append((current_heading, "\n".join(current_lines)))
        for section_number, (heading, section_text) in enumerate(sections):
            words = section_text.split()
            chunk_size = 800
            for i in range(0, len(words), chunk_size):
                chunk_text = " ".join(words[i:i+chunk_size])
                policy_record = {
                    "id": f"{policy_file.stem}-section-{section_number}-chunk-{i//chunk_size}",
                    "source": policy_file.name,
                    "section": heading,
                    "text": chunk_text
                }
                all_policy_chunks.append(policy_record)
    print(f"\nCreated {len(all_policy_chunks)} policy chunks.")
    return all_policy_chunks

def create_embeddings(texts):
    """
    Generates embeddings using the new google-genai library.
    Handles batching for API limits (processes one at a time).
    """
    if not gemini_client:
        raise ValueError("GEMINI_API_KEY not set")
    
    embeddings = []
    total = len(texts) if isinstance(texts, list) else 1
    
    # Handle both single text and list of texts
    text_list = texts if isinstance(texts, list) else [texts]
    
    for idx, text in enumerate(text_list, 1):
        if idx % 50 == 0:
            print(f"  Embedded {idx}/{total} chunks...")
        
        response = gemini_client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=text
        )
        embeddings.append(response.embeddings[0].values)
    
    return embeddings if isinstance(texts, list) else embeddings[0]

def build_policy_index():
    """
    Load pre-built FAISS index or build if it doesn't exist.
    """
    global faiss_index, indexed_policies
    
    if FAISS_INDEX_PATH.exists() and FAISS_METADATA_PATH.exists():
        print("Loading pre-built FAISS index...")
        faiss_index = faiss.read_index(str(FAISS_INDEX_PATH))
        with open(FAISS_METADATA_PATH, "r") as f:
            saved_metadata = json.load(f)
        indexed_policies = saved_metadata.get("policies", [])
        print(f"✓ Loaded {len(indexed_policies)} policy vectors from pre-built index.")
        return
    
    # Build index if it doesn't exist
    print("Building FAISS index with Gemini embeddings...")
    FAISS_DIRECTORY.mkdir(parents=True, exist_ok=True)
    
    current_policies = load_and_chunk_policy_documents()
    print("Creating embeddings...")
    texts = [p["text"] for p in current_policies]
    embeddings = create_embeddings(texts)
    embedding_matrix = np.array(embeddings).astype("float32")
    dimension = embedding_matrix.shape[1]
    
    faiss_index = faiss.IndexFlatL2(dimension)
    faiss_index.add(embedding_matrix)
    indexed_policies = current_policies
    
    faiss.write_index(faiss_index, str(FAISS_INDEX_PATH))
    with open(FAISS_METADATA_PATH, "w") as f:
        json.dump({"policies": indexed_policies, "embedding_model": EMBEDDING_MODEL}, f)
    print(f"✓ FAISS knowledge base created with {len(indexed_policies)} vectors ({dimension}-dim).")

def search_policies(query, number_of_results=3):
    """
    Semantic search using pre-built FAISS index and Gemini API for query embeddings.
    """
    try:
        # Get query embedding from Gemini
        response = gemini_client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=query  # Changed from 'content' to 'contents'
        )
        query_embedding = response.embeddings[0].values
        
        # Search FAISS index
        query_vector = np.array([query_embedding]).astype("float32")
        distances, indices = faiss_index.search(query_vector, number_of_results)
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            policy = indexed_policies[idx]
            similarity = float(1.0 / (1.0 + distance))
            results.append({
                "citation": f"{policy['source']} — {policy['section']}",
                "text": policy["text"],
                "similarity": round(similarity, 3)
            })
        return results
    except Exception as e:
        print(f"Semantic search error: {e}")
        # Fallback to keyword search
        return keyword_search_fallback(query, number_of_results)

def keyword_search_fallback(query, number_of_results=3):
    """Keyword-based fallback when semantic search fails."""
    if not indexed_policies:
        return []
    
    query_lower = query.lower()
    query_words = set(query_lower.split())
    
    scored = []
    for policy in indexed_policies:
        text_lower = policy["text"].lower()
        words = set(text_lower.split())
        
        matches = len(query_words.intersection(words))
        substring = 10 if query_lower in text_lower else 0
        score = matches + substring
        
        if score > 0:
            scored.append({
                "citation": f"{policy['source']} — {policy['section']}",
                "text": policy["text"],
                "similarity": round(min(score / 20.0, 0.9), 3)
            })
    
    scored.sort(key=lambda x: x["similarity"], reverse=True)
    return scored[:number_of_results] if scored else [
        {
            "citation": f"{p['source']} — {p['section']}",
            "text": p["text"],
            "similarity": 0.5
        }
        for p in indexed_policies[:number_of_results]
    ]

def triage_ticket(ticket_text, order_context):
    prompt = f"""You are a customer support triage agent. Analyze this support ticket.

Ticket: "{ticket_text}"
Order: {json.dumps(order_context, indent=2)}

Classify issue type (returns, shipping, payment, technical, account, other) and priority (low, medium, high, urgent).

Return ONLY JSON:
{{"issue_type": "...", "priority": "...", "requires_escalation": false, "rationale": "..."}}"""
    return safe_json(chat(prompt), {"issue_type": "other", "priority": "medium", "requires_escalation": False, "rationale": ""})

def generate_resolution(ticket_text, policies, order_context, classification):
    policy_text = "\n\n".join([f"[{p['citation']}]\n{p['text']}" for p in policies])
    prompt = f"""You are a customer support agent. Generate a helpful response.

Ticket: "{ticket_text}"
Classification: {json.dumps(classification)}
Order: {json.dumps(order_context, indent=2)}

Policies:
{policy_text}

Return ONLY JSON:
{{"customer_response": "...", "internal_notes": "...", "next_steps": ["..."], "citations": ["..."]}}"""
    return safe_json(chat(prompt, 0.5), {"customer_response": "Thank you. We'll respond shortly.", "internal_notes": "", "next_steps": [], "citations": []})

def run_resolution_pipeline(ticket_text, order_context):
    classification = triage_ticket(ticket_text, order_context)
    policies = search_policies(ticket_text, 3)
    resolution = generate_resolution(ticket_text, policies, order_context, classification)
    return {
        "classification": classification,
        "status": "resolved",
        "customer_response": resolution.get("customer_response", ""),
        "internal_notes": resolution.get("internal_notes", ""),
        "next_steps": resolution.get("next_steps", []),
        "citations": resolution.get("citations", []),
        "requires_escalation": classification.get("requires_escalation", False),
        "rationale": classification.get("rationale", "")
    }

class SupportOrchestrator:
    def __init__(self):
        build_policy_index()
    
    def resolve_ticket(self, ticket):
        order_context = ticket.order_context.model_dump(mode="json") if ticket.order_context else {}
        order_context["customer"] = {"name": ticket.customer_name, "loyalty_tier": ticket.customer_tier.value}
        order_context["ticket_id"] = ticket.ticket_id
        result = run_resolution_pipeline(ticket.ticket_text, order_context)
        classification = result.get("classification", {})
        return FinalResolution(
            ticket_id=ticket.ticket_id,
            issue_type=classification.get("issue_type", "other"),
            priority=classification.get("priority", "medium"),
            customer_response=result.get("customer_response", ""),
            internal_notes=result.get("internal_notes", ""),
            actions_to_take=result.get("next_steps", []),
            citations=result.get("citations", []),
            compliance_status="approved",
            requires_escalation=result.get("requires_escalation", False),
            escalation_reason=result.get("rationale", ""),
            rewrite_count=0
        )
