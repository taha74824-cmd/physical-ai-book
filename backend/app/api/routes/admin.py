"""
Admin endpoints for document ingestion and management.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
import os

from app.core.database import get_db
from app.models.chat import Document
from app.services.ingestion import ingest_book, ingest_markdown_file
from app.services.vector_store import vector_store

router = APIRouter(prefix="/admin", tags=["admin"])


class IngestRequest(BaseModel):
    docs_path: str
    clear_existing: bool = False


class IngestResponse(BaseModel):
    total_files: int
    ingested: int
    failed: int
    total_chunks: int
    failed_files: list[dict]


@router.post("/ingest", response_model=IngestResponse)
async def ingest_documents(
    request: IngestRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Ingest all markdown files from the Docusaurus docs directory.
    Call this endpoint after deploying to populate the vector store.
    """
    if not os.path.exists(request.docs_path):
        raise HTTPException(
            status_code=400,
            detail=f"Path does not exist: {request.docs_path}"
        )

    if request.clear_existing:
        await vector_store.delete_collection()

    result = await ingest_book(request.docs_path, db)
    return IngestResponse(**result)


@router.post("/ingest/file")
async def ingest_single_file(
    filepath: str,
    db: AsyncSession = Depends(get_db),
):
    """Ingest a single markdown file."""
    if not os.path.exists(filepath):
        raise HTTPException(status_code=400, detail=f"File not found: {filepath}")

    count = await ingest_markdown_file(filepath, db)
    return {"chunks_created": count, "file": filepath}


@router.get("/documents")
async def list_documents(db: AsyncSession = Depends(get_db)):
    """List all ingested documents."""
    result = await db.execute(select(Document))
    docs = result.scalars().all()

    return [
        {
            "id": d.id,
            "title": d.title,
            "source_path": d.source_path,
            "chunk_count": d.chunk_count,
            "indexed_at": str(d.indexed_at),
        }
        for d in docs
    ]


@router.delete("/documents/all")
async def clear_all_documents(db: AsyncSession = Depends(get_db)):
    """Clear all documents from vector store and database."""
    await vector_store.delete_collection()

    result = await db.execute(select(Document))
    docs = result.scalars().all()
    for doc in docs:
        await db.delete(doc)
    await db.commit()

    return {"message": "All documents cleared"}


@router.get("/health/vector-store")
async def vector_store_health():
    """Check Qdrant connection."""
    try:
        collections = await vector_store.client.get_collections()
        return {
            "status": "healthy",
            "collections": [c.name for c in collections.collections],
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
