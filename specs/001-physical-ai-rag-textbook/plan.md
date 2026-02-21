# Implementation Plan: Physical AI RAG Textbook

**Feature:** 001-physical-ai-rag-textbook
**Created:** 2026-02-21
**Status:** Approved
**Technology Choices:** Docusaurus 3 + FastAPI + OpenAI + Qdrant + Neon Postgres

---

## Technology Stack

| Layer | Technology | Rationale |
|---|---|---|
| Book frontend | Docusaurus 3 (React + TypeScript) | Required by hackathon spec. Static site → GitHub Pages deploy via Actions |
| Chatbot UI | Custom React component (CSS Modules) | Embedded in Docusaurus, floating overlay pattern |
| Backend API | FastAPI (Python 3.11+) | Required by hackathon spec. Async, auto Swagger docs, SSE support |
| LLM | OpenAI gpt-4o-mini | Required by hackathon spec. Cost-effective, high quality |
| Embeddings | OpenAI text-embedding-3-small | 1536-dim, pairs with gpt-4o-mini |
| Vector DB | Qdrant Cloud Free Tier | Required by hackathon spec. Free, hosted, Python client |
| Relational DB | Neon Serverless Postgres | Required by hackathon spec. Free tier, serverless, asyncpg |
| Book deploy | GitHub Pages via GitHub Actions | Required by hackathon spec |
| Backend deploy | Railway (primary) or Render (fallback) | Free tier, auto-deploy from GitHub, env var support |
| Spec framework | Spec-Kit Plus (specifyplus) | Required by hackathon spec |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Reader's Browser                       │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │         Docusaurus Book (GitHub Pages)            │   │
│  │  ┌────────────────────────────────────────────┐  │   │
│  │  │  Chapter Content (MDX)                     │  │   │
│  │  │  ┌──────────────────────────────────────┐  │  │   │
│  │  │  │  FloatingChatBot Component           │  │  │   │
│  │  │  │  - Text selection tooltip            │  │  │   │
│  │  │  │  - Chat panel (SSE streaming)        │  │  │   │
│  │  │  └──────────────────────────────────────┘  │  │   │
│  │  └────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                            │ HTTPS/SSE
                            ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend (Railway/Render)             │
│                                                          │
│  POST /api/v1/chat/stream                                │
│  POST /api/v1/admin/ingest                               │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  RAG Service │  │ Vector Store │  │  Ingestion   │  │
│  │  (rag.py)   │  │ (qdrant)     │  │  Service     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────────┐
│   OpenAI     │   │ Qdrant Cloud │   │  Neon Postgres   │
│  (chat +     │   │  (vectors)   │   │  (conversations) │
│  embeddings) │   │              │   │                  │
└──────────────┘   └──────────────┘   └──────────────────┘
```

---

## Implementation Phases

### Phase 0: Spec-Kit Plus Setup [DONE]
- [x] Install specifyplus
- [x] Run `sp init . --ai claude --ignore-agent-tools`
- [x] Create constitution.md
- [x] Create spec.md
- [x] Create plan.md (this file)

### Phase 1: Docusaurus Book Content
**Goal:** 10 chapters with real, substantive content deployed to GitHub Pages

- [ ] Verify/enhance all 10 chapter files (>500 words + code examples each)
- [ ] Update `docusaurus.config.ts` with correct GitHub username
- [ ] Create GitHub repository (`physical-ai-book`)
- [ ] Initialize git and push to GitHub
- [ ] Enable GitHub Pages in repo settings
- [ ] Verify book deploys and all chapters are accessible

### Phase 2: Backend Services Setup
**Goal:** FastAPI backend running locally and all services configured

- [ ] Create `backend/.env` with all API keys
- [ ] Install Python dependencies (`pip install -r requirements.txt`)
- [ ] Start backend locally (`uvicorn app.main:app --reload`)
- [ ] Verify `/docs` Swagger page works
- [ ] Run document ingestion (POST `/api/v1/admin/ingest`)
- [ ] Verify Qdrant has embeddings

### Phase 3: Integration Testing
**Goal:** Chatbot works end-to-end locally

- [ ] Test chat endpoint with a question about Physical AI
- [ ] Verify SSE streaming works
- [ ] Verify source citations are returned
- [ ] Verify conversation is stored in Neon Postgres

### Phase 4: Backend Deployment
**Goal:** FastAPI backend accessible at public HTTPS URL

- [ ] Deploy backend to Railway
- [ ] Set all environment variables in Railway dashboard
- [ ] Update ALLOWED_ORIGINS with GitHub Pages URL
- [ ] Test deployed API with curl

### Phase 5: Frontend → Backend Wiring
**Goal:** Deployed book talks to deployed backend

- [ ] Update `book/src/components/ChatBot/index.tsx` with production API URL
- [ ] Rebuild and redeploy Docusaurus
- [ ] End-to-end test on live GitHub Pages URL

### Phase 6: Polish & Submission
**Goal:** Everything works, looks good, ready to submit

- [ ] Test selected-text-to-chatbot flow
- [ ] Verify mobile responsiveness
- [ ] Complete tasks.md checkboxes
- [ ] Prepare GitHub repo link + book link for submission

---

## API Contracts

See `contracts/` directory.

---

## Gates

**Simplicity Gate:** ✅ Exactly 3 deployable components (book, backend, external services)
**Anti-Abstraction Gate:** ✅ Using FastAPI/OpenAI/Qdrant SDKs directly
**Integration-First Gate:** ✅ Tests validate real Qdrant search and real OpenAI responses
