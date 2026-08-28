from app.core.database import SessionLocal
from app.services.retrieval import retrieve_similar_chunks
from app.services.llm import generate_answer


TEST_CASES = [
    "What is DocuChat?",
    "What does it use to store the embeddings?",
    "Explain the Indus Valley Civilization.",
    "What is the capital of France?",
    "Tell me something that is not mentioned in the uploaded documents.",
]


def run_evaluation():
    db = SessionLocal()

    try:
        for index, query in enumerate(TEST_CASES, start=1):
            print("=" * 80)
            print(f"TEST CASE {index}")
            print(f"QUESTION: {query}")
            print("-" * 80)

            results = retrieve_similar_chunks(
                db=db,
                query=query,
                top_k=3,
            )

            if not results:
                print("RESULT: NO CONTEXT FOUND")
                continue

            context = "\n\n".join(
                result["content"]
                for result in results
            )

            answer = generate_answer(
                query=query,
                context=context,
            )

            print("ANSWER:")
            print(answer)

            print("-" * 80)
            print("SOURCES:")

            for result in results:
                print(
                    f"- {result['filename']} | "
                    f"chunk={result['chunk_index']} | "
                    f"distance={result['distance']:.4f}"
                )

    finally:
        db.close()


if __name__ == "__main__":
    run_evaluation()
