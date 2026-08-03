# ResolveAI UI integration

This version keeps the existing Streamlit form and `src.models` contract while
using the OpenAI Responses API and a native FAISS index in
`src/orchestrator.py`.

## Required setup

1. Copy `.env.example` to `.env`.
2. Set `OPENAI_API_KEY`.
3. Install packages with `pip install -r requirements.txt`.
4. Start the app with `streamlit run app.py`.

The app builds or loads `faiss_store/policies.index` and
`faiss_store/policies.json` automatically. You can also build them first with
`python build_index.py`.

## UI/backend contract

- The form creates `TicketInput`, `OrderContext`, and `OrderItem` objects.
- `SupportOrchestrator.resolve_ticket(ticket)` runs triage, policy retrieval,
  resolution writing, and compliance review.
- It always returns `FinalResolution`, which contains every property used by
  `display_result()` and Results History.
- Order context is optional. Photo and video uploads are also optional at
  intake; the response can request policy-required evidence later.
- Customer email is retained by the UI but is not sent to the LLM.
- No `orders.json` file or order-status tool is required.

## Generated files

Do not commit `.env` or `faiss_store/`. The index is regenerated from the
Markdown files in `data/policies/` whenever the saved metadata or embedding
model no longer matches.
