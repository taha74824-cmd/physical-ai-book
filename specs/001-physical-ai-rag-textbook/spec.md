# Feature Specification: Physical AI RAG Textbook

**Feature Branch:** 001-physical-ai-rag-textbook
**Created:** 2026-02-21
**Status:** Approved
**Author:** Taha Saeed (via /sp.specify)

---

## Input Description

Build a publicly accessible interactive textbook about Physical AI (robotics, embodied AI, perception, and autonomous systems) that:
- Teaches Physical AI through 10 structured chapters
- Embeds an AI chatbot powered by RAG (Retrieval-Augmented Generation) so readers can ask questions about the book content
- Supports "select text → ask AI" interaction so readers can highlight any passage and immediately ask the chatbot about it
- Persists conversation history in a database
- Is deployed publicly on GitHub Pages (book) with a cloud backend (chatbot API)

---

## User Scenarios & Testing

### P1 — Reader Asks a Question About Book Content

**Description:** A reader is studying Chapter 3 (Machine Learning for Physical AI) and doesn't understand a concept. They open the floating chat button, type their question, and receive a streaming answer that cites the relevant section of the book.

**Priority Justification:** This is the core value proposition — the entire chatbot exists for this scenario.

**Acceptance Scenarios:**

- **Given** the book is open on any chapter page
  **When** the reader clicks the floating chat button and types "What is sim-to-real transfer?"
  **Then** the chatbot streams a response within 3 seconds AND the response includes a source citation linking to the relevant chapter

- **Given** the chatbot has answered a question
  **When** the reader asks a follow-up question
  **Then** the chatbot uses conversation history as context (not just the new question)

- **Given** the backend is down
  **When** the reader sends a message
  **Then** the chatbot displays a friendly error message (not a blank screen)

**Edge Cases:**
- Question about a topic not covered in the book → chatbot says "This topic isn't covered in this book" rather than hallucinating
- Very long question (>500 chars) → truncated gracefully
- Network timeout → user sees retry option

---

### P2 — Reader Uses "Select Text → Ask AI"

**Description:** A reader highlights a dense paragraph about computer vision in Chapter 4. A tooltip appears. They click "Ask AI about this" and the chatbot opens pre-loaded with that passage as context, ready for a focused question.

**Priority Justification:** This is the differentiating UX feature that makes the book interactive, not just a static site with a generic chatbot.

**Acceptance Scenarios:**

- **Given** the reader highlights text on any page
  **When** the selection tooltip appears and they click "Ask AI about this"
  **Then** the chatbot panel opens with the selected text visible as context

- **Given** the chatbot has pre-loaded selected text context
  **When** the reader types a question
  **Then** the chatbot uses both the selected passage AND the vector-search results to answer

- **Given** the reader selects text and opens the chatbot
  **When** they clear the chatbot and start a new conversation
  **Then** the selected text context is cleared and normal Q&A resumes

**Edge Cases:**
- Selected text is only whitespace → tooltip does not appear
- Selected text is extremely long (>1000 chars) → truncated to 500 chars with user notification

---

### P3 — Reader Browses the Book

**Description:** A reader opens the book URL and can navigate through all 10 chapters using the sidebar, read well-structured content with code examples, and the chatbot is always available as a floating button without interrupting reading.

**Priority Justification:** Core book usability — the content must be readable and navigable before the chatbot adds value.

**Acceptance Scenarios:**

- **Given** the book URL is opened
  **When** the homepage loads
  **Then** the title "Physical AI: From Perception to Action" is visible and all 10 chapters are listed

- **Given** the reader is on any chapter
  **When** they look at the sidebar
  **Then** all 10 chapters are listed and the current chapter is highlighted

- **Given** the reader is reading
  **When** they look for the chatbot
  **Then** the floating button is visible in the bottom-right corner and does NOT cover book content

---

## Functional Requirements

- **FR-001** The Docusaurus site MUST serve all 10 chapters at public GitHub Pages URL
- **FR-002** Each chapter MUST contain substantive content (>500 words) with Python code examples
- **FR-003** The floating chatbot button MUST appear on every page of the book
- **FR-004** The chatbot MUST use RAG: retrieve relevant chunks from Qdrant before generating an answer
- **FR-005** The chatbot MUST stream responses via Server-Sent Events (SSE)
- **FR-006** The chatbot MUST display source citations (chapter name + section) for each answer
- **FR-007** Selected text MUST be passed as additional context to the RAG query
- **FR-008** All conversations MUST be stored in Neon Postgres (conversation_id, messages, timestamps)
- **FR-009** The backend MUST expose a `/api/v1/admin/ingest` endpoint to load book content into Qdrant
- **FR-010** The backend MUST run as a deployed HTTPS service (not localhost)
- **FR-011** CORS MUST be configured to allow requests from the GitHub Pages domain

---

## Key Entities

### Book Chapter
- Chapter number (1-10)
- Title
- Content (Markdown)
- Sections (H2/H3 headings)
- Code examples

### Vector Chunk
- chunk_id
- source_document (chapter name)
- content (text segment, ~500 tokens)
- embedding (1536-dim vector, text-embedding-3-small)
- metadata (chapter number, section title)

### Conversation
- conversation_id (UUID)
- created_at
- messages: list of Message

### Message
- message_id
- conversation_id (FK)
- role (user | assistant)
- content
- sources (JSON array of citations)
- created_at

---

## Success Criteria

- **SC-001** Book is publicly accessible at `https://USERNAME.github.io/physical-ai-book/`
- **SC-002** All 10 chapters load without errors
- **SC-003** Chatbot answers a question about any chapter within 5 seconds (streaming start)
- **SC-004** Selected-text context is correctly injected into the RAG query
- **SC-005** Conversation history is retrievable from the Postgres database
- **SC-006** Qdrant vector store contains embeddings for all book chapters after ingestion
- **SC-007** Backend is accessible via public HTTPS URL with working `/docs` Swagger page
