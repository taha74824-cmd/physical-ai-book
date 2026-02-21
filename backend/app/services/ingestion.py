"""
Document ingestion service.
Reads Docusaurus markdown files and ingests them into Qdrant.
"""
import os
import re
import logging
from pathlib import Path
from langchain_text_splitters import MarkdownTextSplitter, RecursiveCharacterTextSplitter
from app.services.vector_store import vector_store
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.chat import Document

logger = logging.getLogger(__name__)


def extract_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter from markdown."""
    frontmatter = {}
    body = content

    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            fm_text = content[3:end].strip()
            body = content[end + 3:].strip()

            for line in fm_text.split("\n"):
                if ":" in line:
                    key, _, value = line.partition(":")
                    frontmatter[key.strip()] = value.strip().strip('"\'')

    return frontmatter, body


def chunk_markdown(text: str, chunk_size: int = None, chunk_overlap: int = None) -> list[str]:
    """Split markdown text into chunks."""
    chunk_size = chunk_size or settings.CHUNK_SIZE
    chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n## ", "\n### ", "\n#### ", "\n\n", "\n", " "],
    )
    return splitter.split_text(text)


def get_chapter_from_path(filepath: str) -> str:
    """Extract chapter name from file path."""
    parts = Path(filepath).parts
    for part in parts:
        if part.startswith("chapter-"):
            return part
    return "unknown"


async def ingest_markdown_file(
    filepath: str,
    db: AsyncSession,
) -> int:
    """
    Ingest a single markdown file into the vector store.
    Returns number of chunks created.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    frontmatter, body = extract_frontmatter(content)
    title = frontmatter.get("title", Path(filepath).stem)
    chapter = get_chapter_from_path(filepath)

    # Remove code blocks to avoid confusing the vector search
    body_clean = re.sub(r"```[\s\S]*?```", "[code example]", body)

    chunks = chunk_markdown(body_clean)
    if not chunks:
        logger.warning(f"No chunks generated from {filepath}")
        return 0

    chunk_data = [
        {
            "text": chunk,
            "metadata": {
                "source": str(filepath),
                "chapter": chapter,
                "title": title,
                "chunk_index": i,
            },
        }
        for i, chunk in enumerate(chunks)
    ]

    count = await vector_store.upsert_chunks(chunk_data)

    # Record in database
    doc = Document(
        title=title,
        source_path=str(filepath),
        chunk_count=count,
        metadata_={"chapter": chapter, "frontmatter": frontmatter},
    )
    db.add(doc)
    await db.commit()

    logger.info(f"Ingested {filepath}: {count} chunks")
    return count


async def ingest_book(docs_path: str, db: AsyncSession) -> dict:
    """
    Ingest the entire Docusaurus book.
    Returns summary of ingestion.
    """
    docs_path = Path(docs_path)
    if not docs_path.exists():
        raise ValueError(f"Docs path does not exist: {docs_path}")

    # Find all markdown files
    md_files = list(docs_path.rglob("*.md")) + list(docs_path.rglob("*.mdx"))

    total_chunks = 0
    ingested_files = []
    failed_files = []

    for md_file in md_files:
        try:
            count = await ingest_markdown_file(str(md_file), db)
            total_chunks += count
            ingested_files.append(str(md_file))
        except Exception as e:
            logger.error(f"Failed to ingest {md_file}: {e}")
            failed_files.append({"file": str(md_file), "error": str(e)})

    return {
        "total_files": len(md_files),
        "ingested": len(ingested_files),
        "failed": len(failed_files),
        "total_chunks": total_chunks,
        "failed_files": failed_files,
    }
