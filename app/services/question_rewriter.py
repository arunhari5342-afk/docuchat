from openai import OpenAI

from app.core.config import settings


client = OpenAI(
    api_key=settings.groq_api_key,
    base_url="https://api.groq.com/openai/v1",
)


def rewrite_question(
    query: str,
    history: str = "",
) -> str:
    """
    Convert a follow-up question into a standalone question
    using the previous conversation.
    """

    if not history.strip():
        return query

    prompt = f"""
You are a question rewriting component for a RAG system.

Your job is to rewrite the current user question into a
standalone question that can be used for document retrieval.

Use the conversation history to resolve references such as:
- it
- they
- them
- this
- that
- these
- those
- he
- she

Do NOT answer the question.

Do NOT add information that is not supported by the conversation.

If the current question is already standalone, return it unchanged.

Conversation history:
{history}

Current question:
{query}

Return ONLY the rewritten standalone question.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": (
                    "Rewrite questions for document retrieval. "
                    "Never answer the question."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        max_tokens=200,
        temperature=0,
    )

    content = response.choices[0].message.content

    if not content:
        return query

    return content.strip()