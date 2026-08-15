import json
import os
from pathlib import Path
from typing import Literal

import faiss
import numpy as np
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel, Field

from src.models import FinalResolution, TicketInput

load_dotenv()

openai_client: Groq | None = None

# Groq API Configuration - COMPLETELY FREE, FAST INFERENCE
MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # Free local embeddings via HuggingFace

PROJECT_DIRECTORY = Path(__file__).resolve().parent.parent
POLICIES_DIRECTORY = PROJECT_DIRECTORY / "data" / "policies"

configured_faiss_directory = Path(
    os.getenv("VECTOR_STORE_PATH", "faiss_store")
)
FAISS_DIRECTORY = (
    configured_faiss_directory
    if configured_faiss_directory.is_absolute()
    else PROJECT_DIRECTORY / configured_faiss_directory
)
FAISS_INDEX_PATH = FAISS_DIRECTORY / "policies.index"
FAISS_METADATA_PATH = FAISS_DIRECTORY / "policies.json"

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
RETRIEVER_K = int(os.getenv("RETRIEVER_K", "3"))
MINIMUM_POLICY_SIMILARITY = float(
    os.getenv("MINIMUM_POLICY_SIMILARITY", "0.25")
)
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"


# Initially empty
faiss_index = None
indexed_policies = []


def get_openai_client():
    """Create the Groq client - FREE and FAST inference."""

    global openai_client

    if openai_client is not None:
        return openai_client

    groq_api_key = os.getenv("GROQ_API_KEY")
    
    if not groq_api_key:
        raise ValueError(
            "GROQ_API_KEY not found. Get a FREE API key at https://console.groq.com"
        )

    # Use Groq SDK directly - 100% FREE, Fast Inference
    from groq import Groq
    openai_client = Groq(api_key=groq_api_key)
    
    return openai_client


def debug_print(message: str) -> None:
    """Print internal pipeline details only when DEBUG_MODE=true."""

    if DEBUG_MODE:
        print(message)


# =========================
# STRUCTURED AGENT OUTPUTS
# =========================

class TriageResult(BaseModel):
    """Structured output produced by the Triage Agent."""

    issue_type: str
    confidence: float = Field(ge=0, le=1)
    priority: Literal["low", "medium", "high", "urgent"]
    missing_fields: list[str] = Field(default_factory=list)
    clarifying_questions: list[str] = Field(default_factory=list)
    summary: str
    requires_escalation: bool = False
    escalation_reason: str = ""


class ResolutionResult(BaseModel):
    """Structured output produced by the Resolution Writer Agent."""

    decision: Literal["approve", "deny", "partial", "needs_escalation"]
    rationale: str
    customer_response: str
    next_steps: list[str] = Field(default_factory=list)
    internal_notes: str = ""
    citations: list[str] = Field(default_factory=list)


class ComplianceResult(BaseModel):
    """Structured output produced by the Compliance/Safety Agent."""

    recommendation: Literal["approve", "rewrite", "escalate"]
    issues_found: list[str] = Field(default_factory=list)
    unsupported_claims: list[str] = Field(default_factory=list)
    missing_citations: list[str] = Field(default_factory=list)
    sensitive_data_detected: bool = False
    rewrite_instructions: str = ""


# =========================
# 1. SPLIT TEXT
# =========================

def split_text(text: str) -> list[str]:
    """Divide one long section into smaller overlapping chunks."""

    chunks = []
    start = 0

    while start < len(text):

        end = min(
            start + CHUNK_SIZE,
            len(text)
        )

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == len(text):
            break

        # Move forward while retaining some previous text.
        start = end - CHUNK_OVERLAP

    return chunks


# =========================
# 2. LOAD AND CHUNK POLICIES
# =========================

def load_and_chunk_policy_documents() -> list[dict]:
    """Read Markdown policies and return structured policy chunks."""

    policy_files = sorted(
        POLICIES_DIRECTORY.glob("*.md")
    )
    if not policy_files:
        raise FileNotFoundError(
            f"No Markdown files found inside: "
            f"{POLICIES_DIRECTORY}"
        )
    all_policy_chunks = []

    for policy_file in policy_files:

        print(f"Reading: {policy_file.name}")

        document_text = policy_file.read_text(
            encoding="utf-8"
        )
        sections = []
        current_heading = "General"
        current_lines = []

        # Separate the document using Markdown headings.
        for line in document_text.splitlines():

            if line.startswith("#"):

                if current_lines:
                    sections.append(
                        (
                            current_heading,
                            "\n".join(current_lines)
                        )
                    )

                current_heading = line.lstrip("#").strip()
                current_lines = [line]

            else:
                current_lines.append(line)

        # Save the final section.
        if current_lines:
            sections.append(
                (
                    current_heading,
                    "\n".join(current_lines)
                )
            )

        # Split every section into smaller chunks.
        for section_number, (heading, section_text) in enumerate(sections):

            chunks = split_text(section_text)

            for chunk_number, chunk_text in enumerate(chunks):

                policy_record = {
                    "id": (
                        f"{policy_file.stem}"
                        f"-section-{section_number}"
                        f"-chunk-{chunk_number}"
                    ),
                    "source": policy_file.name,
                    "section": heading,
                    "text": chunk_text
                }

                all_policy_chunks.append(policy_record)

    print(
        f"\nCreated {len(all_policy_chunks)} policy chunks."
    )

    return all_policy_chunks


# =========================
# 3. CREATE EMBEDDINGS
# =========================

def create_embeddings(
    texts: list[str]
) -> list[list[float]]:
    """Convert a list of texts into embedding vectors using FREE HuggingFace."""

    from sentence_transformers import SentenceTransformer
    
    # Load the free embedding model (runs locally, no API cost)
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    
    # Generate embeddings (completely free)
    embeddings = model.encode(texts, convert_to_numpy=True)
    
    # Return as list of lists
    return [embedding.tolist() for embedding in embeddings]


# =========================
# 4. BUILD POLICY INDEX
# =========================

def build_policy_index() -> None:
    """Create a new FAISS index or load the existing index."""

    global faiss_index, indexed_policies

    # Create faiss_store if it does not already exist.
    FAISS_DIRECTORY.mkdir(parents=True, exist_ok=True)

    # Read original policy documents.
    current_policies = load_and_chunk_policy_documents()

    # Check whether saved FAISS files already exist.
    if (
        FAISS_INDEX_PATH.exists()
        and FAISS_METADATA_PATH.exists()
    ):
        with open(
            FAISS_METADATA_PATH,
            "r",
            encoding="utf-8"
        ) as file:
            saved_metadata = json.load(file)

        saved_policies = (
            saved_metadata.get("policies", [])
            if isinstance(saved_metadata, dict)
            else []
        )
        saved_embedding_model = (
            saved_metadata.get("embedding_model")
            if isinstance(saved_metadata, dict)
            else None
        )
        # Reuse the index if policy documents have not changed.
        if (
            saved_policies == current_policies
            and saved_embedding_model == EMBEDDING_MODEL
        ):

            faiss_index = faiss.read_index(
                str(FAISS_INDEX_PATH)
            )

            # Load the readable records corresponding to the vectors.
            indexed_policies = saved_policies

            print(
                f"\nLoaded {faiss_index.ntotal} "
                f"existing FAISS vectors."
            )

            return

    # Extract only the text from every policy record.
    texts = [
        policy["text"]
        for policy in current_policies
    ]

    print("\nCreating embeddings...")

    embeddings = create_embeddings(texts)

    # Convert embeddings to the format required by FAISS.
    embedding_matrix = np.array(
        embeddings,
        dtype="float32"
    )

    # Normalize vectors for cosine-similarity searching.
    faiss.normalize_L2(embedding_matrix)

    # Find the size of one embedding vector.
    vector_dimension = embedding_matrix.shape[1]

    # Create the FAISS database.
    faiss_index = faiss.IndexFlatIP(
        vector_dimension
    )

    # Add policy vectors to FAISS.
    faiss_index.add(embedding_matrix)

    # Store the corresponding readable policies.
    indexed_policies = current_policies

    # Save the vector database.
    faiss.write_index(
        faiss_index,
        str(FAISS_INDEX_PATH)
    )

    # Save readable policy metadata.
    with open(
        FAISS_METADATA_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            {
                "embedding_model": EMBEDDING_MODEL,
                "policies": indexed_policies
            },
            file,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"\nFAISS knowledge base created with "
        f"{faiss_index.ntotal} vectors."
    )


# =========================
# 5. SEARCH POLICIES TOOL
# =========================

def search_policies(
    query: str,
    number_of_results: int = RETRIEVER_K
) -> list[dict]:
    """Search FAISS and return the most relevant readable policies."""

    if faiss_index is None:
        raise RuntimeError(
            "The FAISS index is not ready. Run build_policy_index() first."
        )

    # Convert the user's search query into one embedding vector.
    query_embedding = create_embeddings([query])

    query_matrix = np.array(
        query_embedding,
        dtype="float32"
    )

    # The stored policy vectors were normalized, so normalize the query too.
    faiss.normalize_L2(query_matrix)

    result_count = min(
        number_of_results,
        faiss_index.ntotal
    )

    similarities, positions = faiss_index.search(
        query_matrix,
        result_count
    )

    results = []

    for similarity, position in zip(
        similarities[0],
        positions[0]
    ):
        if position == -1:
            continue

        policy = indexed_policies[position]

        results.append(
            {
                "id": policy["id"],
                "text": policy["text"],
                "source": policy["source"],
                "section": policy["section"],
                "citation": (
                    f"{policy['source']} — {policy['section']}"
                ),
                "similarity": float(similarity)
            }
        )

    return results


# Description of the Python function given to the AI model.
SEARCH_POLICIES_TOOL = {
    "type": "function",
    "name": "search_policies",
    "description": (
        "Search company policy documents and return the most relevant "
        "policy sections. Use this before answering a policy question."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "A clear policy search query."
            }
        },
        "required": ["query"],
        "additionalProperties": False
    },
    "strict": True
}


# =========================
# 6. TRIAGE AGENT
# =========================

def run_triage_agent(
    ticket_text: str,
    order_context: dict
) -> TriageResult:
    """Classify the ticket and identify missing information."""

    response = get_openai_client().responses.parse(
        model=MODEL,
        instructions=(
            "You are the Triage Agent for an e-commerce support system. "
            "Classify the issue as refund, return, shipping, payment, promo, "
            "fraud, warranty, cancellation, marketplace, account, or other. "
            "Identify only missing fields that are essential for deciding the case. "
            "Ask at most three short clarifying questions. "
            "Photo and video attachments are optional during initial intake. "
            "Do not add missing photos, videos, recordings, or attachment details "
            "to missing_fields or clarifying_questions. They may be requested later "
            "as evidence when an applicable policy explicitly requires them. "
            "Escalate legal threats, fraud, safety issues, or serious policy conflicts. "
            "Never invent missing order information."
        ),
        input=json.dumps(
            {
                "ticket_text": ticket_text,
                "order_context": order_context
            },
            ensure_ascii=False
        ),
        text_format=TriageResult
    )
    if response.output_parsed is None:
        raise RuntimeError("The Triage Agent returned no structured output.")

    return response.output_parsed


# =========================
# 7. POLICY RETRIEVER AGENT
# =========================

def run_policy_retriever_agent(
    ticket_text: str,
    order_context: dict,
    triage: TriageResult
) -> list[dict]:
    """Ask the LLM to form a search query, then execute the FAISS tool."""

    response = get_openai_client().responses.create(
        model=MODEL,
        instructions=(
            "You are the Policy Retriever Agent. Call search_policies once "
            "with a precise query containing the issue type, relevant item category, "
            "region, fulfillment type, and customer request when available."
        ),
        input=json.dumps(
            {
                "ticket_text": ticket_text,
                "order_context": order_context,
                "triage": triage.model_dump()
            },
            ensure_ascii=False
        ),
        tools=[SEARCH_POLICIES_TOOL],
        tool_choice="required"
    )

    retrieved_policies = []
    seen_ids = set()

    for item in response.output:
        if item.type != "function_call":
            continue

        if item.name != "search_policies":
            continue

        arguments = json.loads(item.arguments)

        debug_print(
            f"Retriever called search_policies with: "
            f"{arguments['query']}"
        )

        results = search_policies(arguments["query"])

        for result in results:
            if result["similarity"] < MINIMUM_POLICY_SIMILARITY:
                continue

            if result["id"] in seen_ids:
                continue

            seen_ids.add(result["id"])
            retrieved_policies.append(result)

    return retrieved_policies


# =========================
# 8. RESOLUTION WRITER AGENT
# =========================

def run_resolution_agent(
    ticket_text: str,
    order_context: dict,
    triage: TriageResult,
    policies: list[dict],
    rewrite_instructions: str = ""
) -> ResolutionResult:
    """Draft a customer response using only retrieved policy evidence."""

    response = get_openai_client().responses.parse(
        model=MODEL,
        instructions=(
            "You are the Resolution Writer Agent. Produce a warm, professional "
            "customer-support resolution using only the supplied policy excerpts. "
            "Every policy claim must use an exact citation string supplied in the "
            "policy evidence. Never invent eligibility rules, exceptions, amounts, "
            "or timelines. Missing photo or video attachments at initial intake must "
            "not by itself cause escalation. If a retrieved policy requires photos "
            "or other evidence, make the decision conditional on verification and "
            "request that evidence in next_steps or customer_response. Do not request "
            "a video or promise that a video will be accepted unless the retrieved "
            "policy explicitly supports it. If other essential policy evidence is "
            "missing or conflicting, choose "
            "needs_escalation. If triage requires escalation, preserve that decision. "
            "Keep internal information out of customer_response."
        ),
        input=json.dumps(
            {
                "ticket_text": ticket_text,
                "order_context": order_context,
                "triage": triage.model_dump(),
                "policy_evidence": policies,
                "rewrite_instructions": rewrite_instructions
            },
            ensure_ascii=False
        ),
        text_format=ResolutionResult
    )

    if response.output_parsed is None:
        raise RuntimeError("The Resolution Agent returned no structured output.")

    return response.output_parsed


# =========================
# 9. DETERMINISTIC CITATION CHECK
# =========================

def find_invalid_citations(
    resolution: ResolutionResult,
    policies: list[dict]
) -> list[str]:
    """Return citations that were not present in retrieved evidence."""

    allowed_citations = {
        policy["citation"]
        for policy in policies
    }

    return [
        citation
        for citation in resolution.citations
        if citation not in allowed_citations
    ]


# =========================
# 10. COMPLIANCE / SAFETY AGENT
# =========================

def run_compliance_agent(
    resolution: ResolutionResult,
    policies: list[dict]
) -> ComplianceResult:
    """Audit citations, unsupported claims, policy accuracy and sensitive data."""

    invalid_citations = find_invalid_citations(
        resolution,
        policies
    )

    if invalid_citations:
        return ComplianceResult(
            recommendation="rewrite",
            issues_found=["The response contains invalid citations."],
            unsupported_claims=[],
            missing_citations=invalid_citations,
            sensitive_data_detected=False,
            rewrite_instructions=(
                "Remove or replace these invalid citations using exact citation "
                f"strings from the evidence: {invalid_citations}"
            )
        )

    response = get_openai_client().responses.parse(
        model=MODEL,
        instructions=(
            "You are the Compliance and Safety Agent. Audit the draft against "
            "the supplied policy evidence. Check unsupported factual claims, "
            "missing or weak citations, incorrect policy conclusions, sensitive "
            "data leakage, and unsafe promises. Empathetic sentences do not need "
            "citations. Do not escalate solely because photos or videos were not "
            "provided during initial intake. A conditional request for policy-required "
            "evidence is acceptable. However, flag any claim that an unsupported "
            "attachment type, such as video, will definitely be accepted. "
            "Recommend approve, rewrite, or escalate."
        ),
        input=json.dumps(
            {
                "draft": resolution.model_dump(),
                "policy_ground_truth": policies
            },
            ensure_ascii=False
        ),
        text_format=ComplianceResult
    )

    if response.output_parsed is None:
        raise RuntimeError("The Compliance Agent returned no structured output.")

    return response.output_parsed


# =========================
# 11. ORCHESTRATOR
# =========================

def run_resolution_pipeline(
    ticket_text: str,
    order_context: dict
) -> dict:
    """Run Triage → Retrieval → Resolution → Compliance."""

    debug_print("\n[1/4] Running Triage Agent...")
    triage = run_triage_agent(ticket_text, order_context)

    # Stop and ask the customer for essential missing information.
    if triage.missing_fields:
        questions = triage.clarifying_questions[:3]

        if not questions:
            questions = [
                f"Please provide {field}."
                for field in triage.missing_fields[:3]
            ]

        numbered_questions = "\n".join(
            f"{number}. {question}"
            for number, question in enumerate(questions, start=1)
        )

        return {
            "status": "needs_clarification",
            "classification": {
                "issue_type": triage.issue_type,
                "confidence": triage.confidence,
                "priority": triage.priority
            },
            "missing_fields": triage.missing_fields,
            "clarifying_questions": questions,
            "citations": [],
            "customer_response": (
                "I need a few more details before I can resolve your request:\n"
                f"{numbered_questions}"
            )
        }

    debug_print("[2/4] Running Policy Retriever Agent...")
    policies = run_policy_retriever_agent(
        ticket_text,
        order_context,
        triage
    )

    if not policies:
        return {
            "status": "needs_escalation",
            "classification": {
                "issue_type": triage.issue_type,
                "confidence": triage.confidence,
                "priority": triage.priority
            },
            "decision": "needs_escalation",
            "rationale": (
                "No sufficiently relevant policy evidence was found."
            ),
            "citations": [],
            "customer_response": (
                "I don't have enough information in the provided policies to "
                "resolve this request, so I am escalating it for human review."
            ),
            "next_steps": ["Escalate the ticket to a human support specialist."]
        }

    debug_print("[3/4] Running Resolution Writer Agent...")
    resolution = run_resolution_agent(
        ticket_text,
        order_context,
        triage,
        policies
    )

    debug_print("[4/4] Running Compliance Agent...")
    compliance = run_compliance_agent(
        resolution,
        policies
    )

    rewrite_count = 0

    if compliance.recommendation == "rewrite":
        rewrite_count = 1

        resolution = run_resolution_agent(
            ticket_text,
            order_context,
            triage,
            policies,
            compliance.rewrite_instructions
        )

        compliance = run_compliance_agent(
            resolution,
            policies
        )

    # Never expose a draft that failed the compliance review.
    if compliance.recommendation != "approve":
        return {
            "status": "needs_escalation",
            "classification": {
                "issue_type": triage.issue_type,
                "confidence": triage.confidence,
                "priority": triage.priority
            },
            "decision": "needs_escalation",
            "rationale": "The generated resolution did not pass compliance.",
            "citations": resolution.citations,
            "customer_response": (
                "Thank you for providing the details. Your request requires "
                "additional review, so I have forwarded it to a support specialist. "
                "They will verify the applicable policy and contact you with the "
                "next steps."
            ),
            "next_steps": ["Send the ticket for human review."],
            "compliance": compliance.model_dump(),
            "rewrite_count": rewrite_count
        }

    if triage.requires_escalation or resolution.decision == "needs_escalation":
        return {
            "status": "needs_escalation",
            "classification": {
                "issue_type": triage.issue_type,
                "confidence": triage.confidence,
                "priority": triage.priority
            },
            "decision": "needs_escalation",
            "rationale": (
                triage.escalation_reason
                or resolution.rationale
            ),
            "citations": resolution.citations,
            "customer_response": resolution.customer_response,
            "next_steps": resolution.next_steps,
            "compliance": compliance.model_dump(),
            "rewrite_count": rewrite_count
        }

    return {
        "status": "approved",
        "classification": {
            "issue_type": triage.issue_type,
            "confidence": triage.confidence,
            "priority": triage.priority
        },
        "clarifying_questions": triage.clarifying_questions[:3],
        "decision": resolution.decision,
        "rationale": resolution.rationale,
        "citations": resolution.citations,
        "customer_response": resolution.customer_response,
        "next_steps": resolution.next_steps,
        "internal_notes": resolution.internal_notes,
        "retrieved_policies": policies,
        "compliance": compliance.model_dump(),
        "rewrite_count": rewrite_count
    }


# =========================
# 12. STREAMLIT UI ADAPTER
# =========================

class SupportOrchestrator:
    """Expose the exact interface used by the existing Streamlit application."""

    def __init__(
        self,
        google_api_key: str | None = None,
        groq_api_key: str | None = None,
        model: str | None = None,
        vector_store=None
    ) -> None:
        # Keep the old parameters so existing app.py imports do not break.
        # The OpenAI implementation uses OPENAI_API_KEY and OPENAI_MODEL.
        del google_api_key, groq_api_key, model, vector_store

        get_openai_client()
        build_policy_index()

    def resolve_ticket(self, ticket: TicketInput) -> FinalResolution:
        """Convert the UI input model into a UI-compatible final result."""

        order_context = (
            ticket.order_context.model_dump(mode="json")
            if ticket.order_context is not None
            else {}
        )

        # Name and tier help personalization. Email is excluded as unnecessary PII.
        order_context["customer"] = {
            "name": ticket.customer_name,
            "loyalty_tier": ticket.customer_tier.value
        }
        order_context["ticket_id"] = ticket.ticket_id

        result = run_resolution_pipeline(
            ticket.ticket_text,
            order_context
        )

        classification = result.get("classification", {})
        status = result.get("status", "needs_escalation")
        needs_clarification = status == "needs_clarification"
        requires_escalation = status == "needs_escalation"

        if needs_clarification:
            actions = result.get("clarifying_questions", [])
            internal_notes = (
                "Waiting for required information: "
                + ", ".join(result.get("missing_fields", []))
            )
            compliance_status = "needs_clarification"
            escalation_reason = ""
        elif requires_escalation:
            actions = result.get(
                "next_steps",
                ["Escalate the ticket to a human support specialist."]
            )
            internal_notes = result.get(
                "internal_notes",
                result.get("rationale", "Human review is required.")
            )
            compliance_status = "escalated"
            escalation_reason = result.get(
                "rationale",
                "Human review is required."
            )
        else:
            actions = result.get("next_steps", [])
            internal_notes = result.get("internal_notes", "")
            compliance_status = "approved"
            escalation_reason = ""

        return FinalResolution(
            ticket_id=ticket.ticket_id,
            issue_type=classification.get("issue_type", "other"),
            priority=classification.get("priority", "medium"),
            customer_response=result.get(
                "customer_response",
                "Your request is being reviewed by our support team."
            ),
            internal_notes=internal_notes,
            actions_to_take=actions,
            citations=result.get("citations", []),
            compliance_status=compliance_status,
            requires_escalation=requires_escalation,
            escalation_reason=escalation_reason,
            rewrite_count=result.get("rewrite_count", 0)
        )


# =========================
# 13. CUSTOMER-FACING OUTPUT
# =========================

def create_customer_output(result: dict) -> dict:
    """Return only information that is safe to display in the customer app."""

    internal_status = result.get("status", "")

    status_labels = {
        "approved": "resolved",
        "needs_clarification": "more_information_needed",
        "needs_escalation": "under_review"
    }

    return {
        "status": status_labels.get(
            internal_status,
            "under_review"
        ),
        "message": result.get(
            "customer_response",
            "Your request is being reviewed by our support team."
        ),
        "sources": (
            result.get("citations", [])
            if internal_status == "approved"
            else []
        )
    }


# =========================
# 14. MAIN
# =========================

def main() -> None:

    print("Starting ResolveAI...\n")

    build_policy_index()

    print("\nPolicy index is ready.")
    print("Enter a customer ticket, or type 'exit' to stop.\n")

    while True:
        ticket_text = input("Customer ticket: ").strip()

        if ticket_text.lower() == "exit":
            print("ResolveAI stopped.")
            break

        if not ticket_text:
            print("Please enter a customer ticket.\n")
            continue

        order_context_text = input(
            "Order context as JSON (press Enter if unavailable): "
        ).strip()

        try:
            order_context = (
                json.loads(order_context_text)
                if order_context_text
                else {}
            )

            result = run_resolution_pipeline(
                ticket_text,
                order_context
            )

            customer_output = create_customer_output(result)

            print("\nResolveAI:\n")
            print(customer_output["message"])

            if customer_output["sources"]:
                print("\nSources:")
                for source in customer_output["sources"]:
                    print(f"- {source}")

            print()

            # Developers can inspect the full pipeline result when needed.
            if DEBUG_MODE:
                print("Internal result:")
                print(
                    json.dumps(
                        result,
                        indent=2,
                        ensure_ascii=False
                    )
                )
                print()

        except json.JSONDecodeError:
            print("\nOrder context must be valid JSON.\n")

        except Exception as error:
            print(f"\nError: {error}\n")


# Program execution starts here.
if __name__ == "__main__":
    main()
