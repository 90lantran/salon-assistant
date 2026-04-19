# Backend

FastAPI-oriented backend for:

- service catalog and price lookup
- appointment booking and cancellation
- customer lookup
- feedback capture
- voice/call webhooks

Key app entrypoint: `app/main.py`

Quick start:

```bash
cd /Users/ltran/vibe-coding/salon-assistant/backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/seed_demo_data.py
.venv/bin/uvicorn app.main:app --reload
```
