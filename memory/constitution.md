# Project Constitution
## Physical AI Interactive Textbook

**Created:** 2026-02-21
**Status:** Active
**Project:** Physical AI: From Perception to Action — RAG-powered Docusaurus textbook

---

## Article I — Library-First Principle

Every backend service must be implemented as a self-contained module before being wired into the API. The RAG service, vector store operations, and ingestion pipeline are each standalone Python modules before they become FastAPI endpoints.

## Article II — Interface Mandate

All backend services expose clean REST/SSE HTTP interfaces. The frontend chatbot communicates exclusively through documented API contracts. No direct database calls from the frontend.

## Article III — Test-First Imperative

Acceptance criteria and API contracts are defined before implementation. The spec.md and contracts/ documents define success before a single line of code is written.

## Article IV — Simplicity Gate

The project is limited to exactly 3 deployable components:
1. Docusaurus book (static site → GitHub Pages)
2. FastAPI RAG backend (Python → Railway/Render)
3. External services (OpenAI, Qdrant, Neon — not self-hosted)

No additional services, no microservice sprawl.

## Article V — Anti-Abstraction Principle

Use framework-native patterns directly:
- FastAPI dependency injection, not custom DI containers
- Docusaurus built-in theming, not custom CSS frameworks
- OpenAI SDK directly, not wrapper libraries
- Qdrant Python client directly, not abstraction layers

## Article VI — Integration-First Testing

Tests validate real integrations:
- RAG chatbot answers questions using real Qdrant vector search
- Selected text flows correctly from frontend to backend context
- Ingestion pipeline actually embeds and stores documents

## Article VII — Content Quality Principle

Every chapter in the book must:
- Be substantive (minimum 500 words)
- Include at least one code example in Python
- Cover Physical AI topics accurately
- Be structured with H2/H3 headings for RAG chunking quality

## Article VIII — User Experience Principle

The chatbot must:
- Respond within 3 seconds for streaming to start
- Show source citations for every answer
- Support selected-text context (highlight → ask AI)
- Be non-intrusive (floating button, not blocking content)

## Article IX — Deployment Principle

Every component must be accessible via public URL:
- Book: GitHub Pages (`https://USERNAME.github.io/physical-ai-book/`)
- Backend: Cloud platform with public HTTPS URL
- No localhost-only demos for submission
