import json
from typing import Any, Protocol

import httpx

from app.ai.prompt import SALON_ASSISTANT_SYSTEM_PROMPT
from app.ai.tools import call_tool, get_tool_definitions
from app.core.config import settings


class ResponseOutputItem(Protocol):
    type: str


class ModelResponse(Protocol):
    output: list[ResponseOutputItem]
    output_text: str


class ToolCallFunction(Protocol):
    name: str
    arguments: dict[str, Any]


class ToolCall(Protocol):
    function: ToolCallFunction


class ModelClient(Protocol):
    def create_response(
        self,
        *,
        model: str,
        instructions: str,
        tools: list[dict[str, Any]],
        input_items: list[dict[str, Any]],
    ) -> ModelResponse: ...


class OllamaToolCallFunction:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.name = payload["name"]
        self.arguments = payload.get("arguments", {})


class OllamaToolCall:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.function = OllamaToolCallFunction(payload["function"])


class OllamaOutputItem:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.type = payload.get("type", "message")
        self.content = payload.get("content", "")
        self.tool_calls = [OllamaToolCall(item) for item in payload.get("tool_calls", [])]

    def model_dump(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "role": "assistant",
            "content": self.content,
        }
        if self.tool_calls:
            payload["tool_calls"] = [
                {
                    "type": "function",
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments,
                    },
                }
                for call in self.tool_calls
            ]
        return payload


class OllamaModelResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        message = payload.get("message", {})
        self.output = [OllamaOutputItem(message)]
        self.output_text = message.get("content", "")


class OllamaChatClient:
    def __init__(self, base_url: str) -> None:
        self._client = httpx.Client(base_url=base_url, timeout=60.0)

    def create_response(
        self,
        *,
        model: str,
        instructions: str,
        tools: list[dict[str, Any]],
        input_items: list[dict[str, Any]],
    ) -> Any:
        messages = [{"role": "system", "content": instructions}, *input_items]
        try:
            response = self._client.post(
                "/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "tools": tools,
                    "stream": False,
                },
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise RuntimeError(
                "Ollama is unavailable. Make sure the Ollama app is running and the model is pulled."
            ) from exc

        return OllamaModelResponse(response.json())


class ConversationOrchestrator:
    def __init__(
        self,
        *,
        model_client: ModelClient,
        model: str,
        system_prompt: str = SALON_ASSISTANT_SYSTEM_PROMPT,
        max_round_trips: int = 5,
    ) -> None:
        self.model_client = model_client
        self.model = model
        self.system_prompt = system_prompt
        self.max_round_trips = max_round_trips

    def respond(
        self,
        *,
        user_utterance: str,
        conversation_history: list[dict[str, str]] | None = None,
        caller_phone: str | None = None,
    ) -> dict[str, Any]:
        input_items = self._build_input_items(
            user_utterance=user_utterance,
            conversation_history=conversation_history or [],
            caller_phone=caller_phone,
        )
        tools = self._build_tools()
        tools_used: list[str] = []
        tool_results: list[dict[str, Any]] = []

        for _ in range(self.max_round_trips):
            response = self.model_client.create_response(
                model=self.model,
                instructions=self.system_prompt,
                tools=tools,
                input_items=input_items,
            )

            input_items.extend(self._serialize_output_item(item) for item in response.output)

            function_calls = self._extract_function_calls(response.output)
            if not function_calls:
                return {
                    "assistant_text": response.output_text.strip(),
                    "tools_used": tools_used,
                    "tool_results": tool_results,
                }

            for tool_call in function_calls:
                tools_used.append(tool_call.function.name)
                result = self._execute_tool_call(tool_call)
                tool_results.append({"tool_name": tool_call.function.name, "result": result})
                input_items.append(
                    {
                        "role": "tool",
                        "tool_name": tool_call.function.name,
                        "content": json.dumps(result),
                    }
                )

        return {
            "assistant_text": (
                "I’m sorry, I need a salon staff member to help with this request."
            ),
            "tools_used": tools_used,
            "tool_results": tool_results,
        }

    def _build_input_items(
        self,
        *,
        user_utterance: str,
        conversation_history: list[dict[str, str]],
        caller_phone: str | None,
    ) -> list[dict[str, Any]]:
        input_items: list[dict[str, Any]] = []

        if caller_phone:
            input_items.append(
                {
                    "role": "system",
                    "content": f"Caller phone number on file: {caller_phone}",
                }
            )

        for message in conversation_history:
            input_items.append(
                {
                    "role": message["role"],
                    "content": message["content"],
                }
            )

        input_items.append({"role": "user", "content": user_utterance})
        return input_items

    def _build_tools(self) -> list[dict[str, Any]]:
        tools: list[dict[str, Any]] = []

        for definition in get_tool_definitions():
            parameters = dict(definition["input_schema"])
            parameters.setdefault("additionalProperties", False)
            tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": definition["name"],
                        "description": definition["description"],
                        "parameters": parameters,
                    },
                }
            )

        return tools

    def _extract_function_calls(self, items: list[ResponseOutputItem]) -> list[ToolCall]:
        function_calls: list[ToolCall] = []

        for item in items:
            tool_calls = getattr(item, "tool_calls", [])
            function_calls.extend(tool_calls)

        return function_calls

    def _execute_tool_call(self, tool_call: ToolCall) -> dict[str, Any]:
        try:
            return call_tool(tool_call.function.name, tool_call.function.arguments)
        except Exception as exc:
            return {
                "ok": False,
                "tool_name": tool_call.function.name,
                "message": (
                    "Tool execution failed. Ask the caller for a clearer date, time, or service."
                ),
                "error": str(exc),
            }

    def _serialize_output_item(self, item: Any) -> dict[str, Any]:
        if hasattr(item, "model_dump"):
            return item.model_dump()
        if isinstance(item, dict):
            return item
        return item.__dict__


def get_orchestrator() -> ConversationOrchestrator:
    return ConversationOrchestrator(
        model_client=OllamaChatClient(base_url=settings.ollama_base_url),
        model=settings.ollama_model,
    )
