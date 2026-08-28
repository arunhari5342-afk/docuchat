import uuid

from fastapi import APIRouter, Depends, File, UploadFile, status, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Document
from app.services.ingestion.service import ingest_document


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    allowed_types = {
        ".txt",
        ".pdf",
    }

    filename = file.filename or ""

    extension = filename.lower().rsplit(".", 1)[-1]

    extension = f".{extension}" if extension else ""

    if extension not in allowed_types:
        return {
            "error": "Unsupported file type",
            "allowed_types": [".txt", ".pdf"],
        }

    file_content = file.file.read()

    document = ingest_document(
        db=db,
        filename=filename,
        file_content=file_content,
    )

    return {
        "message": "Document uploaded and indexed successfully",
        "document_id": str(document.id),
        "filename": document.filename,
    }


@router.get("")
def list_documents(
    db: Session = Depends(get_db),
):
    documents = (
        db.query(Document)
        .order_by(Document.created_at.desc())
        .all()
    )

    return {
        "documents": [
            {
                "document_id": str(document.id),
                "filename": document.filename,
                "file_type": document.file_type,
                "created_at": document.created_at,
                "chunk_count": len(document.chunks),
            }
            for document in documents
        ]
    }


@router.get("/{document_id}")
def get_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return {
        "document_id": str(document.id),
        "filename": document.filename,
        "file_type": document.file_type,
        "file_path": document.file_path,
        "metadata": document.document_metadata,
        "created_at": document.created_at,
        "chunks": [
            {
                "chunk_id": str(chunk.id),
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "metadata": chunk.chunk_metadata,
            }
            for chunk in document.chunks
        ],
    }


@router.delete("/{document_id}")
def delete_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    filename = document.filename

    db.delete(document)
    db.commit()

    return {
        "message": "Document deleted successfully",
        "document_id": str(document_id),
        "filename": filename,
    }