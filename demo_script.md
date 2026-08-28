# DocuChat — 5-Minute Demo Script

## 1. Introduction — 30 seconds

Good morning.

My final project is **DocuChat**, a RAG-powered conversational chat application.

The purpose of DocuChat is to allow users to upload documents and ask questions about their content.

Instead of relying only on the LLM's existing knowledge, DocuChat retrieves relevant information from the uploaded documents and uses that information to generate grounded answers.

---

## 2. Architecture — 45 seconds

The application follows the Retrieval-Augmented Generation pipeline.

The flow is:

Document Upload
→ Text/PDF Extraction
→ Chunking
→ Embedding Generation
→ PostgreSQL + pgvector
→ Semantic Retrieval
→ Context Assembly
→ Groq LLM
→ Grounded Answer
→ Conversation History

FastAPI is used for the backend API.

PostgreSQL stores application data, documents, chunks, conversations, and messages.

pgvector stores the document embeddings and performs similarity search.

Sentence Transformers generates embeddings.

Groq provides the LLM used for answer generation.

SQLAlchemy is used for database interaction.

---

## 3. Document Upload Demo — 45 seconds

First, I upload a document.

DocuChat supports TXT and PDF files.

When a document is uploaded, the application:

1. Saves the physical file.
2. Extracts the document text.
3. Splits the text into smaller chunks.
4. Generates an embedding for each chunk.
5. Stores the document and chunks in PostgreSQL.
6. Stores the embeddings using pgvector.

I can verify that the document and its chunks have been stored successfully.

---

## 4. Semantic Retrieval Demo — 45 seconds

Next, I ask a question about the uploaded document.

For example:

"What is the Indus Valley Civilization?"

The application converts the question into an embedding.

It then performs a vector similarity search against the stored document embeddings.

The most relevant chunks are returned based on their distance.

These retrieved chunks become the context for the LLM.

---

## 5. Grounded Generation Demo — 45 seconds

The retrieved document chunks are passed to the LLM together with the user's question.

The prompt instructs the model to use only the provided document context.

The LLM then generates the answer.

The response also includes the source document, chunk ID, document ID, and similarity distance.

This makes the answer traceable to the uploaded document.

---

## 6. Conversational Chat Demo — 45 seconds

DocuChat also supports multi-turn conversations.

For example, I can first ask:

"What is DocuChat?"

Then I can ask:

"What does it use to store the embeddings?"

The second question depends on the previous conversation.

DocuChat retrieves the conversation history and provides it to the LLM so that follow-up questions can be understood correctly.

Each user and assistant message is persisted in PostgreSQL.

---

## 7. Error Handling Demo — 30 seconds

DocuChat also handles cases where an answer cannot be found.

For example:

"What is the capital of France?"

If the uploaded documents do not contain the answer, DocuChat responds:

"I could not find the answer in the uploaded documents."

This prevents the application from intentionally generating unsupported answers.

The API also validates empty queries and unsupported document types.

---

## 8. Database Architecture — 30 seconds

The main database tables are:

- users
- documents
- document_chunks
- conversations
- messages

A document can contain multiple document chunks.

A conversation can contain multiple messages.

Document chunks contain the text, metadata, and vector embedding.

Messages contain the conversation ID, role, content, and source metadata.

---

## 9. Technologies Used — 20 seconds

The main technologies used are:

- Python
- FastAPI
- PostgreSQL
- pgvector
- SQLAlchemy
- Sentence Transformers
- Groq
- Docker
- Pydantic

---

## 10. Conclusion — 25 seconds

DocuChat demonstrates a complete RAG application from document ingestion to conversational generation.

The project implements:

- Document ingestion
- Text and PDF extraction
- Chunking
- Embedding generation
- Vector storage
- Semantic retrieval
- Grounded generation
- Source tracking
- Conversation memory
- API validation
- Evaluation
- PostgreSQL persistence

This completes the DocuChat RAG pipeline and provides a foundation for a production-style document question-answering application.
