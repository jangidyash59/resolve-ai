# Bugfix Requirements Document

## Introduction

The AI service ticket resolution system currently fails when processing customer support tickets due to incompatible API calls between CrewAI framework and Groq API. The orchestrator uses CrewAI's `responses.parse()` and `responses.create()` methods which attempt to call OpenAI-incompatible endpoints (`/responses`) that don't exist in Groq's API specification. This causes all ticket processing to fail with 400 Bad Request errors, rendering the entire AI resolution pipeline non-functional.

The fix involves replacing the CrewAI-based agent orchestration with direct Groq SDK implementation using the standard `/chat/completions` endpoint, while preserving the existing multi-agent workflow logic (Triage → Policy Retrieval → Resolution → Compliance).

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN a customer support ticket is submitted for AI processing THEN the system calls `get_openai_client().responses.parse()` which attempts to access the non-existent `/responses` endpoint on Groq API

1.2 WHEN the orchestrator executes the triage agent THEN Groq API returns 400 Bad Request error because the `/responses` endpoint is not part of Groq's OpenAI-compatible API specification

1.3 WHEN the policy retriever agent executes with `get_openai_client().responses.create()` THEN the same 400 Bad Request error occurs due to the incompatible endpoint

1.4 WHEN any agent in the pipeline (triage, retriever, resolution, compliance) is invoked THEN the error propagates to the FastAPI service and returns "Failed to process ticket through AI service" to the frontend

1.5 WHEN CrewAI Agent objects are instantiated with `llm` parameter THEN they introduce additional overhead and dependencies that are incompatible with Groq's API structure

### Expected Behavior (Correct)

2.1 WHEN a customer support ticket is submitted for AI processing THEN the system SHALL use `client.chat.completions.create()` method from the Groq SDK to call the standard `/chat/completions` endpoint

2.2 WHEN the orchestrator executes the triage agent THEN it SHALL successfully receive structured JSON output conforming to the `TriageResult` schema using JSON mode or function calling

2.3 WHEN the policy retriever agent executes THEN it SHALL successfully call the search_policies function via Groq's native function calling mechanism and retrieve relevant policy excerpts

2.4 WHEN the resolution agent executes THEN it SHALL generate customer-facing responses using the standard chat completions API with structured output constraints

2.5 WHEN the compliance agent performs validation THEN it SHALL audit the resolution using the standard chat completions API and return a structured `ComplianceResult`

2.6 WHEN all agents complete successfully THEN the system SHALL return a properly formatted resolution to the frontend without any API compatibility errors

### Unchanged Behavior (Regression Prevention)

3.1 WHEN the FAISS vector store is initialized with policy documents THEN the system SHALL CONTINUE TO load 301 policy chunks and create embeddings using sentence-transformers/all-MiniLM-L6-v2

3.2 WHEN search_policies() function is called with a query string THEN the system SHALL CONTINUE TO perform FAISS similarity search and return policy excerpts with citations and relevance scores

3.3 WHEN the multi-agent pipeline executes (Triage → Retrieval → Resolution → Compliance) THEN the system SHALL CONTINUE TO follow the same logical workflow order and decision-making process

3.4 WHEN triage identifies missing required fields THEN the system SHALL CONTINUE TO return status "needs_clarification" with clarifying questions rather than proceeding to resolution

3.5 WHEN compliance validation fails THEN the system SHALL CONTINUE TO trigger a rewrite or escalation following the same business rules

3.6 WHEN the SupportOrchestrator.resolve_ticket() method is called THEN the system SHALL CONTINUE TO accept TicketInput and return FinalResolution with the same schema structure

3.7 WHEN environment variables (GROQ_API_KEY, GROQ_MODEL, EMBEDDING_MODEL) are loaded THEN the system SHALL CONTINUE TO use the same configuration values from the .env file

3.8 WHEN invalid citations are detected by find_invalid_citations() THEN the system SHALL CONTINUE TO enforce citation validation using the same deterministic logic

3.9 WHEN the FastAPI service integrates with the orchestrator THEN the system SHALL CONTINUE TO maintain the same API contract and response format

3.10 WHEN DEBUG_MODE is enabled THEN the system SHALL CONTINUE TO output debug_print() messages showing pipeline progress
