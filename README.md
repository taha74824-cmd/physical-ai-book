# Physical AI: From Perception to Action

> A comprehensive RAG-powered textbook on Physical AI, built with Docusaurus and deployed to GitHub Pages.

---

## Project Structure

```
physical-ai-book/
├── book/                          # Docusaurus site (the book)
│   ├── docs/                      # Book chapters (Markdown)
│   │   ├── chapter-01-introduction/
│   │   ├── chapter-02-foundations/
│   │   ├── chapter-03-machine-learning/
│   │   ├── chapter-04-computer-vision/
│   │   ├── chapter-05-nlp-robotics/
│   │   ├── chapter-06-sim-to-real/
│   │   ├── chapter-07-embodied-ai/
│   │   ├── chapter-08-humanoid-robots/
│   │   ├── chapter-09-safety-ethics/
│   │   └── chapter-10-future/
│   ├── src/
│   │   ├── components/ChatBot/    # RAG Chatbot React component
│   │   ├── pages/index.tsx        # Homepage
│   │   └── theme/Root.tsx         # Global chatbot injection
│   └── docusaurus.config.ts
│
├── backend/                       # FastAPI RAG backend
│   ├── app/
│   │   ├── api/routes/
│   │   │   ├── chat.py            # Chat endpoints (SSE streaming)
│   │   │   └── admin.py           # Document ingestion endpoints
│   │   ├── core/
│   │   │   ├── config.py          # Settings from .env
│   │   │   └── database.py        # SQLAlchemy + Neon Postgres
│   │   ├── models/chat.py         # DB models (Conversation, Message, Document)
│   │   ├── services/
│   │   │   ├── rag.py             # RAG service (OpenAI + Qdrant)
│   │   │   ├── vector_store.py    # Qdrant operations
│   │   │   └── ingestion.py       # Document chunking + embedding
│   │   └── main.py                # FastAPI app
│   ├── requirements.txt
│   └── .env.example               # Environment variable template
│
└── .github/workflows/deploy.yml   # GitHub Actions deployment
```

---

## Quick Start

### Step 1: Get Your API Keys

You need accounts and keys from:

| Service | URL | What for |
|---------|-----|----------|
| OpenAI | https://platform.openai.com/api-keys | Chat + Embeddings |
| Qdrant Cloud | https://cloud.qdrant.io/ | Vector database (free tier) |
| Neon | https://neon.tech/ | Serverless Postgres (free tier) |

### Step 2: Set Up the Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your API keys (see instructions below)

# Start the server
uvicorn app.main:app --reload --port 8000
```

The API will be at `http://localhost:8000`
Interactive docs at `http://localhost:8000/docs`

### Step 3: Ingest the Book Content

Once the backend is running, call the ingestion endpoint to load the book into Qdrant:

```bash
curl -X POST "http://localhost:8000/api/v1/admin/ingest" \
  -H "Content-Type: application/json" \
  -d '{"docs_path": "C:/Users/Lenovo T480 i5 8th/Desktop/Taha Saeed Hackhaton/book/docs", "clear_existing": false}'
```

Or open `http://localhost:8000/docs` and use the interactive Swagger UI.

### Step 4: Run the Book Locally

```bash
cd book

# Install dependencies
npm install

# Start development server
npm start
```

Open `http://localhost:3000` — you'll see the book with the floating AI chatbot!

---

## Environment Variables Reference

Copy `backend/.env.example` to `backend/.env` and fill in:

```env
# OpenAI (required)
OPENAI_API_KEY=sk-...

# Qdrant Cloud (required)
QDRANT_URL=https://your-cluster.cloud.qdrant.io
QDRANT_API_KEY=your-key

# Neon PostgreSQL (required)
DATABASE_URL=postgresql+asyncpg://user:pass@host/db?sslmode=require

# Optional settings
OPENAI_CHAT_MODEL=gpt-4o-mini        # or gpt-4o for better quality
QDRANT_COLLECTION_NAME=physical_ai_book
RAG_TOP_K=5                          # Number of chunks to retrieve
```

---

## Deploy to GitHub Pages

### Step 1: Create a GitHub Repository

1. Go to https://github.com/new
2. Create a repo named `physical-ai-book`
3. Make it Public

### Step 2: Update Configuration

In `book/docusaurus.config.ts`, replace:
```
YOUR_GITHUB_USERNAME  →  your actual GitHub username
```

### Step 3: Enable GitHub Pages

In your GitHub repo:
1. Go to **Settings** → **Pages**
2. Set Source to **GitHub Actions**

### Step 4: Push to GitHub

```bash
# Initialize git (run from project root)
git init
git add .
git commit -m "Initial commit: Physical AI Book"
git remote add origin https://github.com/YOUR_USERNAME/physical-ai-book.git
git push -u origin main
```

The GitHub Action will automatically build and deploy your book.

Your book will be live at: `https://YOUR_USERNAME.github.io/physical-ai-book/`

---

## Deploy the Backend

For production, deploy the FastAPI backend to any cloud provider:

### Option A: Railway (Easiest)
1. Connect your GitHub repo at https://railway.app
2. Add a Python service pointing to the `backend` folder
3. Set environment variables in Railway dashboard
4. Railway auto-deploys on push

### Option B: Render
1. Create a Web Service at https://render.com
2. Build command: `pip install -r requirements.txt`
3. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Set environment variables

### Option C: Fly.io
```bash
cd backend
fly launch
fly secrets set OPENAI_API_KEY=sk-...
fly deploy
```

### After Deploying

Update `book/src/components/ChatBot/index.tsx`:
```tsx
const API_URL =
  process.env.NODE_ENV === "production"
    ? "https://YOUR-BACKEND.railway.app/api/v1"   // ← Replace this
    : "http://localhost:8000/api/v1";
```

Also update `ALLOWED_ORIGINS` in your backend `.env`:
```env
ALLOWED_ORIGINS=["https://YOUR_USERNAME.github.io"]
```

---

## Features

### RAG Chatbot
- **Streaming responses** via Server-Sent Events
- **Source citations** — see which book passage answered your question
- **Conversation history** — maintains context across messages
- **Stored in Neon Postgres** — all conversations persisted

### Select Text to Ask
- Highlight any text in the book
- Click "Ask AI about this" tooltip
- The chatbot uses the selected passage as context

### Book Content
- 10 comprehensive chapters on Physical AI
- Python code examples throughout
- Tables, diagrams, and structured content
- Dark/light mode support

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/chat/` | Send message, get full response |
| POST | `/api/v1/chat/stream` | Send message, get SSE stream |
| GET | `/api/v1/chat/conversations` | List conversations |
| GET | `/api/v1/chat/conversations/{id}/messages` | Get messages |
| POST | `/api/v1/admin/ingest` | Ingest book into Qdrant |
| GET | `/api/v1/admin/documents` | List ingested documents |
| GET | `/api/v1/admin/health/vector-store` | Check Qdrant health |

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Book frontend | Docusaurus 3 (React + TypeScript) |
| AI chatbot UI | Custom React + CSS Modules |
| Backend API | FastAPI (Python) |
| LLM + Embeddings | OpenAI (gpt-4o-mini + text-embedding-3-small) |
| Vector database | Qdrant Cloud (free tier) |
| Relational DB | Neon Serverless Postgres |
| Deployment | GitHub Pages (book) + Railway/Render (backend) |
| CI/CD | GitHub Actions |
