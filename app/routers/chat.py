import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Conversation, Message
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm import generate_answer
from app.services.question_rewriter import rewrite_question
from app.services.retrieval import retrieve_similar_chunks


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


DEMO_USER_ID = uuid.UUID(
    "11111111-1111-1111-1111-111111111111"
)


@router.post(
    "",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    query = request.query.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty.",
        )

    # ---------------------------------------------------------
    # 1. Find existing conversation or create a new one
    # ---------------------------------------------------------

    if request.conversation_id:
        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.id == request.conversation_id,
                Conversation.user_id == DEMO_USER_ID,
            )
            .first()
        )

        if not conversation:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found.",
            )

    else:
        conversation = Conversation(
            user_id=DEMO_USER_ID,
            title=query[:255],
        )

        db.add(conversation)
        db.flush()

    # ---------------------------------------------------------
    # 2. Get previous conversation history
    # ---------------------------------------------------------

    previous_messages = (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation.id
        )
        .order_by(Message.created_at.asc())
        .all()
    )

    history = "\n".join(
        f"{message.role.capitalize()}: {message.content}"
        for message in previous_messages
    )

    # ---------------------------------------------------------
    # 3. Rewrite follow-up question
    # ---------------------------------------------------------

    standalone_question = rewrite_question(
        query=query,
        history=history,
    )

    # ---------------------------------------------------------
    # 4. Save original user question
    # ---------------------------------------------------------

    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=query,
        message_metadata={
            "rewritten_question": standalone_question,
        },
    )

    db.add(user_message)

    # ---------------------------------------------------------
    # 5. Retrieve using rewritten question
    # ---------------------------------------------------------

    results = retrieve_similar_chunks(
        db=db,
        query=standalone_question,
        top_k=request.top_k,
    )

    # ---------------------------------------------------------
    # 6. No relevant documents found
    # ---------------------------------------------------------

    if not results:
        answer = (
            "I could not find the answer "
            "in the uploaded documents."
        )

        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=answer,
            message_metadata={
                "sources": [],
                "rewritten_question": standalone_question,
            },
        )

        db.add(assistant_message)
        db.commit()

        return ChatResponse(
            conversation_id=conversation.id,
            query=query,
            answer=answer,
            sources=[],
        )

    # ---------------------------------------------------------
    # 7. Build document context
    # ---------------------------------------------------------

    context = "\n\n".join(
        result["content"]
        for result in results
    )

    # ---------------------------------------------------------
    # 8. Generate grounded answer
    # ---------------------------------------------------------

    answer = generate_answer(
        query=query,
        context=context,
        history=history,
    )

    # ---------------------------------------------------------
    # 9. Prepare sources
    # ---------------------------------------------------------

    sources = [
        {
            "chunk_id": uuid.UUID(
                str(result["chunk_id"])
            ),
            "document_id": uuid.UUID(
                str(result["document_id"])
            ),
            "filename": result["filename"],
            "distance": float(result["distance"]),
        }
        for result in results
    ]

    # ---------------------------------------------------------
    # 10. Save assistant response
    # ---------------------------------------------------------

    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=answer,
        message_metadata={
            "rewritten_question": standalone_question,
            "sources": [
                {
                    "chunk_id": str(source["chunk_id"]),
                    "document_id": str(source["document_id"]),
                    "filename": source["filename"],
                    "distance": source["distance"],
                }
                for source in sources
            ],
        },
    )

    db.add(assistant_message)

    db.commit()

    # ---------------------------------------------------------
    # 11. Return response
    # ---------------------------------------------------------

    return ChatResponse(
        conversation_id=conversation.id,
        query=query,
        answer=answer,
        sources=sources,
    )