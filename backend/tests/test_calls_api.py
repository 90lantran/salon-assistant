from fastapi.testclient import TestClient

from app.api.routes.calls import CALL_SESSIONS, get_call_orchestrator
from app.main import app


class StubCallOrchestrator:
    def __init__(self, response_text: str, tool_results: list[dict] | None = None) -> None:
        self.response_text = response_text
        self.tool_results = tool_results or []
        self.calls: list[dict] = []

    def respond(self, **kwargs):
        self.calls.append(kwargs)
        return {
            "assistant_text": self.response_text,
            "tools_used": [item["tool_name"] for item in self.tool_results],
            "tool_results": self.tool_results,
        }


client = TestClient(app)


def teardown_function() -> None:
    app.dependency_overrides.clear()
    CALL_SESSIONS.clear()


def test_incoming_call_returns_gather_twiml() -> None:
    response = client.post("/calls/incoming", data={"CallSid": "CA123"})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/xml")
    assert "<Gather" in response.text
    assert "ask about prices, availability, or booking an appointment" in response.text


def test_process_call_input_uses_orchestrator_and_reprompts() -> None:
    stub = StubCallOrchestrator("A gel manicure is $35. Would you like to book it?")
    app.dependency_overrides[get_call_orchestrator] = lambda: stub
    CALL_SESSIONS["CA123"] = []

    response = client.post(
        "/calls/process-speech",
        data={
            "CallSid": "CA123",
            "From": "+15551234567",
            "SpeechResult": "How much is a gel manicure?",
        },
    )

    assert response.status_code == 200
    assert "<Gather" in response.text
    assert "A gel manicure is $35. Would you like to book it?" in response.text
    assert stub.calls[0]["caller_phone"] == "+15551234567"
    assert stub.calls[0]["conversation_history"] == []
    assert CALL_SESSIONS["CA123"][0]["content"] == "How much is a gel manicure?"


def test_process_call_input_hangs_up_after_booking_confirmation() -> None:
    stub = StubCallOrchestrator(
        "Your gel manicure is booked for Monday at 2 PM. See you then.",
        tool_results=[{"tool_name": "create_appointment", "result": {"created": True}}],
    )
    app.dependency_overrides[get_call_orchestrator] = lambda: stub
    CALL_SESSIONS["CA999"] = []

    response = client.post(
        "/calls/process-speech",
        data={
            "CallSid": "CA999",
            "SpeechResult": "Book me for Monday at 2",
        },
    )

    assert response.status_code == 200
    assert "<Hangup" in response.text
    assert "booked for Monday at 2 PM" in response.text
    assert "CA999" not in CALL_SESSIONS


def test_process_call_input_reprompts_on_empty_speech() -> None:
    stub = StubCallOrchestrator("unused")
    app.dependency_overrides[get_call_orchestrator] = lambda: stub
    CALL_SESSIONS["CAEMPTY"] = []

    response = client.post("/calls/process-speech", data={"CallSid": "CAEMPTY"})

    assert response.status_code == 200
    assert "I didn't catch that" in response.text
    assert stub.calls == []
