from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    conversation_id: str | None = None
    message: str = Field(min_length=1, max_length=8000)
    subject: str
    learning_level: str
    explanation_style: str
    learning_mode: str


class CreateConversationRequest(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    subject: str
    learning_level: str
    explanation_style: str
    learning_mode: str


class MessageExportResponse(BaseModel):
    conversation_id: str
    markdown: str
