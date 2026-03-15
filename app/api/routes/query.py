import logging

from fastapi import APIRouter

from app.schemas.query import ChatRequest, ChatResponse
from app.services.query_service import chat_with_openai

router = APIRouter(tags=["chat"])
logger = logging.getLogger(__name__)


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    logger.info("Chat route called")
    return chat_with_openai(
        message=payload.message, conversation_history=payload.conversation_history
    )
