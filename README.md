# DocuChat

DocuChat is a RAG-powered conversational chat application that allows users to upload documents, retrieve relevant information from those documents, and generate grounded answers using an LLM.

## Project Overview

DocuChat combines document ingestion, vector search, retrieval-augmented generation, and conversational memory into a single FastAPI application.

### Technologies Used

* Python
* FastAPI
* PostgreSQL
* pgvector
* SQLAlchemy
* Sentence Transformers
* Groq LLM
* Docker
* Pydantic Settings
* PyPDF

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
                Semantic Retrieval
                       |
                       v
              Relevant Document Chunks
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
              Conversation History
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

These vectors allow the application to compare the semantic meaning of a user's question with document chunks.

### 4. Vector Storage

Embeddings are stored in PostgreSQL using the `pgvector` extension.

The main vector column is:

```text
document_chunks.embedding
```

Similarity is calculated using the pgvector distance operator:

```sql
<=> 
```

### 5. Semantic Retrieval

When a user asks a question:

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
Sort By Similarity
      |
      v
Return Top-K Chunks
```

The application retrieves the most relevant document chunks.

### 6. Grounded Generation

The retrieved chunks are passed to the LLM as document context.

The model is instructed to:

* Use only the supplied document context.
* Avoid inventing information.
* Use conversation history only to understand follow-up questions.
* Return a fixed response when the answer cannot be found.

When no relevant answer is available, DocuChat returns:

```text
I could not find the answer in the uploaded documents.
```

### 7. Conversational Chat

DocuChat supports multi-turn conversations.

For example:

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

The second question can use the previous conversation context to understand what "it" refers to.

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
filename
file_type
file_path
metadata
created_at
user_id
```

### Document Chunks

Stores the individual text chunks and their embeddings.

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

The document is:

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

### Semantic Search

```http
GET /search?query=your question&top_k=5
```

Returns the most relevant document chunks.

Example:

```text
GET /search?query=What is DocuChat?&top_k=5
```

### Chat

```http
POST /chat
```

Generates a grounded answer using:

```text
Conversation History
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
DATABASE_URL=postgresql+psycopg://docuchat_user:docuchat_password@127.0.0.1:5434/docuchat

GROQ_API_KEY="your_groq_api_key"
```

Never commit the real `.env` file or API key to GitHub.

Use `.env.example` for sharing the required configuration structure.

## Running PostgreSQL

Docker Compose is used to run PostgreSQL with pgvector.

Start the database:

```powershell
docker compose up -d
```

Check running containers:

```powershell
docker ps
```

The PostgreSQL database is exposed locally through:

```text
127.0.0.1:5434
```

Database:

```text
docuchat
```

User:

```text
docuchat_user
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

The application will run at:

```text
http://127.0.0.1:8000
```

FastAPI Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## Testing

The project was tested using:

* FastAPI Swagger UI
* Python test scripts
* PostgreSQL queries
* Semantic retrieval tests
* RAG evaluation tests

### Retrieval Test

The retrieval pipeline successfully returned relevant chunks from:

```text
test.txt
IndusValleyCivilization.pdf
```

### Chat Test

Example:

```text
Question:
What is DocuChat?

Answer:
DocuChat is a RAG-powered chat application that lets users
upload documents, split the text into chunks, generate
embeddings, and store those embeddings in PostgreSQL
using pgvector.
```

### Follow-up Test

```text
Question:
What does it use to store the embeddings?

Answer:
It stores the embeddings in a PostgreSQL database using
the pgvector extension.
```

This verifies conversational context handling.

## Evaluation

The project includes evaluation cases covering:

1. Questions answered from uploaded documents.
2. Follow-up questions.
3. Questions about different uploaded documents.
4. Questions whose answers are not present.
5. Requests for information not contained in the documents.

Example out-of-context question:

```text
What is the capital of France?
```

Expected behavior:

```text
I could not find the answer in the uploaded documents.
```

This prevents the application from relying on unsupported outside information.

## Error Handling

DocuChat handles several invalid scenarios.

### Empty Query

An empty chat query is rejected.

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

The project considers the following RAG evaluation areas:

### Faithfulness

The generated answer should be supported by the retrieved document context.

### Answer Relevance

The answer should directly address the user's question.

### Context Relevance

Retrieved chunks should contain useful information for answering the question.

### Grounding

The LLM should not invent information that is absent from the uploaded documents.

## Security and Configuration

Sensitive configuration is stored using environment variables.

The API key is not hard-coded in application source code.

The `.env` file should remain excluded from Git.

Example:

```text
.env
```

should be included in `.gitignore`.

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
* Context assembly
* Grounded generation
* Conversational memory
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
        ---------------------
        |                   |
        v                   v
     Search               Chat
        |                   |
        v                   v
    Top-K Chunks      Conversation History
        |                   |
        -----------+---------
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

The recommended 5-minute demonstration is:

### Step 1 — Show Application

Open:

```text
http://127.0.0.1:8000/docs
```

### Step 2 — Upload Document

Upload a `.txt` or `.pdf` document.

### Step 3 — Verify Document

Call:

```http
GET /documents
```

Show the document and chunk count.

### Step 4 — Perform Retrieval

Ask:

```text
What is DocuChat?
```

using:

```http
GET /search
```

Show the retrieved chunk and similarity distance.

### Step 5 — Ask Chat Question

Use:

```http
POST /chat
```

Ask a question based on the uploaded document.

### Step 6 — Demonstrate Follow-Up

Ask a follow-up question such as:

```text
What does it use to store the embeddings?
```

Show that the conversation history allows the application to understand the reference.

### Step 7 — Demonstrate Guardrail

Ask something unrelated:

```text
What is the capital of France?
```

The application should respond:

```text
I could not find the answer in the uploaded documents.
```

## Conclusion

DocuChat is a complete RAG-based conversational application that connects document ingestion, semantic vector retrieval, grounded LLM generation, and multi-turn conversation through a FastAPI backend.

The project demonstrates how private document knowledge can be transformed into a searchable vector representation and used to generate answers that remain grounded in retrieved source content.
