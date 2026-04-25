from dataclasses import dataclass

from app.ai.orchestrator import ConversationOrchestrator


@dataclass
class FakeToolCallFunction:
    name: str
    arguments: dict


@dataclass
class FakeToolCall:
    function: FakeToolCallFunction


@dataclass
class FakeOutputItem:
    type: str
    tool_calls: list[FakeToolCall] | None = None
    content: str = ""

    def model_dump(self) -> dict:
        payload = {"role": "assistant", "content": self.content}
        if self.tool_calls is not None:
            payload["tool_calls"] = [
                {
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                    },
                }
                for tool_call in self.tool_calls
            ]
        return payload


@dataclass
class FakeResponse:
    output: list[FakeOutputItem]
    output_text: str


class FakeModelClient:
    def __init__(self, responses: list[FakeResponse]) -> None:
        self.responses = responses
        self.calls: list[dict] = []

    def create_response(self, **kwargs):
        self.calls.append(kwargs)
        return self.responses.pop(0)


def test_orchestrator_handles_tool_call_then_final_text() -> None:
    fake_client = FakeModelClient(
        responses=[
            FakeResponse(
                output=[
                    FakeOutputItem(
                        type="message",
                        tool_calls=[
                            FakeToolCall(
                                function=FakeToolCallFunction(
                                    name="lookup_service_price",
                                    arguments={"service_name": "Gel Manicure"},
                                )
                            )
                        ],
                    )
                ],
                output_text="",
            ),
            FakeResponse(output=[], output_text="A gel manicure is $35 and takes about 60 minutes."),
        ]
    )
    orchestrator = ConversationOrchestrator(model_client=fake_client, model="qwen3")

    result = orchestrator.respond(user_utterance="How much is a gel manicure?")

    assert result["assistant_text"] == "A gel manicure is $35 and takes about 60 minutes."
    assert result["tools_used"] == ["lookup_service_price"]
    assert result["tool_results"][0]["result"]["found"] is False or isinstance(
        result["tool_results"][0]["result"],
        dict,
    )
    assert len(fake_client.calls) == 2


def test_orchestrator_includes_phone_context_and_history() -> None:
    fake_client = FakeModelClient(
        responses=[FakeResponse(output=[], output_text="Sure, what service would you like to book?")]
    )
    orchestrator = ConversationOrchestrator(model_client=fake_client, model="qwen3")

    orchestrator.respond(
        user_utterance="I want to book an appointment.",
        caller_phone="5551234567",
        conversation_history=[{"role": "assistant", "content": "Welcome to the salon."}],
    )

    first_call = fake_client.calls[0]
    assert first_call["instructions"]
    assert first_call["input_items"][0]["content"] == "Caller phone number on file: 5551234567"
    assert first_call["input_items"][1]["content"] == "Welcome to the salon."


def test_orchestrator_handles_invalid_tool_arguments_without_crashing() -> None:
    fake_client = FakeModelClient(
        responses=[
            FakeResponse(
                output=[
                    FakeOutputItem(
                        type="message",
                        tool_calls=[
                            FakeToolCall(
                                function=FakeToolCallFunction(
                                    name="check_availability",
                                    arguments={"service_name": "Gel Manicure", "requested_date": "tomorrow"},
                                )
                            )
                        ],
                    )
                ],
                output_text="",
            ),
            FakeResponse(
                output=[],
                output_text="I can help with that if you tell me the exact date you'd like.",
            ),
        ]
    )
    orchestrator = ConversationOrchestrator(model_client=fake_client, model="qwen3")

    result = orchestrator.respond(user_utterance="Do you have anything tomorrow?")

    assert result["assistant_text"] == "I can help with that if you tell me the exact date you'd like."
    assert result["tools_used"] == ["check_availability"]
    assert result["tool_results"][0]["result"]["ok"] is False
    assert "Tool execution failed" in result["tool_results"][0]["result"]["message"]
