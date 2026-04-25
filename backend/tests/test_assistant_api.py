from fastapi.testclient import TestClient

from app.api.routes.assistant import get_assistant_orchestrator
from app.main import app


class StubOrchestrator:
    def respond(self, **kwargs):
        return {
            "assistant_text": "I can help with that. Which service would you like?",
            "tools_used": ["lookup_service_price"],
            "tool_results": [
                {"tool_name": "lookup_service_price", "result": {"found": True}}
            ],
        }


client = TestClient(app)


def setup_function() -> None:
    app.dependency_overrides[get_assistant_orchestrator] = lambda: StubOrchestrator()


def teardown_function() -> None:
    app.dependency_overrides.clear()


def test_assistant_respond_route_returns_phone_friendly_reply() -> None:
    response = client.post(
        "/assistant/respond",
        json={
            "user_utterance": "Can you help me book an appointment?",
            "caller_phone": "5551234567",
            "conversation_history": [{"role": "assistant", "content": "Hello!"}],
        },
    )

    assert response.status_code == 200
    assert response.json()["assistant_text"] == "I can help with that. Which service would you like?"
