from app.services.llm import client


response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "user",
            "content": (
                "Explain what the Indus Valley Civilization is "
                "in two sentences."
            ),
        }
    ],
    max_tokens=500,
    temperature=0.2,
)


print("FINISH REASON:")
print(response.choices[0].finish_reason)

print("\nMESSAGE:")
print(response.choices[0].message)

print("\nCONTENT:")
print(repr(response.choices[0].message.content))

print("\nUSAGE:")
print(response.usage)