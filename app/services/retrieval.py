from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.embedding import generate_embedding


SIMILARITY_THRESHOLD = 0.6


def retrieve_similar_chunks(
    db: Session,
    query: str,
    top_k: int = 3,
):
    query_embedding = generate_embedding(query)

    sql = text(
        """
        SELECT
            dc.id AS chunk_id,
            dc.document_id,
            dc.chunk_index,
            dc.content,
            d.filename,
            dc.embedding <=> CAST(:query_embedding AS vector) AS distance
        FROM document_chunks dc
        JOIN documents d
            ON d.id = dc.document_id
        WHERE dc.embedding <=> CAST(:query_embedding AS vector) <= :threshold
        ORDER BY dc.embedding <=> CAST(:query_embedding AS vector)
        LIMIT :top_k
        """
    )

    result = db.execute(
        sql,
        {
            "query_embedding": str(query_embedding),
            "top_k": top_k,
            "threshold": SIMILARITY_THRESHOLD,
        },
    )

    rows = result.mappings().all()

    return [dict(row) for row in rows]