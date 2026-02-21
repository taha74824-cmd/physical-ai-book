from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    SearchRequest,
)
from openai import AsyncOpenAI
from app.core.config import settings
import uuid
import logging

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self):
        self.client = AsyncQdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
        )
        self.openai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.collection = settings.QDRANT_COLLECTION_NAME

    async def ensure_collection(self):
        """Create collection if it doesn't exist."""
        collections = await self.client.get_collections()
        names = [c.name for c in collections.collections]

        if self.collection not in names:
            await self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(
                    size=settings.OPENAI_EMBEDDING_DIMENSIONS,
                    distance=Distance.COSINE,
                ),
            )
            logger.info(f"Created Qdrant collection: {self.collection}")

    async def embed_text(self, text: str) -> list[float]:
        """Generate embedding for a text chunk."""
        response = await self.openai.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input=text,
        )
        return response.data[0].embedding

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts efficiently."""
        response = await self.openai.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input=texts,
        )
        return [item.embedding for item in response.data]

    async def upsert_chunks(self, chunks: list[dict]) -> int:
        """
        Insert document chunks into the vector store.
        Each chunk: {"text": str, "metadata": dict}
        """
        await self.ensure_collection()

        texts = [chunk["text"] for chunk in chunks]
        embeddings = await self.embed_batch(texts)

        points = []
        for chunk, embedding in zip(chunks, embeddings):
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "text": chunk["text"],
                    "source": chunk["metadata"].get("source", "unknown"),
                    "chapter": chunk["metadata"].get("chapter", "unknown"),
                    "title": chunk["metadata"].get("title", ""),
                    "chunk_index": chunk["metadata"].get("chunk_index", 0),
                },
            )
            points.append(point)

        await self.client.upsert(
            collection_name=self.collection,
            points=points,
        )

        logger.info(f"Upserted {len(points)} chunks into Qdrant")
        return len(points)

    async def search(
        self,
        query: str,
        top_k: int = None,
        chapter_filter: str = None,
    ) -> list[dict]:
        """
        Search for relevant chunks given a query.
        Returns list of {text, source, chapter, score}.
        """
        top_k = top_k or settings.RAG_TOP_K
        query_embedding = await self.embed_text(query)

        search_filter = None
        if chapter_filter:
            search_filter = Filter(
                must=[
                    FieldCondition(
                        key="chapter",
                        match=MatchValue(value=chapter_filter),
                    )
                ]
            )

        results = await self.client.search(
            collection_name=self.collection,
            query_vector=query_embedding,
            limit=top_k,
            query_filter=search_filter,
            score_threshold=settings.RAG_SIMILARITY_THRESHOLD,
        )

        return [
            {
                "text": hit.payload.get("text", ""),
                "source": hit.payload.get("source", ""),
                "chapter": hit.payload.get("chapter", ""),
                "title": hit.payload.get("title", ""),
                "score": hit.score,
            }
            for hit in results
        ]

    async def delete_collection(self):
        """Delete the entire collection (use carefully)."""
        await self.client.delete_collection(self.collection)
        logger.warning(f"Deleted Qdrant collection: {self.collection}")


# Singleton
vector_store = VectorStore()
