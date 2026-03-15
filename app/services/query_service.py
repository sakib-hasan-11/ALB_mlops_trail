import logging

from openai import OpenAI

from app.core.config import get_settings
from app.schemas.query import ChatResponse, Message

logger = logging.getLogger(__name__)
settings = get_settings()

client = OpenAI(api_key=settings.openai_api_key)


def chat_with_openai(message: str, conversation_history: list[Message]) -> ChatResponse:
    """
    Send a message to OpenAI's chat endpoint with conversation history.
    Logs each step for CloudWatch ingestion.
    """
    logger.info("Starting chat with OpenAI", extra={"model": settings.openai_model})

    # Build messages list for OpenAI API
    messages = []
    for msg in conversation_history:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": message})

    logger.info("Sending request to OpenAI", extra={"message_count": len(messages)})

    try:
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            temperature=0.7,
            max_tokens=512,
        )
        logger.info(
            "Received response from OpenAI",
            extra={"finish_reason": response.choices[0].finish_reason},
        )
        reply = response.choices[0].message.content
    except Exception as exc:
        logger.exception("OpenAI request failed")
        raise exc

    # Update conversation history
    updated_history = [
        Message(role=msg.role, content=msg.content) for msg in conversation_history
    ]
    updated_history.append(Message(role="user", content=message))
    updated_history.append(Message(role="assistant", content=reply))

    logger.info(
        "Chat response prepared", extra={"history_length": len(updated_history)}
    )
    return ChatResponse(reply=reply, conversation_history=updated_history)
