# API Contracts

## POST /api/v1/chat/stream

**Description:** Send a chat message, receive streaming SSE response with RAG context

**Request Body:**
```json
{
  "message": "What is sim-to-real transfer?",
  "conversation_id": "uuid-optional",
  "selected_text": "optional highlighted text from book"
}
```

**Response:** Server-Sent Events stream
```
data: {"type": "token", "content": "Sim-to-real"}
data: {"type": "token", "content": " transfer is..."}
data: {"type": "sources", "sources": [{"chapter": "Chapter 6", "section": "Sim-to-Real Gap", "excerpt": "..."}]}
data: {"type": "done", "conversation_id": "uuid"}
```

---

## POST /api/v1/chat/

**Description:** Non-streaming chat (full response)

**Request Body:** same as /stream

**Response:**
```json
{
  "message": "Full answer text...",
  "conversation_id": "uuid",
  "sources": [{"chapter": "Chapter 6", "section": "...", "excerpt": "..."}]
}
```

---

## POST /api/v1/admin/ingest

**Description:** Ingest book markdown files into Qdrant vector store

**Request Body:**
```json
{
  "docs_path": "C:/path/to/book/docs",
  "clear_existing": false
}
```

**Response:**
```json
{
  "status": "success",
  "chunks_ingested": 142,
  "documents_processed": 10
}
```

---

## GET /api/v1/admin/health/vector-store

**Response:**
```json
{
  "status": "healthy",
  "collection": "physical_ai_book",
  "vectors_count": 142
}
```
