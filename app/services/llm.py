from openai import OpenAI

from app.core.config import settings


client = OpenAI(
    api_key=settings.groq_api_key,
    base_url="https://api.groq.com/openai/v1",
)


def generate_answer(
    query: str,
    context: str,
    history: str = "",
) -> str:

    prompt = f"""
You are DocuChat, an AI assistant that answers questions using
information retrieved from the user's documents.

Use ONLY the provided document context to answer the question.

Conversation history may help you understand references such as:
"it", "they", "that", "this", or follow-up questions.

However, conversation history is only for understanding the user's
question. The actual answer must come ONLY from the provided document
context.

If the answer cannot be found in the document context, say exactly:

"I could not find the answer in the uploaded documents."

Do not invent, assume, or use outside knowledge.

Conversation history:
{history}

Document context:
{context}

Current question:
{query}
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You answer questions using only the provided "
                    "document context."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        max_tokens=1000,
        temperature=0.2,
    )

    content = response.choices[0].message.content

    if not content:
        return "I could not generate an answer."

    return content.strip()