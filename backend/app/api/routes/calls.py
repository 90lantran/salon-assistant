from collections.abc import Iterable
from xml.etree.ElementTree import Element, SubElement, tostring

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import Response

from app.ai.orchestrator import ConversationOrchestrator, get_orchestrator
from app.core.config import settings

router = APIRouter()

CALL_SESSIONS: dict[str, list[dict[str, str]]] = {}


@router.post("/incoming")
def incoming_call(
    request: Request,
    call_sid: str = Form(..., alias="CallSid"),
) -> Response:
    CALL_SESSIONS[call_sid] = []

    return _xml_response(
        _gather_response(
            action_url=str(request.url_for("process_call_input")),
            prompt=(
                f"Thank you for calling {settings.salon_name}. "
                "You can ask about prices, availability, or booking an appointment."
            ),
        )
    )


def get_call_orchestrator() -> ConversationOrchestrator:
    try:
        return get_orchestrator()
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.post("/process-speech", name="process_call_input")
def process_call_input(
    request: Request,
    orchestrator: ConversationOrchestrator = Depends(get_call_orchestrator),
    call_sid: str = Form(..., alias="CallSid"),
    caller_phone: str | None = Form(default=None, alias="From"),
    speech_result: str | None = Form(default=None, alias="SpeechResult"),
    digits: str | None = Form(default=None, alias="Digits"),
) -> Response:
    utterance = _normalize_utterance(speech_result, digits)
    action_url = str(request.url_for("process_call_input"))

    if not utterance:
        return _xml_response(
            _gather_response(
                action_url=action_url,
                prompt="I didn't catch that. Please tell me the service or appointment help you need.",
            )
        )

    if utterance.lower() in {"goodbye", "bye", "no thanks", "that is all", "that's all"}:
        return _xml_response(_say_and_hangup("Thank you for calling. Goodbye."))

    history = CALL_SESSIONS.setdefault(call_sid, [])
    result = orchestrator.respond(
        user_utterance=utterance,
        conversation_history=list(history),
        caller_phone=caller_phone,
    )

    history.extend(
        [
            {"role": "user", "content": utterance},
            {"role": "assistant", "content": result["assistant_text"]},
        ]
    )

    if _should_forward_to_staff(utterance, result["assistant_text"]):
        if settings.twilio_forward_number:
            return _xml_response(
                _say_and_dial(
                    "Please hold while I transfer you to the salon team.",
                    settings.twilio_forward_number,
                )
            )
        return _xml_response(
            _say_and_hangup(
                "A salon team member will need to help with that. Please call back during business hours."
            )
        )

    if _booking_was_created(result["tool_results"]):
        CALL_SESSIONS.pop(call_sid, None)
        return _xml_response(_say_and_hangup(result["assistant_text"]))

    return _xml_response(
        _gather_response(
            action_url=action_url,
            prompt=f"{result['assistant_text']} You can tell me another service, date, or time.",
        )
    )


def _normalize_utterance(speech_result: str | None, digits: str | None) -> str:
    if speech_result and speech_result.strip():
        return speech_result.strip()
    if digits and digits.strip():
        return digits.strip()
    return ""


def _booking_was_created(tool_results: list[dict]) -> bool:
    return any(
        item.get("tool_name") == "create_appointment"
        and item.get("result", {}).get("created") is True
        for item in tool_results
    )


def _should_forward_to_staff(utterance: str, assistant_text: str) -> bool:
    lowered_utterance = utterance.lower()
    lowered_reply = assistant_text.lower()
    return lowered_utterance == "0" or "staff member" in lowered_reply


def _xml_response(root: Element) -> Response:
    return Response(
        content=tostring(root, encoding="unicode"),
        media_type="application/xml",
    )


def _gather_response(action_url: str, prompt: str) -> Element:
    root = Element("Response")
    gather = SubElement(
        root,
        "Gather",
        {
            "input": "speech dtmf",
            "action": action_url,
            "method": "POST",
            "speechTimeout": "auto",
            "actionOnEmptyResult": "true",
        },
    )
    _append_say(gather, prompt)
    _append_say(root, "I still did not receive any input. Goodbye.")
    return root


def _say_and_hangup(message: str) -> Element:
    root = Element("Response")
    _append_say(root, message)
    SubElement(root, "Hangup")
    return root


def _say_and_dial(message: str, phone_number: str) -> Element:
    root = Element("Response")
    _append_say(root, message)
    dial = SubElement(root, "Dial")
    dial.text = phone_number
    return root


def _append_say(parent: Element, message: str) -> None:
    say = SubElement(parent, "Say", {"voice": "woman", "language": "en-US"})
    say.text = _sanitize_for_speech(message)


def _sanitize_for_speech(message: str) -> str:
    return " ".join(message.split())
