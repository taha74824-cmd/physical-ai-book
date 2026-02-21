---
id: "001"
title: "Hackathon Full Deployment"
stage: general
date: "2026-02-21"
surface: agent
model: claude-sonnet-4-6
feature: physical-ai-rag-textbook
branch: main
user: taha74824-cmd
command: "hackathon 1 - full project setup and deployment"
labels: ["deployment", "hackathon", "spec-driven", "rag", "docusaurus", "railway", "github-pages"]
links:
  spec: "specs/001-physical-ai-rag-textbook/spec.md"
  plan: "specs/001-physical-ai-rag-textbook/plan.md"
  tasks: "specs/001-physical-ai-rag-textbook/tasks.md"
  adr: "null"
  pr: "null"
files_created:
  - memory/constitution.md
  - specs/001-physical-ai-rag-textbook/spec.md
  - specs/001-physical-ai-rag-textbook/plan.md
  - specs/001-physical-ai-rag-textbook/tasks.md
  - specs/001-physical-ai-rag-textbook/contracts/api.md
  - specs/001-physical-ai-rag-textbook/checklists/requirements.md
  - backend/Procfile
  - backend/railway.json
  - backend/runtime.txt
  - history/prompts/general/001-hackathon-full-deployment.general.prompt.md
files_modified:
  - book/docusaurus.config.ts
  - book/src/components/ChatBot/index.tsx
  - backend/requirements.txt
  - backend/.env.example
  - backend/app/services/vector_store.py
tests_run:
  - "curl GET https://physical-ai-book-production-c6d2.up.railway.app/ → 200 OK"
  - "curl GET https://physical-ai-book-production-c6d2.up.railway.app/api/v1/admin/health/vector-store → healthy, 1 collection"
  - "curl POST /api/v1/chat/ with 'What is embodied AI?' → correct RAG answer with sources"
  - "curl GET https://taha74824-cmd.github.io/physical-ai-book/ → 200 OK"
  - "Local RAG test: 58 chunks ingested, answers with chapter citations"
---

## Prompt

hackathon 1 — build a textbook hackathon project with:
1. AI/Spec-Driven Book Creation using Docusaurus deployed to GitHub Pages, using Spec-Kit Plus
2. Integrated RAG Chatbot using OpenAI, FastAPI, Neon Serverless Postgres, Qdrant Cloud
Requirements: spec-driven development, public GitHub repo, published book link, chatbot embedded

User is non-techie, needs full guidance. GitHub username: taha74824-cmd

## Response Summary

Full project deployed end-to-end in one session:

### Spec-Kit Plus Setup
- Installed `specifyplus` via pip
- Ran `sp init . --ai claude --ignore-agent-tools`
- Created all SDD artifacts: constitution.md, spec.md, plan.md, tasks.md, contracts/api.md, checklists/requirements.md

### Backend Fixes Applied
- Upgraded qdrant-client 1.13.2 → 1.17.0 (server compatibility)
- Fixed DATABASE_URL: `sslmode=require` → `ssl=require` (asyncpg format)
- Fixed vector search: `client.search()` → `client.query_points()` (new API)
- Removed broken nixpacks.toml, let Railway auto-detect Python

### Deployments
- Book: https://taha74824-cmd.github.io/physical-ai-book/ ✅
- Backend: https://physical-ai-book-production-c6d2.up.railway.app ✅
- GitHub: https://github.com/taha74824-cmd/physical-ai-book ✅

### RAG System
- 58 chunks ingested from 10 chapters into Qdrant Cloud
- Live test confirmed: answers "What is embodied AI?" with correct chapter citation
- Neon Postgres storing conversation history

## Outcome

COMPLETE — all hackathon requirements met:
- ✅ Docusaurus book on GitHub Pages
- ✅ Spec-Kit Plus SDD artifacts
- ✅ RAG chatbot with OpenAI + Qdrant + Neon
- ✅ Selected-text-to-chatbot feature
- ✅ SSE streaming responses
- ✅ Source citations
- ✅ FastAPI backend on Railway
