# Architecture Diagram

This diagram shows both the current backend flow and the future phone-call path for the salon assistant.

```mermaid
flowchart LR
    caller["Caller"]
    phone["Phone Provider\n(Twilio or similar)"]
    webhook["Voice / Webhook Layer"]
    api["FastAPI Backend"]
    assistant["Assistant Route\nPOST /assistant/respond"]
    orchestrator["Conversation Orchestrator"]
    prompt["Salon System Prompt"]
    model["Ollama Model\nResponses API"]
    tools["Local Tool Registry"]
    pricing["Pricing Service"]
    booking["Booking Service"]
    feedback["Feedback Service"]
    db["SQLite / PostgreSQL"]
    dashboard["Staff Dashboard\n(Future)"]
    staff["Salon Staff"]

    caller --> phone
    phone --> webhook
    webhook --> assistant
    assistant --> orchestrator
    prompt --> orchestrator
    orchestrator --> model
    model --> orchestrator
    orchestrator --> tools
    tools --> pricing
    tools --> booking
    tools --> feedback
    pricing --> db
    booking --> db
    feedback --> db
    dashboard --> api
    api --> db
    orchestrator --> assistant
    assistant --> webhook
    webhook --> phone
    phone --> caller
    webhook -. "handoff / fallback" .-> staff

    classDef external fill:#f4efe6,stroke:#7a5c28,color:#2d2418;
    classDef backend fill:#e8f2ff,stroke:#3169b3,color:#14243d;
    classDef ai fill:#eef8ee,stroke:#2f7d4a,color:#163322;
    classDef data fill:#fff4e6,stroke:#b46b1f,color:#4a2a00;
    classDef human fill:#fbe9ef,stroke:#b33a62,color:#4a1426;

    class caller,phone,webhook external;
    class api,assistant,tools,pricing,booking,feedback,dashboard backend;
    class orchestrator,prompt,model ai;
    class db data;
    class staff human;
```

## Legend

- Beige `external`: outside-facing systems and transport layers such as the caller, telephony provider, and webhook entrypoint
- Blue `backend`: application-owned backend components including routes, tool registry, and business services
- Green `ai`: AI orchestration components including the prompt, orchestrator, and model
- Orange `data`: persistent storage and source-of-truth data systems
- Pink `human`: manual fallback or staff-assisted parts of the workflow

## Reading the Diagram

- `Caller -> Phone Provider -> Voice / Webhook Layer` is the future live-call path.
- `POST /assistant/respond` is the current application entry point for text-driven orchestration.
- `Conversation Orchestrator` sends the caller request, system prompt, and tool definitions to the model.
- The model can call local tools for prices, availability, and booking instead of inventing salon data.
- Business services read and write the database, which remains the source of truth.
- If the assistant cannot safely handle a request, the flow can hand off to salon staff.
