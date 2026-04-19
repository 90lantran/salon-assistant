# MVP Architecture

Core pieces:

- `backend/app/api`: HTTP endpoints and phone webhooks
- `backend/app/ai`: AI-facing tool definitions and orchestration
- `backend/app/db.py`: database engine and shared ORM base
- `backend/app/services`: business logic for pricing, booking, and feedback
- `backend/app/models`: database models
- `backend/app/schemas`: request/response schemas
- `infra`: deployment and infrastructure notes
- `scripts`: local development helpers

MVP data model:

- `services`: nail services, price, duration, category, active flag
- `customers`: caller/customer profile keyed by phone number
- `appointments`: scheduled service visits and booking status
- `business_hours`: salon opening windows by day of week
- `feedback`: post-service ratings, comments, and follow-up requests

Suggested delivery order:

1. Build text-first APIs and booking logic.
2. Add AI tool calling against those APIs/services.
3. Add telephony and voice handling.
4. Add dashboard, logs, and production hardening.
