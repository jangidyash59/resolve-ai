"""
Simplified orchestrator using Groq SDK directly (no CrewAI)
"""
import json
import os
import re
from pathlib import Path

import faiss
import numpy as np
from dotenv import load_dotenv
from groq import Groq

from src.models import FinalResolution, TicketInput

load_dotenv()

groq_client = None
MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

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
    Use Hugging Face Router API for embeddings (zero local RAM usage).
    Uses new router.huggingface.co endpoint to avoid Render DNS issues.
    """
    hf_token = os.getenv("HF_TOKEN")
    
    if hf_token:
        # NEW: Use HF Router API (fixes Render DNS timeout)
        import requests
        api_url = "https://router.huggingface.co/hf-inference/models/sentence-transformers/all-MiniLM-L6-v2"
        headers = {"Authorization": f"Bearer {hf_token}"}
        
        embeddings = []
        for text in texts:
            try:
                response = requests.post(
                    api_url,
                    headers=headers,
                    json={"inputs": [text], "options": {"wait_for_model": True}},
                    timeout=30
                )
                
                if response.status_code == 200:
                    embeddings.append(response.json()[0])
                else:
                    print(f"HF API error: {response.status_code}, falling back to local")
                    # Fallback to local model
                    from sentence_transformers import SentenceTransformer
                    model = SentenceTransformer(EMBEDDING_MODEL)
                    return [embedding.tolist() for embedding in model.encode(texts, convert_to_numpy=True)]
            except Exception as e:
                print(f"HF API exception: {e}, falling back to local")
                from sentence_transformers import SentenceTransformer
                model = SentenceTransformer(EMBEDDING_MODEL)
                return [embedding.tolist() for embedding in model.encode(texts, convert_to_numpy=True)]
        
        return embeddings
    else:
        # Fallback: local sentence-transformers (requires RAM)
        print("HF_TOKEN not set, using local sentence-transformers model")
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(EMBEDDING_MODEL)
        embeddings = model.encode(texts, convert_to_numpy=True)
        return [embedding.tolist() for embedding in embeddings]

def build_policy_index():
    """
    Load pre-built FAISS index from repository.
    Index building happens only locally with `python build_index.py`.
    """
    global faiss_index, indexed_policies
    
    if not FAISS_INDEX_PATH.exists() or not FAISS_METADATA_PATH.exists():
        raise FileNotFoundError(
            f"Pre-built FAISS index not found at {FAISS_INDEX_PATH}. "
            "Run 'python build_index.py' locally first."
        )
    
    print("Loading pre-built FAISS index...")
    faiss_index = faiss.read_index(str(FAISS_INDEX_PATH))
    with open(FAISS_METADATA_PATH, "r") as f:
        saved_metadata = json.load(f)
    indexed_policies = saved_metadata.get("policies", [])
    print(f"✓ Loaded {len(indexed_policies)} policy vectors from pre-built index.")

def search_policies(query, number_of_results=3):
    """
    Semantic search using pre-built FAISS index and HF Router API for query embeddings.
    """
    try:
        query_embedding = create_embeddings([query])[0]
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
        print(f"Search error: {e}, using keyword fallback")
        # Fallback to keyword search if embeddings fail
        return keyword_search_policies(query, number_of_results)

def keyword_search_policies(query, number_of_results=3):
    """
    Keyword-based policy search fallback.
    """
    if not indexed_policies:
        return []
    
    query_lower = query.lower()
    query_words = set(query_lower.split())
    
    scored_policies = []
    for policy in indexed_policies:
        policy_text_lower = policy["text"].lower()
        policy_words = set(policy_text_lower.split())
        
        word_matches = len(query_words.intersection(policy_words))
        substring_match = 5 if query_lower in policy_text_lower else 0
        score = word_matches + substring_match
        
        if score > 0:
            scored_policies.append({
                "score": score,
                "citation": f"{policy['source']} — {policy['section']}",
                "text": policy["text"],
                "similarity": round(min(score / 10.0, 0.95), 3)
            })
    
    scored_policies.sort(key=lambda x: x["score"], reverse=True)
    return scored_policies[:number_of_results] if scored_policies else [
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
