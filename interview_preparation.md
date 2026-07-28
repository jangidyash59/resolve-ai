# 🎯 Interview Preparation — AI Engineer Intern @ Purple Merit

> **Interview Date:** Friday, 10 April 2026, 6:30 PM IST  
> **Platform:** Google Meet  
> **Project:** ResolveAI — 4-Agent RAG Pipeline for E-commerce Support

---

## Table of Contents

1. [Project Overview — What You Built](#1-project-overview)
2. [RAG (Retrieval-Augmented Generation) — Deep Theory](#2-rag-deep-theory)
3. [Word Embeddings — Theory & Implementation](#3-word-embeddings)
4. [Vector Databases — FAISS Deep Dive](#4-vector-databases--faiss)
5. [Large Language Models (LLMs) — Gemini](#5-large-language-models)
6. [Multi-Agent Systems — Theory & CrewAI](#6-multi-agent-systems)
7. [LangChain — Framework Theory](#7-langchain-framework)
8. [Prompt Engineering — Techniques Used](#8-prompt-engineering)
9. [Data Preprocessing & Chunking](#9-data-preprocessing--chunking)
10. [Pydantic — Data Validation](#10-pydantic-data-validation)
11. [Evaluation & Metrics](#11-evaluation--metrics)
12. [Model Fundamentals — ML Basics](#12-model-fundamentals)
13. [Deployment — Streamlit Cloud](#13-deployment)
14. [Debugging & Problem Solving](#14-debugging--problem-solving)
15. [Potential Interview Questions with Answers](#15-potential-interview-questions)

---

## 1. Project Overview

### What is ResolveAI?

ResolveAI is a **production-grade, multi-agent AI system** that automatically resolves e-commerce customer support tickets. It uses a **4-agent sequential pipeline** built on **CrewAI**, powered by **Google Gemini 2.5 Flash**, with a **RAG (Retrieval-Augmented Generation)** architecture grounded in a **FAISS vector store** of 13 policy documents (~25,000 words).

### The 4-Agent Pipeline

```
Customer Ticket → [Triage Agent] → [Policy Researcher] → [Resolution Architect] → [Compliance Guard] → Final Response
```

| Agent | Role | Key Output |
|---|---|---|
| **Triage Agent** | Classifies issue type, sets priority (low → urgent), detects mandatory escalation triggers (legal, fraud, safety) | `issue_type`, `priority`, `requires_escalation` |
| **Policy Researcher** | Runs semantic search over FAISS vector store, retrieves top-K relevant policy chunks with citations | `policy_excerpts`, `citations` |
| **Resolution Architect** | Drafts empathetic, tier-aware customer response with inline policy citations | `customer_response`, `actions_to_take` |
| **Compliance Guard** | Audits for hallucinations, verifies every citation, checks PII, decides: approve / rewrite / escalate | `compliance_status` |

### Why This Architecture?

- **Separation of concerns**: Each agent has a focused, testable responsibility.
- **Compliance loop**: Writer ↔ Auditor feedback cycle (max 1 rewrite) catches hallucinations before they reach customers.
- **Grounded responses**: Every factual claim MUST be backed by a retrieved policy citation — zero hallucination design.
- **Graceful escalation**: Fraud, legal threats, and safety issues bypass the full pipeline and immediately escalate.

### Key Results

| Metric | Score |
|---|---|
| Citation Coverage Rate | **100%** |
| Compliance Pass Rate | **100%** |
| Error Rate | **0%** |
| Avg Processing Time | ~30–50s per ticket |

---

## 2. RAG Deep Theory

### What is RAG?

**Retrieval-Augmented Generation (RAG)** is a technique that enhances LLM responses by first **retrieving relevant information** from an external knowledge base and then **feeding that information as context** to the LLM during generation.

### Why RAG? (The Problem It Solves)

LLMs have several fundamental limitations:
1. **Knowledge cutoff**: Trained on data up to a certain date — they don't know about recent policies or updates.
2. **Hallucination**: LLMs generate plausible-sounding but factually incorrect information.
3. **No domain grounding**: A general-purpose model doesn't know your company's specific return policy or warranty terms.

RAG solves all three by **grounding** the LLM in retrieved, verifiable source documents.

### RAG Architecture (As Implemented in ResolveAI)

```
┌─────────────────────────────────────────────────────────────────────┐
│                        RAG PIPELINE                                 │
│                                                                     │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────────────┐│
│  │ User Query   │────▶│ Embedding    │────▶│ Vector Similarity    ││
│  │ (Ticket)     │     │ Model        │     │ Search (FAISS)       ││
│  └──────────────┘     └──────────────┘     └────────┬─────────────┘│
│                                                      │              │
│                                              Top-K Documents        │
│                                                      │              │
│  ┌──────────────────────────────────────────────────▼──────────────┐│
│  │                    LLM (Gemini 2.5)                             ││
│  │  System Prompt + Retrieved Context + User Query → Response      ││
│  └─────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────┘
```

### The Two Phases of RAG

#### Phase 1: Indexing (Offline — `build_index.py`)
1. **Load** policy markdown documents from `data/policies/`
2. **Chunk** documents using `RecursiveCharacterTextSplitter` (800 chars, 200 overlap)
3. **Embed** each chunk using `all-MiniLM-L6-v2` (384-dimensional vectors)
4. **Store** vectors in FAISS index → saved to `data/vectorstore_hf/`

#### Phase 2: Retrieval + Generation (Online — at query time)
1. **Embed** the user's query using the same embedding model
2. **Search** the FAISS index for top-K most similar chunks
3. **Inject** retrieved chunks into the LLM's prompt as context
4. **Generate** a response grounded in the retrieved evidence
5. **Verify** (Compliance Guard) that the response is faithful to sources

### How ResolveAI Implements RAG Differently

Most RAG systems are simple retrieve-and-generate. ResolveAI uses a **multi-agent RAG** where:
- The **Triage Agent** first understands the query to generate better search terms
- The **Retriever Agent** uses the triage summary (not the raw ticket) for more focused search
- The **Resolution Agent** generates using the retrieved context
- The **Compliance Guard** verifies faithfulness — a **post-generation grounding check**

This is sometimes called **"Agent-Augmented RAG"** or **"Agentic RAG"**.

### Key RAG Concepts to Know

| Concept | Definition | In ResolveAI |
|---|---|---|
| **Indexing** | Pre-processing documents into searchable vectors | `build_index.py` → FAISS |
| **Retrieval** | Finding relevant docs via similarity search | `PolicyVectorStore.search()` with K=3 |
| **Generation** | LLM produces output using retrieved context | Resolution Agent with Gemini |
| **Grounding** | Ensuring output is faithful to sources | Compliance Guard verification |
| **Chunking** | Splitting docs into smaller pieces for embedding | 800 chars, 200 overlap |
| **Top-K** | Number of retrieved documents | K=3 per query |
| **Context Window** | Max tokens the LLM can process | Gemini: ~1M tokens, we use ~2048 |

---

## 3. Word Embeddings

### What are Word Embeddings?

Word embeddings are **dense vector representations** of text in a continuous vector space where semantically similar texts are mapped to nearby points.

### How Embeddings Work (Intuition)

```
"return policy"       → [0.23, -0.45, 0.78, ..., 0.12]   (384 dimensions)
"refund guidelines"   → [0.21, -0.42, 0.81, ..., 0.10]   (similar vector!)
"shipping cost"       → [-0.67, 0.33, -0.12, ..., 0.89]  (very different vector)
```

**Key insight**: The closer two vectors are in this space (measured by cosine similarity or L2 distance), the more semantically related the texts are.

### Types of Embeddings (Evolution)

| Generation | Method | Key Idea |
|---|---|---|
| **1st Gen** | Word2Vec (2013), GloVe (2014) | Static word vectors from co-occurrence patterns |
| **2nd Gen** | ELMo (2018) | Contextual embeddings (same word, different meanings) |
| **3rd Gen** | BERT (2019), Sentence-BERT | Transformer-based, bidirectional context |
| **Current** | all-MiniLM-L6-v2, E5, BGE | Optimized for semantic similarity & retrieval |

### The Embedding Model We Use: `all-MiniLM-L6-v2`

| Property | Value |
|---|---|
| **Architecture** | 6-layer MiniLM (distilled from larger model) |
| **Dimensions** | 384 |
| **Training** | Trained on 1B+ sentence pairs for semantic similarity |
| **Speed** | Very fast — runs locally on CPU |
| **Cost** | **Free** — no API calls needed |
| **Max Sequence** | 256 tokens |

### Why We Chose This Model

1. **Local execution**: Runs entirely on-device, no API costs for embeddings
2. **High quality**: Top-tier performance on semantic similarity benchmarks
3. **Fast**: Small model (22M parameters) — ideal for real-time retrieval
4. **Zero cost**: Critical for a project with a free-tier Gemini API key

### How Embedding Search Works (Mathematically)

1. **Query embedding**: `q = embed("customer wants refund for damaged item")`
2. **Document embeddings**: Already stored in FAISS as `d_1, d_2, ..., d_n`
3. **Similarity**: Compute `sim(q, d_i)` for all documents
4. **Ranking**: Return top-K documents with highest similarity

**Cosine Similarity Formula:**
```
cos(q, d) = (q · d) / (||q|| × ||d||)
```
- Value range: [-1, 1]
- 1.0 = identical meaning
- 0.0 = unrelated
- We convert FAISS L2 distance to similarity: `similarity = 1 - distance`

### Sentence Embeddings vs. Word Embeddings

ResolveAI uses **sentence embeddings** (via Sentence-BERT), not individual word embeddings:
- **Word embedding**: `"refund"` → one vector
- **Sentence embedding**: `"I want a refund for my damaged laptop"` → one vector *for the whole sentence*

This is critical because we need to match **meaning of queries** against **meaning of policy chunks**, not individual words.

---

## 4. Vector Databases & FAISS

### What is a Vector Database?

A specialized database optimized for storing, indexing, and querying high-dimensional vectors (embeddings). Unlike traditional databases that use exact match or keyword search, vector databases use **approximate nearest neighbor (ANN)** algorithms.

### FAISS (Facebook AI Similarity Search)

FAISS is an open-source library by Meta for efficient similarity search of dense vectors.

| Property | Value |
|---|---|
| **Developer** | Meta (Facebook AI Research) |
| **Type** | In-memory vector index |
| **Search** | Approximate Nearest Neighbor (ANN) |
| **Distance Metric** | L2 (Euclidean) distance (default) |
| **Scale** | Can handle billions of vectors |
| **Overhead** | Zero — runs in-process, no separate server |

### Why FAISS Over Other Options?

| Option | Pros | Cons | Our Decision |
|---|---|---|---|
| **FAISS** | Zero overhead, in-memory, fast, free | No persistence server, not distributed | ✅ Perfect for ~200 chunks |
| **Pinecone** | Managed, scalable, cloud-native | Paid, API dependency, latency | ❌ Overkill for our scale |
| **Chroma** | Lightweight, good for dev | Less mature, slower at scale | ❌ Less battle-tested |
| **Weaviate** | Full-featured, hybrid search | Complex setup, heavier | ❌ Too heavy for our use case |

### How FAISS Works Internally

1. **Flat Index (IndexFlatL2)**: Brute-force search — compares query against ALL vectors. Exact results but O(n).
2. **IVF (Inverted File Index)**: Clusters vectors, only searches nearby clusters. Faster but approximate.
3. **PQ (Product Quantization)**: Compresses vectors for memory efficiency.

**ResolveAI uses `IndexFlatL2`** because our dataset is small (~200 chunks), so brute-force is fast enough and gives exact results.

### Our FAISS Implementation

```python
# From src/vectorstore/store.py

class PolicyVectorStore:
    def __init__(self, embedding_model="sentence-transformers/all-MiniLM-L6-v2"):
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
        self.vectorstore = None  # FAISS index

    def build_index(self, chunks: list[Document]) -> FAISS:
        # Embeds all chunks and builds the FAISS index
        self.vectorstore = FAISS.from_documents(chunks, self.embeddings)

    def search(self, query: str, k: int = 5) -> list[Document]:
        # Embeds query, searches FAISS, returns top-K
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        # Convert L2 distance to similarity score
        for doc, score in results:
            doc.metadata["relevance_score"] = round(1 - score, 4)
        return documents
```

### Key Concepts

| Concept | Explanation |
|---|---|
| **Similarity Search** | Finding vectors closest to a query vector |
| **L2 Distance** | Euclidean distance — lower = more similar |
| **Cosine Similarity** | Angle between vectors — higher = more similar |
| **Top-K** | Return the K most similar results |
| **Index Persistence** | Save/load index to/from disk (`save_local` / `load_local`) |
| **Deduplication** | Removing duplicate results when using multiple queries |

---

## 5. Large Language Models (LLMs)

### What is an LLM?

A **Large Language Model** is a deep neural network trained on massive amounts of text data to understand and generate human language. They use the **Transformer architecture** (Vaswani et al., 2017).

### The Transformer Architecture (Simplified)

```
Input Tokens → [Embedding Layer] → [Self-Attention] × N layers → [Output Probabilities]
```

Key components:
1. **Tokenization**: Text → numerical tokens (subword units)
2. **Self-Attention**: Each token attends to all other tokens to understand context
3. **Feed-Forward Networks**: Process attention outputs
4. **Layer Stacking**: 6 to 100+ transformer layers deep

### Self-Attention (The Core Innovation)

For the sentence: *"The customer returned the item because **it** was damaged"*

Self-attention allows "it" to attend to "item" (not "customer"), understanding the reference.

**Formula:**
```
Attention(Q, K, V) = softmax(QK^T / √d_k) · V
```
- **Q** (Query): What am I looking for?
- **K** (Key): What do I contain?
- **V** (Value): What information do I provide?
- **√d_k**: Scaling factor for numerical stability

### Google Gemini 2.5 Flash (Our LLM)

| Property | Value |
|---|---|
| **Developer** | Google DeepMind |
| **Architecture** | Transformer (MoE — Mixture of Experts) |
| **Context Window** | ~1M tokens |
| **Speed** | Optimized for low-latency inference |
| **Cost** | Free tier with 15 RPM limit |
| **Strengths** | Fast, reliable, good at structured output |

### Why Gemini Over GPT-4 or Claude?

1. **Free tier**: 15 requests/minute — sufficient for sequential agents
2. **Speed**: Flash Lite is optimized for fast responses
3. **Structured output**: Handles our tagged output format (ISSUE_TYPE:, PRIORITY:, etc.) well
4. **Reliability**: Fewer hallucinations than open-source alternatives

### Key LLM Parameters We Configured

```python
self.llm = LLM(
    model="gemini/gemini-2.5-flash",
    api_key=primary_api_key,
    temperature=0.1,     # Low randomness — deterministic, factual
    max_tokens=2048,     # Enough for customer response + metadata
)
```

| Parameter | Value | Why |
|---|---|---|
| `temperature` | 0.1 | We want consistent, factual responses — not creative ones |
| `max_tokens` | 2048 | Sufficient for structured output without waste |
| `model` | gemini-2.5-flash | Best speed/cost balance for agentic use |

### Key LLM Concepts to Know

| Concept | Definition |
|---|---|
| **Temperature** | Controls randomness. 0 = deterministic, 1 = creative |
| **Top-P (Nucleus)** | Only considers tokens whose cumulative probability ≥ P |
| **Max Tokens** | Maximum length of generated output |
| **Context Window** | Maximum input + output token length |
| **Tokenization** | Breaking text into subword units (BPE, SentencePiece) |
| **Hallucination** | Model generates plausible but factually incorrect text |
| **Grounding** | Anchoring output to verifiable source material |
| **Fine-tuning** | Training a pre-trained model on domain-specific data |
| **In-context Learning** | Teaching via examples in the prompt (few-shot) |

---

## 6. Multi-Agent Systems

### What is a Multi-Agent System?

A system where **multiple AI agents** — each with a distinct role, goal, and set of capabilities — collaborate to solve a complex task that no single agent could handle well alone.

### Why Multiple Agents Instead of One?

| Single Agent | Multi-Agent (ResolveAI) |
|---|---|
| One prompt does everything | Each agent has a focused task |
| Hallucination risk is high | Compliance Guard catches hallucinations |
| Hard to debug | Each agent's output is separately inspectable |
| No feedback loop | Writer ↔ Auditor rewrite cycle |
| Prompt becomes enormous | Each prompt is small and focused |

### Agent Design Patterns

| Pattern | Description | Used in ResolveAI? |
|---|---|---|
| **Sequential** | Agents execute one after another, passing outputs forward | ✅ Primary pattern |
| **Hierarchical** | Manager agent delegates to worker agents | ❌ Not needed |
| **Collaborative** | Agents discuss and reach consensus | ❌ Not needed |
| **Feedback Loop** | Agent A checks Agent B's output, sends corrections | ✅ Compliance → Resolution rewrite |

### CrewAI — Our Agent Orchestration Framework

CrewAI is a production-grade framework for building multi-agent AI systems.

| Feature | Detail |
|---|---|
| **Agents** | Define roles, goals, backstories, tools, LLM |
| **Tasks** | Define what each agent must do, expected output format |
| **Crew** | Groups agents + tasks, defines execution strategy |
| **Process** | Sequential or hierarchical execution |
| **Tools** | Custom tools agents can invoke (e.g., `PolicySearchTool`) |
| **Memory** | Shared task context across sequential agents |

### Agent Configuration (Example: Triage Agent)

```python
Agent(
    role="Customer Support Triage Specialist",
    goal="Classify tickets by type and priority",
    backstory="You are a triage specialist...",
    llm=gemini_llm,
    verbose=True,             # Log agent reasoning
    allow_delegation=False,   # No delegating to other agents
    max_iter=3,               # Hard cap on reasoning iterations
    use_system_prompt=False,  # Gemini compatibility flag
)
```

### Key Design Decisions in Our Multi-Agent System

| Decision | Why |
|---|---|
| `allow_delegation=False` | Prevents agents from endlessly delegating to each other |
| `max_iter=3` | Hard cap prevents infinite loops in agent reasoning |
| `use_system_prompt=False` | Gemini 2.5 Flash works better with user prompts only |
| `MAX_REWRITES=1` | At most 1 compliance rewrite before escalation |
| 5-second inter-task delay | Avoids hitting Gemini's 15 RPM rate limit |

### The Compliance Loop (Feedback Mechanism)

```
Resolution Writer → draft response
       │
       ▼
Compliance Guard → audit response
       │
   ┌───┴───┐
   │       │
APPROVE   FAIL → send feedback → Resolution Writer → redraft
   │                                                      │
   ▼                                                      ▼
FINAL                                              Compliance Guard again
                                                          │
                                                   ┌──────┴──────┐
                                                APPROVE    ESCALATE (max retries)
```

---

## 7. LangChain Framework

### What is LangChain?

LangChain is a framework for building applications powered by LLMs. It provides modular, composable components for common LLM workflows.

### Components We Use from LangChain

| Component | Package | What It Does in ResolveAI |
|---|---|---|
| `HuggingFaceEmbeddings` | `langchain-community` | Wraps the all-MiniLM-L6-v2 model for embedding |
| `FAISS` (wrapper) | `langchain-community` | LangChain-compatible FAISS interface |
| `Document` | `langchain-core` | Standard document object with `page_content` + `metadata` |
| `RecursiveCharacterTextSplitter` | `langchain-text-splitters` | Chunks documents hierarchically |
| `ChatGoogleGenerativeAI` | `langchain-google-genai` | Wraps Gemini API for LangChain compatibility |

### Why LangChain?

1. **Standardization**: `Document` objects with metadata flow cleanly through the pipeline
2. **FAISS integration**: `FAISS.from_documents()` handles embedding + indexing in one call
3. **Text splitting**: `RecursiveCharacterTextSplitter` is the gold standard for chunking
4. **Ecosystem**: CrewAI builds on LangChain's abstractions

### LangChain Document Model

```python
Document(
    page_content="Full text content of the chunk...",
    metadata={
        "source": "returns_refunds.md",      # Which file
        "section": "Non-Returnable Items",    # Which section
        "citation": "returns_refunds.md — Non-Returnable Items",
        "chunk_index": 3,                      # Position in document
        "total_chunks": 12,                    # Total chunks from this doc
    }
)
```

---

## 8. Prompt Engineering

### What is Prompt Engineering?

The art and science of designing **effective instructions** for LLMs to produce desired outputs. It's the primary interface between the developer and the model.

### Techniques Used in ResolveAI

#### 1. Role Prompting
```python
role="Customer Support Triage Specialist"
backstory="You are a triage specialist. You quickly identify the core issue..."
```
**Why**: Gives the LLM a persona and behavioral constraints.

#### 2. Structured Output Format
```
Provide your response in this exact format:

ISSUE_TYPE: [type]
PRIORITY: [low/medium/high/urgent]
REQUIRES_ESCALATION: [true/false]
```
**Why**: Makes output parseable with regex — critical for pipeline data flow.

#### 3. Constraint Prompting
```
- ONLY use information from the retrieved policy excerpts
- Do NOT invent policies or make assumptions
- If a policy doesn't cover the situation, explicitly state it
```
**Why**: Prevents hallucination — the #1 risk in production AI systems.

#### 4. Chain-of-Thought (Implicit)
The task descriptions guide the agent through a logical sequence:
```
1. Classify type
2. Determine priority
3. Check for missing info
4. Summarize for downstream agents
```
**Why**: Breaking complex tasks into steps improves reasoning quality.

#### 5. Few-Shot Context (Via Retrieved Documents)
The Resolution Agent receives retrieved policy excerpts as "examples" of what to cite:
```
## Retrieved Policy Excerpts
[actual policy text provided as context]
```
**Why**: Grounds the model in real data — the "R" in RAG.

#### 6. Negative Prompting
```
- Never share internal-only information with the customer
- Do NOT flag empathetic sentences for missing citations
```
**Why**: Explicitly prevents common failure modes identified during development.

---

## 9. Data Preprocessing & Chunking

### Why Chunk Documents?

- Embedding models have **token limits** (256 tokens for MiniLM)
- Smaller chunks = **more focused** = better retrieval precision
- Whole documents would dilute the relevance signal

### Our Chunking Strategy

```python
RecursiveCharacterTextSplitter(
    chunk_size=800,        # Max 800 characters per chunk
    chunk_overlap=200,     # 200 char overlap between chunks
    separators=["\\n## ", "\\n### ", "\\n#### ", "\\n\\n", "\\n", ". ", " ", ""],
    keep_separator=True,
)
```

### How RecursiveCharacterTextSplitter Works

1. **Try `\n## `** first (section headers) — preserve document structure
2. If chunk is still too big, try **`\n### `** (subsection headers)
3. Then **`\n\n`** (paragraphs)
4. Then **`\n`** (lines)
5. Then **`. `** (sentences)
6. Finally **`" "` and `""`** (words and characters) as last resort

This **hierarchical approach** preserves semantic boundaries — a chunk should ideally contain one complete thought or policy rule.

### Chunk Size & Overlap Rationale

| Parameter | Value | Why |
|---|---|---|
| `chunk_size=800` | ~150-200 words per chunk | Fits within MiniLM's 256-token limit with margin |
| `chunk_overlap=200` | 25% overlap | Ensures sentences at boundaries aren't lost |

### Metadata Enrichment

Each chunk retains rich metadata for citations:
```python
chunk.metadata = {
    "source": "returns_refunds.md",
    "doc_id": "POL-001",
    "title": "Returns & Refunds Policy",
    "chunk_index": 3,
    "total_chunks": 12,
    "section": "Non-Returnable Items",
    "citation": "returns_refunds.md — Non-Returnable Items"
}
```

This metadata is what enables the **100% citation rate** — every retrieved chunk carries its own citation string.

---

## 10. Pydantic Data Validation

### What is Pydantic?

A Python library for **data validation** using Python type annotations. Version 2 (which we use) is a complete rewrite in Rust for performance.

### Why Pydantic in an AI System?

LLM outputs are **unstructured text**. Pydantic provides:
1. **Schema definition**: Clear contracts between agents
2. **Validation**: Catches malformed data before it propagates
3. **Type safety**: Python type hints enforced at runtime
4. **Serialization**: Easy JSON conversion for API responses

### Our Pydantic Models

```python
class TicketInput(BaseModel):
    ticket_id: str
    customer_name: str
    customer_tier: CustomerTier = CustomerTier.BRONZE  # Enum validation
    ticket_text: str
    order_context: Optional[OrderContext] = None       # Nested model

class FinalResolution(BaseModel):
    ticket_id: str
    issue_type: str
    priority: str
    customer_response: str
    compliance_status: str    # "approved" | "escalated" | "max_rewrites_exceeded"
    requires_escalation: bool
    rewrite_count: int = 0
```

### Key Pydantic Features Used

| Feature | Example | Benefit |
|---|---|---|
| `Field(description=...)` | `Field(description="Priority: low, medium, high, urgent")` | Self-documenting schema |
| `Optional[T]` | `delivery_date: Optional[str]` | Handles missing data gracefully |
| `Enum` validation | `CustomerTier.GOLD` | Restricts to valid values only |
| Nested models | `OrderContext` inside `TicketInput` | Validates complex structures |
| Default values | `rewrite_count: int = 0` | Safe defaults for missing fields |

---

## 11. Evaluation & Metrics

### How We Evaluate the System

We run a **23-ticket automated benchmark** covering diverse scenarios:
- 8 standard tickets (refunds, returns, shipping)
- 6 exception-heavy tickets (edge cases, policy conflicts)
- 4 conflict tickets (contradictory information)
- 3 not-in-policy tickets (questions about unsupported features)
- 2 mandatory escalation tickets (fraud, legal threats)

### Metrics Computed

| Metric | Formula | Our Score |
|---|---|---|
| **Citation Coverage Rate** | (tickets with ≥1 citation) / total | 100% |
| **Compliance Pass Rate** | (tickets with "approved" status) / total | 100% |
| **Escalation Rate** | (escalated tickets) / total | As expected |
| **Rewrite Rate** | (tickets requiring ≥1 rewrite) / total | Low |
| **Error Rate** | (tickets with processing errors) / total | 0% |
| **Avg Processing Time** | Mean time per ticket | ~30-50s |

### Why These Metrics Matter

- **Citation Coverage**: Proves the system never generates ungrounded responses
- **Compliance Pass**: Confirms the audit system works — no hallucinations pass through
- **Error Rate**: System stability under real-world conditions

### Evaluation Script Architecture

```python
def run_evaluation():
    # 1. Build vector store from policy docs
    # 2. Initialize the full 4-agent pipeline
    # 3. For each test ticket:
    #    a. Run through pipeline
    #    b. Record results (citations, compliance, time, errors)
    # 4. Compute aggregate metrics
    # 5. Save JSON results + markdown report
```

---

## 12. Model Fundamentals — ML Basics

> The interview email mentions: model fundamentals, basic ML algorithms, training/evaluation, metrics.

### Supervised vs. Unsupervised Learning

| Type | Definition | Examples | In ResolveAI |
|---|---|---|---|
| **Supervised** | Learn from labeled data (input → output pairs) | Classification, regression | Embedding model training (pairs of similar sentences) |
| **Unsupervised** | Find patterns in unlabeled data | Clustering, dimensionality reduction | FAISS clustering (IVF index) |
| **Self-supervised** | Generates own labels from data | BERT (masked language modeling), GPT (next token prediction) | How Gemini was pre-trained |

### Key ML Algorithms (Quick Reference)

| Algorithm | Type | Use Case |
|---|---|---|
| **Linear Regression** | Supervised | Predicting continuous values |
| **Logistic Regression** | Supervised | Binary classification |
| **Decision Trees / Random Forest** | Supervised | Classification with interpretability |
| **K-Nearest Neighbors (KNN)** | Supervised | Classification by similarity |
| **K-Means** | Unsupervised | Clustering data points |
| **SVM** | Supervised | Classification with max margin |
| **Neural Networks** | Supervised | Complex pattern recognition |
| **Transformers** | Self-supervised → Fine-tuned | NLP, LLMs, our embedding model |

### Loss Functions

| Loss | Usage | Formula |
|---|---|---|
| **MSE** | Regression | `(1/n) Σ(y - ŷ)²` |
| **Cross-Entropy** | Classification | `-Σ y·log(ŷ)` |
| **Contrastive Loss** | Embedding training | Pull similar pairs close, push dissimilar apart |
| **Triplet Loss** | Embedding training | `max(0, d(anchor, positive) - d(anchor, negative) + margin)` |

### Bias-Variance Tradeoff

| Concept | Definition |
|---|---|
| **Bias** | Error from overly simple models (underfitting) |
| **Variance** | Error from overly complex models (overfitting) |
| **Tradeoff** | As model complexity increases, bias decreases but variance increases |

### Overfitting vs. Underfitting

| Problem | Symptoms | Solutions |
|---|---|---|
| **Overfitting** | High training accuracy, low test accuracy | Regularization, dropout, more data, early stopping |
| **Underfitting** | Low training accuracy, low test accuracy | More complex model, more features, less regularization |

### Common Evaluation Metrics

| Metric | Formula | When to Use |
|---|---|---|
| **Accuracy** | (TP + TN) / Total | Balanced datasets |
| **Precision** | TP / (TP + FP) | When false positives are costly |
| **Recall** | TP / (TP + FN) | When false negatives are costly |
| **F1 Score** | 2 × (P × R) / (P + R) | Imbalanced datasets |
| **AUC-ROC** | Area under ROC curve | Binary classification ranking |

### NumPy & Pandas Basics

**NumPy**: Numerical computing library — underpins all ML in Python.
```python
import numpy as np
# Vector operations used in embeddings
embedding = np.array([0.23, -0.45, 0.78])
cosine_sim = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
```

**Pandas**: Data manipulation library.
```python
import pandas as pd
df = pd.DataFrame(results)  # Convert evaluation results to table
df.groupby("issue_type")["compliance_status"].value_counts()  # Analyze by category
```

### PyTorch / TensorFlow Basics

While we don't train models from scratch in ResolveAI, the embedding model runs on PyTorch:

```python
# Sentence Transformers uses PyTorch under the hood
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")

# This internally does:
# 1. Tokenize input text
# 2. Pass through PyTorch transformer model
# 3. Pool token embeddings → single vector
# 4. Return 384-dimensional numpy array
```

**Key PyTorch concepts**: Tensors, `torch.no_grad()`, `model.eval()`, GPU acceleration via CUDA.

---

## 13. Deployment — Streamlit Cloud

### What is Streamlit?

A Python framework for building interactive web applications with minimal frontend code. Used for data science dashboards and ML demos.

### Our Deployment Stack

| Component | Detail |
|---|---|
| **Frontend** | Streamlit with glassmorphism dark UI |
| **Hosting** | Streamlit Community Cloud (free tier) |
| **Config** | `.streamlit/config.toml` + Streamlit Secrets |
| **Dependencies** | `requirements.txt` + `packages.txt` (system deps) |

### Deployment Architecture

```
GitHub Repo → Streamlit Cloud (auto-deploy on push)
                    │
                    ├── Install requirements.txt
                    ├── Install packages.txt (system packages)
                    ├── Load .streamlit/secrets.toml → env vars
                    └── Run: streamlit run app.py
```

### Environment Management

```python
# config/settings.py — Pydantic-style settings
class Settings:
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini/gemini-2.5-flash")
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # With validation
    @classmethod
    def validate(cls):
        if not cls.GOOGLE_API_KEY:
            raise ValueError("API key not set!")
```

---

## 14. Debugging & Problem Solving

### Real Problems We Solved (Great Interview Talking Points!)

#### Problem 1: Infinite Agent Loops
**Symptom**: Agent would keep reasoning forever, never producing output.  
**Root Cause**: CrewAI's ReAct loop had no hard stop condition.  
**Solution**: Set `max_iter=3` on every agent + ensure agents output "Final Answer" format.

#### Problem 2: Windows UTF-8 Crashes
**Symptom**: `UnicodeEncodeError` when CrewAI agents used emojis in output.  
**Root Cause**: Windows console uses `cp1252` encoding by default, not UTF-8.  
**Solution**: `sys.stdout.reconfigure(encoding='utf-8')` at startup.

#### Problem 3: Rate Limit 429 Errors
**Symptom**: Gemini API returning HTTP 429 (Too Many Requests).  
**Root Cause**: 4 agents × 1-2 API calls each = 4-8 RPM, close to the 15 RPM limit.  
**Solution**: 5-second `time.sleep()` between agent executions.

#### Problem 4: False-Positive Compliance Rewrites
**Symptom**: Compliance Guard flagging empathetic language as "unsupported claims".  
**Root Cause**: It was treating *all* statements as factual claims needing citations.  
**Solution**: Added explicit prompt instruction: "Do NOT flag empathetic or transitional sentences for missing citations."

#### Problem 5: Agent Output Parsing Failures
**Symptom**: Inconsistent structured output from LLM agents.  
**Root Cause**: LLM sometimes generated freeform text instead of our tagged format.  
**Solution**: Robust regex-based parser with fallback defaults for every field.

---

## 15. Potential Interview Questions

### About Your Project

**Q: Walk me through your project architecture.**
> ResolveAI uses a 4-agent sequential pipeline built on CrewAI. A customer ticket enters the Triage Agent for classification and priority setting. The Policy Researcher then performs semantic search over our FAISS vector store of 13 policy documents using all-MiniLM-L6-v2 embeddings to retrieve the top-3 most relevant policy chunks. The Resolution Architect drafts an empathetic, policy-grounded response with inline citations. Finally, the Compliance Guard audits the response for hallucinations, verifies all citations, and checks for PII leakage. If it fails, the response goes back to the Resolution Architect for a rewrite, with a max_retries=1 hard cap before escalation.

**Q: Why did you use multiple agents instead of one?**
> Single-agent systems have a fundamental problem: the prompt becomes enormous and the model has to handle classification, retrieval, generation, AND verification in one shot. This leads to hallucinations and inconsistent output. By separating concerns — triage, retrieval, drafting, and compliance — each agent has a focused task with a clean prompt. Most importantly, the Compliance Guard acts as a separate verifier that catches hallucinations, which a single agent can't do because it would be checking its own work.

**Q: What is RAG and why did you use it?**
> RAG stands for Retrieval-Augmented Generation. Instead of relying on the LLM's parametric memory (which can hallucinate), we first retrieve relevant policy documents from a vector store and inject them into the LLM's context. This grounds the model's response in verifiable source material. In ResolveAI, the Policy Researcher searches our FAISS index to find relevant policy chunks, and the Resolution Architect can only use those chunks — it's explicitly instructed to never invent policies. This gives us a 100% citation coverage rate.

**Q: How do your word embeddings work?**
> We use the all-MiniLM-L6-v2 model from Sentence Transformers, which produces 384-dimensional vectors. When we build the index, each policy chunk is embedded and stored in FAISS. At query time, the customer's issue is also embedded into the same 384-dimensional space. We then compute L2 distance between the query vector and all stored vectors to find the most semantically similar policy chunks. The key insight is that this captures semantic meaning — "I want a refund" and "return request for damaged item" will be close in vector space even though they share few words.

**Q: What challenges did you face and how did you solve them?**
> The biggest challenge was preventing hallucinations in a production setting. (Then discuss the 5 debugging stories from Section 14.) Each problem has a concrete root cause and solution — a great demonstration of systematic debugging.

### About Theory

**Q: Explain the Transformer architecture.**
> The Transformer uses self-attention to process input sequences in parallel (unlike RNNs which are sequential). Each token computes attention scores with every other token using Query, Key, Value matrices. The attention formula is softmax(QK^T / √d_k) · V. This allows the model to capture long-range dependencies. Modern LLMs like Gemini stack dozens of these layers, each refining the representation.

**Q: What's the difference between fine-tuning and RAG?**
> Fine-tuning modifies the model's weights on domain-specific data — it permanently changes the model. RAG keeps the model unchanged and instead provides relevant information at inference time through retrieval. RAG is better when: (1) data changes frequently (like policies), (2) you need citations for traceability, (3) you don't have GPU resources for fine-tuning. Fine-tuning is better when: (1) you need the model to learn a specific style or behavior, (2) latency is critical (no retrieval overhead).

**Q: Explain cosine similarity vs. L2 distance.**
> Cosine similarity measures the *angle* between two vectors (range: -1 to 1). L2 distance measures the *Euclidean distance* between them (range: 0 to ∞). For normalized vectors, they're mathematically equivalent. FAISS uses L2 by default. We convert to similarity with `1 - distance` for human-readable scores. Cosine is better for comparing meaning (direction matters, not magnitude). L2 is better when magnitude matters.

**Q: What is the bias-variance tradeoff?**
> A simple model (high bias) underfits — it can't capture the data's complexity. A complex model (high variance) overfits — it memorizes training data but fails on new data. The sweet spot is a model complex enough to capture patterns but regularized enough to generalize. In our context, the LLM itself is extremely high-variance (can hallucinate freely), so we add high-bias constraints through our compliance loop and structured prompts.

**Q: How would you evaluate an LLM-based system?**
> Traditional ML metrics like accuracy don't directly apply. For our system, we evaluate: (1) Citation Coverage Rate — does every response cite policy sources? (2) Compliance Pass Rate — does the audit agent approve the response? (3) Faithfulness — is the response consistent with retrieved documents? (4) Relevance — are the retrieved documents actually relevant? (5) Error Rate — system stability. We also use our 23-ticket benchmark with diverse scenarios including edge cases and adversarial queries.

### About Deployment & Engineering

**Q: How did you handle rate limits?**
> Gemini's free tier has a 15 RPM limit. With 4 agents making 1-2 API calls each, we could easily hit this. We implemented a 5-second `time.sleep()` between agent executions as proactive pacing. For evaluation (23 tickets), we added an 8-second inter-ticket delay. We also set `max_iter=3` on all agents to prevent runaway API consumption from infinite reasoning loops.

**Q: How do you ensure no PII leaks in responses?**
> The Compliance Guard explicitly checks for sensitive data in its audit checklist. If PII is detected, it flags `SENSITIVE_DATA_DETECTED: true` and either requests a rewrite or escalates. We also instruct the Resolution Agent to "never share internal-only information" — internal escalation procedures, agent authority levels, and fraud scores are explicitly excluded via negative prompting.

**Q: How would you scale this system?**
> Current bottleneck is the sequential pipeline (~30-50s per ticket). To scale: (1) Async ticket batching with rate-limit-aware queue, (2) Deploy FAISS on a dedicated vector DB service like Pinecone for persistence, (3) Streaming responses to reduce perceived latency, (4) Add session memory so agents reference similar past resolutions, (5) Replace free-tier Gemini with a paid model for higher RPM limits.

---

## Quick Reference Card (Print This!)

### Your Tech Stack — One-Liner Descriptions

| Tech | One-Liner |
|---|---|
| **CrewAI** | Multi-agent orchestration framework — defines agents, tasks, and sequential execution |
| **LangChain** | LLM application framework — we use its document model, text splitters, and FAISS wrapper |
| **FAISS** | Meta's vector similarity search library — stores and searches 384-dim policy chunk embeddings |
| **Gemini 2.5 Flash** | Google's fast, free-tier LLM — powers all 4 agents with temperature=0.1 |
| **all-MiniLM-L6-v2** | HuggingFace sentence embedding model — converts text to 384-dim vectors locally |
| **Pydantic v2** | Data validation library — enforces typed schemas for inputs/outputs across agents |
| **Streamlit** | Python web framework — powers our glassmorphism dashboard UI |
| **RAG** | Retrieval-Augmented Generation — retrieve relevant docs, inject into LLM prompt |
| **FAISS IndexFlatL2** | Brute-force exact search using L2 (Euclidean) distance — perfect for ~200 chunks |
| **RecursiveCharacterTextSplitter** | Hierarchical chunking (headers → paragraphs → sentences → chars) |

### Numbers to Remember

| What | Number |
|---|---|
| Policy documents | 13 |
| Total policy words | ~25,000 |
| Embedding dimensions | 384 |
| Chunk size | 800 characters |
| Chunk overlap | 200 characters |
| Total chunks | ~200 |
| Top-K retrieval | 3 |
| Temperature | 0.1 |
| Max tokens | 2048 |
| Max agent iterations | 3 |
| Max compliance rewrites | 1 |
| Rate limit pacing | 5 seconds |
| Test tickets | 23 |
| Citation coverage | 100% |
| Compliance pass rate | 100% |

---

> [!TIP]
> **Interview Strategy**: Always tie theory back to your project. When asked "What is RAG?", don't just define it — say "RAG is X, and in my project I implemented it by..." This shows both theoretical understanding AND practical application.

> [!IMPORTANT]
> **Key Differentiator**: Most candidates can explain RAG. What sets you apart is the **compliance loop** (Writer ↔ Auditor feedback cycle) and the **zero-hallucination design**. Emphasize that your system doesn't just generate — it **verifies** every claim against source documents.

---

*Good luck with the interview, Tanmay! You've built a genuinely impressive project. Own it. 🚀*
