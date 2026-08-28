from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.routers.documents import router as documents_router
from app.routers.retrieval import router as retrieval_router
from app.routers.conversations import router as conversations_router
from app.routers.chat import router as chat_router
from app.models import Document, DocumentChunk, Conversation, Message
from app.core.database import get_db



app = FastAPI(
    title="DocuChat",
    description="A RAG-powered document chat application",
    version="1.0.0",
)

app.include_router(documents_router)
app.include_router(retrieval_router)
app.include_router(chat_router)
app.include_router(conversations_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to DocuChat",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


@app.get("/health/db")
def database_health(db: Session = Depends(get_db)):
    result = db.execute(
        text("SELECT current_database()")
    )

    database_name = result.scalar()

    return {
        "status": "healthy",
        "database": database_name,
    }

@app.get("/health/vector")
def vector_health(db: Session = Depends(get_db)):
    result = db.execute(
        text("""
            SELECT extname, extversion
            FROM pg_extension
            WHERE extname = 'vector'
        """)
    )

    vector_extension = result.fetchone()

    if not vector_extension:
        return {
            "status": "error",
            "message": "pgvector extension not found",
        }

    return {
        "status": "healthy",
        "extension": vector_extension[0],
        "version": vector_extension[1],
    }