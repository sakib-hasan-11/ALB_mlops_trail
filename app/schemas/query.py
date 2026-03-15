from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., min_length=1, max_length=4096)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4096)
    conversation_history: list[Message] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str
    conversation_history: list[Message]
