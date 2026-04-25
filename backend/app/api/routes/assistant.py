from fastapi import APIRouter, Depends, HTTPException, status

from app.ai.orchestrator import ConversationOrchestrator, get_orchestrator
from app.schemas.assistant import AssistantRequest, AssistantResponse, ToolResult

router = APIRouter()


def get_assistant_orchestrator() -> ConversationOrchestrator:
    try:
        return get_orchestrator()
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.post("/respond", response_model=AssistantResponse)
def respond(
    payload: AssistantRequest,
    orchestrator: ConversationOrchestrator = Depends(get_assistant_orchestrator),
) -> AssistantResponse:
    try:
        result = orchestrator.respond(
            user_utterance=payload.user_utterance,
            conversation_history=[item.model_dump() for item in payload.conversation_history],
            caller_phone=payload.caller_phone,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return AssistantResponse(
        assistant_text=result["assistant_text"],
        tools_used=result["tools_used"],
        tool_results=[ToolResult(**item) for item in result["tool_results"]],
    )
