# DocuChat

DocuChat is a RAG-powered conversational chat application that allows users to upload documents, retrieve relevant information from those documents, and generate grounded answers using an LLM.

## Project Overview

DocuChat combines document ingestion, vector search, retrieval-augmented generation, question rewriting, and conversational memory into a FastAPI application.

The application supports:

* TXT and PDF document uploads
* Text extraction
* Text chunking
* Embedding generation
* PostgreSQL + pgvector vector storage
* Semantic search
* Question rewriting for follow-up questions
* Context-aware conversational chat
* Grounded LLM generation
* Document listing, retrieval, and deletion
* RAG hallucination protection
* Conversation history
* Source tracking

## Technologies Used

* Python
* FastAPI
* PostgreSQL 17
* pgvector
* SQLAlchemy
* Sentence Transformers
* Groq API
* OpenAI Python SDK
* Docker
* Pydantic Settings
* PyPDF
* LangChain Text Splitters

## RAG Architecture

```text
                    Document Upload
                           |
                           v
                  TXT / PDF Extraction
                           |
                           v
                     Text Chunking
                           |
                           v
                 Embedding Generation
                           |
                           v
                  PostgreSQL + pgvector
                           |
                           v
                    Semantic Search
                           |
                           v
                  Relevant Chunks
                           |
                           v
                   Context Assembly
                           |
                           v
                      Groq LLM
                           |
                           v
                    Grounded Answer
```

## Conversational RAG Architecture

For follow-up questions, DocuChat uses conversation history and a question rewriter.

```text
                  User Question
                       |
                       v
               Conversation History
                       |
                       v
                Question Rewriter
                       |
                       v
              Standalone Question
                       |
                       v
              Query Embedding
                       |
                       v
             pgvector Retrieval
                       |
                       v
                Relevant Chunks
                       |
                       v
                Context Assembly
                       |
                       v
                    Groq LLM
                       |
                       v
                Grounded Answer
                       |
                       v
               Save Message to DB
                       |
                       v
                  Chat Response
```

## How DocuChat Works

### 1. Document Upload

Users can upload supported `.txt` and `.pdf` documents through the FastAPI API.

The application:

1. Receives the uploaded file.
2. Generates a unique stored filename.
3. Saves the physical file in the `uploads` directory.
4. Extracts readable text.
5. Splits the text into smaller chunks.
6. Generates embeddings for each chunk.
7. Stores the document and chunks in PostgreSQL.

### 2. Text Chunking

Large documents are divided into smaller chunks so that relevant sections can be retrieved efficiently.

Each chunk contains:

* Chunk ID
* Document ID
* Chunk index
* Text content
* Embedding
* Metadata

### 3. Embedding Generation

DocuChat uses the Sentence Transformers model:

```text
all-MiniLM-L6-v2
```

The model converts text into numerical vectors.

The generated embeddings have 384 dimensions:

```text
VECTOR(384)
```

These vectors allow the application to compare the semantic meaning of a user's question with document chunks.

### 4. Vector Storage

Embeddings are stored in PostgreSQL using the `pgvector` extension.

The main vector column is:

```text
document_chunks.embedding
```

The column is defined as:

```sql
embedding VECTOR(384)
```

Similarity is calculated using the pgvector distance operator:

```sql
<=>
```

### 5. Semantic Retrieval

When a user asks a question, DocuChat:

```text
User Question
      |
      v
Generate Query Embedding
      |
      v
Compare Against Document Embeddings
      |
      v
Calculate Vector Distance
      |
      v
Sort By Similarity
      |
      v
Return Top-K Chunks
```

The application retrieves the most semantically relevant document chunks.

The retrieval query uses:

```sql
ORDER BY dc.embedding <=> CAST(:query_embedding AS vector)
```

A smaller distance indicates greater similarity.

### 6. Question Rewriting

DocuChat supports follow-up questions that contain references such as:

```text
it
they
this
that
these
those
```

For example:

```text
User:
What technologies does DocuChat use?

Assistant:
DocuChat uses document ingestion, embeddings, pgvector,
semantic retrieval, and grounded generation.

User:
What does it use for semantic search?
```

The question rewriter converts the follow-up question into a standalone question:

```text
What does DocuChat use for semantic search?
```

The rewritten question is then converted into an embedding and used for semantic retrieval.

This improves retrieval for multi-turn conversations.

### 7. Grounded Generation

The retrieved chunks are passed to the LLM as document context.

The model is instructed to:

* Use only the supplied document context.
* Avoid inventing information.
* Use conversation history only to understand follow-up questions.
* Answer only from retrieved document information.
* Return a fixed response when the answer cannot be found.

When no relevant answer is available, DocuChat returns:

```text
I could not find the answer in the uploaded documents.
```

### 8. Conversational Chat

DocuChat supports multi-turn conversations.

Example:

```text
User:

What is DocuChat?

Assistant:

DocuChat is a RAG-powered chat application...

User:

What does it use to store the embeddings?

Assistant:

It stores the embeddings in PostgreSQL using pgvector.
```

The conversation history allows the question rewriter to understand what `"it"` refers to.

## Database Schema

DocuChat uses PostgreSQL with the following main tables:

```text
users
  |
  +---- documents
  |
  +---- conversations
              |
              +---- messages

documents
  |
  +---- document_chunks
```

### Users

Stores application users.

Important fields:

```text
id
email
password_hash
created_at
```

### Documents

Stores uploaded document information.

Important fields:

```text
id
user_id
filename
file_type
file_path
metadata
created_at
```

### Document Chunks

Stores individual text chunks and their embeddings.

Important fields:

```text
id
document_id
chunk_index
content
embedding
metadata
created_at
```

### Conversations

Stores chat sessions.

Important fields:

```text
id
user_id
title
created_at
updated_at
```

### Messages

Stores every user and assistant message.

Important fields:

```text
id
conversation_id
role
content
metadata
created_at
```

Assistant messages store retrieved source information in JSON metadata.

## API Endpoints

### Root

```http
GET /
```

Returns the application status.

### Health Check

```http
GET /health
```

Checks whether the application is running.

### Database Health

```http
GET /health/db
```

Checks the PostgreSQL connection.

Example response:

```json
{
  "status": "healthy",
  "database": "docuchat"
}
```

### Vector Health

```http
GET /health/vector
```

Checks whether the pgvector extension is available.

### Upload Document

```http
POST /documents/upload
```

Uploads and indexes a `.txt` or `.pdf` document.

The document processing pipeline is:

```text
Upload
   ↓
Save
   ↓
Extract
   ↓
Chunk
   ↓
Embed
   ↓
Store
```

### List Documents

```http
GET /documents
```

Returns uploaded documents and their chunk counts.

### Get Document

```http
GET /documents/{document_id}
```

Returns document details and its chunks.

### Delete Document

```http
DELETE /documents/{document_id}
```

Deletes a document and its related chunks.

Document chunks are automatically removed through the database foreign-key cascade.

### Semantic Search

```http
GET /search?query=your question&top_k=5
```

Returns the most relevant document chunks.

Example:

```http
GET /search?query=What is DocuChat?&top_k=5
```

Example response:

```json
{
  "query": "What is DocuChat?",
  "results": [
    {
      "chunk_id": "485f3221-f512-4ef9-b9da-f19c15cddfbf",
      "document_id": "937bcd74-2770-453c-8691-87eaaf9babf7",
      "chunk_index": 0,
      "content": "DocuChat is a RAG-powered chat application...",
      "filename": "test.txt",
      "distance": 0.2154
    }
  ]
}
```

### Chat

```http
POST /chat
```

Generates a grounded answer using:

```text
Conversation History
        +
Question Rewriting
        +
Semantic Retrieval
        +
Document Context
        +
Groq LLM
        =
Grounded Answer
```

Example request:

```json
{
  "query": "What is DocuChat?",
  "top_k": 3
}
```

Example response:

```json
{
  "conversation_id": "d79d0ca5-1e0a-4d9c-bd95-3bf4b130ef04",
  "query": "What is DocuChat?",
  "answer": "DocuChat is a RAG-powered chat application...",
  "sources": [
    {
      "chunk_id": "485f3221-f512-4ef9-b9da-f19c15cddfbf",
      "document_id": "937bcd74-2770-453c-8691-87eaaf9babf7",
      "filename": "test.txt",
      "distance": 0.2154
    }
  ]
}
```

## Project Structure

```text
docuchat/
│
├── app/
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── __init__.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── document.py
│   │   ├── chunk.py
│   │   ├── conversation.py
│   │   ├── message.py
│   │   └── __init__.py
│   │
│   ├── routers/
│   │   ├── documents.py
│   │   ├── retrieval.py
│   │   ├── conversations.py
│   │   ├── chat.py
│   │   └── __init__.py
│   │
│   ├── schemas/
│   │   ├── chat.py
│   │   └── __init__.py
│   │
│   ├── services/
│   │   ├── embedding.py
│   │   ├── retrieval.py
│   │   ├── llm.py
│   │   ├── question_rewriter.py
│   │   ├── __init__.py
│   │   │
│   │   └── ingestion/
│   │       ├── loader.py
│   │       ├── chunker.py
│   │       ├── service.py
│   │       └── __init__.py
│   │
│   ├── __init__.py
│   └── main.py
│
├── uploads/
│
├── docker-compose.yml
├── schema.sql
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Environment Variables

Create a `.env` file in the project root.

```env
DATABASE_URL=postgresql+psycopg://docuchat_user:docuchat_password@127.0.0.1:5432/docuchat

GROQ_API_KEY="your_groq_api_key"
```

Never commit the real `.env` file or API key to GitHub.

Use `.env.example` for sharing the required configuration structure.

Example `.gitignore` entry:

```text
.env
```

## PostgreSQL and pgvector

DocuChat uses PostgreSQL 17 with the pgvector extension.

Enable pgvector with:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Verify the extension:

```sql
SELECT extname, extversion
FROM pg_extension
WHERE extname = 'vector';
```

The application uses a 384-dimensional vector column:

```sql
embedding VECTOR(384)
```

## Running PostgreSQL

If PostgreSQL is configured through Docker Compose, start it with:

```powershell
docker compose up -d
```

Check running containers:

```powershell
docker ps
```

The application database configuration currently uses:

```text
Host: 127.0.0.1
Port: 5432
Database: docuchat
User: docuchat_user
```

## Running the Application

Activate the virtual environment:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Start FastAPI:

```powershell
uvicorn app.main:app --reload
```

The application runs at:

```text
http://127.0.0.1:8000
```

FastAPI Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## Requirements

The main Python dependencies are:

```text
fastapi==0.141.1
uvicorn==0.52.4
SQLAlchemy==2.0.52
psycopg==3.3.4
psycopg-binary==3.3.4
pgvector==0.5.0
pydantic==2.13.4
pydantic-settings==2.15.0
python-dotenv==1.2.3
pypdf==6.1.0
langchain-text-splitters
sentence-transformers
openai
```

## Testing

The project was tested using:

* FastAPI Swagger UI
* Python test scripts
* PostgreSQL queries
* Semantic retrieval tests
* RAG evaluation tests
* Follow-up question tests
* Hallucination protection tests

### Database Verification

After uploading a document, document records can be checked with:

```sql
SELECT * FROM documents;
```

Document chunks can be checked with:

```sql
SELECT * FROM document_chunks;
```

Verify embedding dimensions:

```sql
SELECT
    id,
    document_id,
    chunk_index,
    vector_dims(embedding) AS embedding_dimensions
FROM document_chunks;
```

Expected embedding dimension:

```text
384
```

Verify document chunk counts:

```sql
SELECT
    d.filename,
    COUNT(dc.id) AS chunk_count
FROM documents d
LEFT JOIN document_chunks dc
    ON d.id = dc.document_id
GROUP BY d.id, d.filename;
```

## Retrieval Test

The retrieval pipeline successfully returns relevant chunks from uploaded documents.

Example:

```text
============================================================
RESULT 1
Distance: 0.26260404213642696
Filename: test.txt
Chunk: 0
Content: DocuChat is a RAG powered chat application. It uses
document ingestion, embeddings, pgvector, semantic retrieval
and grounded generation.
```

## Chat Test

Example question:

```text
What technologies does DocuChat use?
```

Example answer:

```text
DocuChat uses document ingestion, embeddings, pgvector,
semantic retrieval, and grounded generation.
```

The response also includes the retrieved source chunk.

## Follow-Up Question Test

First question:

```text
What technologies does DocuChat use?
```

Follow-up question:

```text
What does it use for semantic search?
```

The question rewriter converts the follow-up into a standalone question before retrieval.

The system can then return an answer such as:

```text
It uses semantic retrieval for semantic search.
```

This verifies conversational context handling and question rewriting.

## Hallucination Protection Test

DocuChat is designed to avoid answering questions using unsupported outside knowledge.

Example:

```text
What is the capital of France?
```

Expected response:

```text
I could not find the answer in the uploaded documents.
```

The LLM is explicitly instructed to use only the retrieved document context.

## Evaluation

The project includes evaluation cases covering:

1. Questions answered from uploaded documents.
2. Follow-up questions.
3. Questions about different uploaded documents.
4. Questions whose answers are not present.
5. Requests for information not contained in the documents.
6. Question rewriting for conversational references.
7. Semantic retrieval quality.
8. Grounded answer generation.

## Error Handling

DocuChat handles several invalid scenarios.

### Empty Query

An empty chat query is rejected:

```text
Query cannot be empty.
```

### Unsupported File

Only the following file types are supported:

```text
.txt
.pdf
```

### Missing Document

If a requested document does not exist:

```text
Document not found
```

### No Relevant Context

If the answer cannot be found:

```text
I could not find the answer in the uploaded documents.
```

### Database Health

The application provides:

```text
/health/db
```

to verify PostgreSQL connectivity.

### Vector Health

The application provides:

```text
/health/vector
```

to verify the pgvector extension.

## RAG Evaluation Concepts

The project considers the following RAG evaluation areas.

### Faithfulness

The generated answer should be supported by the retrieved document context.

### Answer Relevance

The answer should directly address the user's question.

### Context Relevance

Retrieved chunks should contain useful information for answering the question.

### Grounding

The LLM should not invent information that is absent from the uploaded documents.

### Retrieval Quality

The retrieved chunks should be semantically related to the user's question.

### Question Rewriting Quality

Follow-up questions should be transformed into standalone questions without changing their intended meaning.

## Security and Configuration

Sensitive configuration is stored using environment variables.

The Groq API key is not hard-coded in application source code.

The `.env` file should remain excluded from Git.

Example:

```text
.env
```

should be included in `.gitignore`.

Use:

```text
.env.example
```

to document required environment variables without exposing secrets.

## Key Concepts Demonstrated

This project demonstrates practical understanding of:

* Artificial Intelligence
* Natural Language Processing
* Large Language Models
* Embeddings
* Vector databases
* pgvector
* Semantic search
* RAG
* Document ingestion
* Text extraction
* Text chunking
* Chunk overlap
* Metadata
* Top-K retrieval
* Similarity search
* Vector distance
* Context assembly
* Question rewriting
* Conversational memory
* Grounded generation
* Hallucination protection
* FastAPI
* PostgreSQL
* SQLAlchemy
* Docker
* API validation
* Error handling
* RAG evaluation

## Project Data Flow

```text
                         USER
                           |
                           v
                    Upload Document
                           |
                           v
                  Document Extraction
                           |
                           v
                       Chunking
                           |
                           v
                     Embeddings
                           |
                           v
                PostgreSQL + pgvector
                           |
                           |
              +------------+------------+
              |                         |
              v                         v
           Search                     Chat
              |                         |
              v                         v
        Query Embedding          Conversation History
              |                         |
              v                         v
        Top-K Chunks            Question Rewriter
              |                         |
              |                         v
              |                 Standalone Question
              |                         |
              |                         v
              |                  Semantic Retrieval
              |                         |
              +------------+------------+
                           |
                           v
                    Context Assembly
                           |
                           v
                        Groq LLM
                           |
                           v
                    Grounded Response
                           |
                           v
                   Save Message to DB
                           |
                           v
                         USER
```

## Final Project Goal

DocuChat demonstrates a complete production-style RAG workflow:

```text
Document Upload
       ↓
Document Processing
       ↓
Text Extraction
       ↓
Chunking
       ↓
Embedding Generation
       ↓
pgvector Storage
       ↓
Question Rewriting
       ↓
Semantic Retrieval
       ↓
Context Assembly
       ↓
Grounded LLM Generation
       ↓
Conversation Memory
       ↓
FastAPI Chat API
```

## Demo Flow

The recommended five-minute demonstration is:

### Step 1 — Show Application

Open:

```text
http://127.0.0.1:8000/docs
```

### Step 2 — Upload Document

Use:

```http
POST /documents/upload
```

Upload a `.txt` or `.pdf` document.

### Step 3 — Verify Document

Call:

```http
GET /documents
```

Show the document and chunk count.

### Step 4 — Perform Retrieval

Use:

```http
GET /search
```

Ask:

```text
What is DocuChat?
```

Show the retrieved chunk and vector distance.

### Step 5 — Ask Chat Question

Use:

```http
POST /chat
```

Ask a question based on the uploaded document.

### Step 6 — Demonstrate Follow-Up

Ask:

```text
What does it use to store the embeddings?
```

Show that conversation history and question rewriting allow the application to understand the reference.

### Step 7 — Demonstrate Guardrail

Ask an unrelated question:

```text
What is the capital of France?
```

The application should respond:

```text
I could not find the answer in the uploaded documents.
```

## Conclusion

DocuChat is a complete RAG-based conversational application that connects document ingestion, semantic vector retrieval, question rewriting, grounded LLM generation, and multi-turn conversation through a FastAPI backend.

The project demonstrates how private document knowledge can be transformed into searchable vector representations and used to generate answers that remain grounded in retrieved source content.

The application provides a practical implementation of a modern RAG pipeline:

```text
Ingestion
    ↓
Document Processing
    ↓
Chunking
    ↓
Embedding Generation
    ↓
pgvector Storage
    ↓
Question Rewriting
    ↓
Semantic Retrieval
    ↓
Context Assembly
    ↓
Grounded LLM Generation
    ↓
Conversation Memory
    ↓
FastAPI Chat API
```
