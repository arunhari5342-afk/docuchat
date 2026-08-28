import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Conversation


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


# Create a new conversation
@router.post("", status_code=201)
def create_conversation(
    title: str | None = None,
    db: Session = Depends(get_db),
):
    conversation = Conversation(
        title=title,
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return {
        "conversation_id": str(conversation.id),
        "title": conversation.title,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
    }


# List all conversations
@router.get("")
def list_conversations(
    db: Session = Depends(get_db),
):
    conversations = (
        db.query(Conversation)
        .order_by(Conversation.updated_at.desc())
        .all()
    )

    return {
        "conversations": [
            {
                "conversation_id": str(conversation.id),
                "title": conversation.title,
                "created_at": conversation.created_at,
                "updated_at": conversation.updated_at,
            }
            for conversation in conversations
        ]
    }


# Get a single conversation with messages
@router.get("/{conversation_id}")
def get_conversation(
    conversation_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    messages = sorted(
        conversation.messages,
        key=lambda message: message.created_at,
    )

    return {
        "conversation_id": str(conversation.id),
        "title": conversation.title,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
        "messages": [
            {
                "message_id": str(message.id),
                "role": message.role,
                "content": message.content,
                "metadata": message.message_metadata,
                "created_at": message.created_at,
            }
            for message in messages
        ],
    }


# Delete a conversation
@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    db.delete(conversation)
    db.commit()

    return {
        "message": "Conversation deleted successfully",
        "conversation_id": str(conversation_id),
    }