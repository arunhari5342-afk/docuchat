from pathlib import Path
import uuid

from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.chunk import DocumentChunk
from app.services.ingestion.loader import load_document
from app.services.ingestion.chunker import split_text
from app.services.embedding import generate_embeddings


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


DEMO_USER_ID = uuid.UUID(
    "11111111-1111-1111-1111-111111111111"
)


def ingest_document(
    db: Session,
    filename: str,
    file_content: bytes,
) -> Document:

    # 1. Generate unique filename
    file_extension = Path(filename).suffix.lower()

    stored_filename = (
        f"{uuid.uuid4()}{file_extension}"
    )

    file_path = UPLOAD_DIR / stored_filename

    # 2. Save physical file
    file_path.write_bytes(file_content)

    # 3. Extract text
    text = load_document(str(file_path))

    if not text.strip():
        raise ValueError(
            "The uploaded document contains no readable text"
        )

    # 4. Split into chunks
    chunks = split_text(text)

    if not chunks:
        raise ValueError(
            "No chunks were generated from the document"
        )

    # 5. Generate embeddings
    embeddings = generate_embeddings(chunks)

    # 6. Create Document record
    document = Document(
        user_id=DEMO_USER_ID,
        filename=filename,
        file_type=file_extension,
        file_path=str(file_path),
        document_metadata={
            "chunk_count": len(chunks),
            "embedding_model": "all-MiniLM-L6-v2",
        },
    )

    db.add(document)
    db.flush()

    # 7. Create DocumentChunk records
    for index, (chunk_text, embedding) in enumerate(
        zip(chunks, embeddings)
    ):
        chunk = DocumentChunk(
            document_id=document.id,
            chunk_index=index,
            content=chunk_text,
            embedding=embedding,
            chunk_metadata={
                "source": filename,
                "chunk_index": index,
            },
        )

        db.add(chunk)

    # 8. Commit everything
    db.commit()

    # 9. Refresh document
    db.refresh(document)

    return document