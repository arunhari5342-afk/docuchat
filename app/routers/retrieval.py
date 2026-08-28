from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.retrieval import retrieve_similar_chunks


router = APIRouter(
    prefix="/search",
    tags=["Search"],
)


@router.get("")
def search_documents(
    query: str = Query(..., min_length=1),
    top_k: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
):
    results = retrieve_similar_chunks(
        db=db,
        query=query,
        top_k=top_k,
    )

    return {
        "query": query,
        "results": [
            {
                "chunk_id": str(row["chunk_id"]),
                "document_id": str(row["document_id"]),
                "chunk_index": row["chunk_index"],
                "content": row["content"],
                "filename": row["filename"],
                "distance": float(row["distance"]),
            }
            for row in results
        ],
    }