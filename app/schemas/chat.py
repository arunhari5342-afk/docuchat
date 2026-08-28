import uuid

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        description="Question to ask about the uploaded documents.",
    )

    conversation_id: uuid.UUID | None = Field(
        default=None,
        description="Existing conversation ID for follow-up questions.",
    )

    top_k: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of relevant document chunks to retrieve.",
    )


class SourceResponse(BaseModel):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    filename: str
    distance: float


class ChatResponse(BaseModel):
    conversation_id: uuid.UUID
    query: str
    answer: str
    sources: list[SourceResponse]