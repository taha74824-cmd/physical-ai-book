from openai import AsyncOpenAI
from app.core.config import settings
from app.services.vector_store import vector_store
import logging

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an AI assistant for the book "Physical AI: From Perception to Action".
You help readers understand concepts about Physical AI, including robotics, machine learning,
computer vision, NLP for robotics, sim-to-real transfer, embodied AI, humanoid robots,
safety, ethics, and the future of Physical AI.

Answer questions based on the provided context from the book. If the context doesn't contain
enough information to answer the question, say so clearly and suggest what chapter might
have the relevant information.

Be educational, clear, and precise. Use examples when helpful. Format your answers
with markdown when appropriate (headings, bullet points, code blocks).

IMPORTANT: Base your answers on the provided context. Do not make up information."""

SELECTED_TEXT_PROMPT = """You are an AI assistant for the book "Physical AI: From Perception to Action".
The user has selected specific text from the book and wants to ask a question about it.

Selected text from the book:
---
{selected_text}
---

Answer the user's question about this selected text. Use the additional context provided
to give a comprehensive answer. Be educational and precise."""


class RAGService:
    def __init__(self):
        self.openai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def generate_answer(
        self,
        question: str,
        conversation_history: list[dict],
        selected_text: str = None,
    ) -> tuple[str, list[dict]]:
        """
        Generate a RAG-powered answer.

        Returns:
            (answer_text, source_documents)
        """
        # If there's selected text, use it as part of the search query
        search_query = question
        if selected_text:
            search_query = f"{selected_text}\n\n{question}"

        # Retrieve relevant context from vector store
        sources = await vector_store.search(
            query=search_query,
            top_k=settings.RAG_TOP_K,
        )

        # Build context from retrieved chunks
        context_parts = []
        for i, source in enumerate(sources, 1):
            context_parts.append(
                f"[Source {i} - {source['title']} ({source['chapter']})]\n{source['text']}"
            )
        context = "\n\n---\n\n".join(context_parts)

        # Build messages for OpenAI
        if selected_text:
            system_content = SELECTED_TEXT_PROMPT.format(selected_text=selected_text)
        else:
            system_content = SYSTEM_PROMPT

        if context:
            system_content += f"\n\nRELEVANT BOOK CONTENT:\n{context}"

        messages = [{"role": "system", "content": system_content}]

        # Add conversation history (last 6 exchanges for context window management)
        for msg in conversation_history[-12:]:
            messages.append({"role": msg["role"], "content": msg["content"]})

        # Add the current question
        messages.append({"role": "user", "content": question})

        # Generate response
        response = await self.openai.chat.completions.create(
            model=settings.OPENAI_CHAT_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=1500,
        )

        answer = response.choices[0].message.content
        return answer, sources

    async def stream_answer(
        self,
        question: str,
        conversation_history: list[dict],
        selected_text: str = None,
    ):
        """
        Stream a RAG-powered answer token by token.
        Yields chunks of text.
        """
        search_query = question
        if selected_text:
            search_query = f"{selected_text}\n\n{question}"

        sources = await vector_store.search(
            query=search_query,
            top_k=settings.RAG_TOP_K,
        )

        context_parts = []
        for i, source in enumerate(sources, 1):
            context_parts.append(
                f"[Source {i} - {source['title']} ({source['chapter']})]\n{source['text']}"
            )
        context = "\n\n---\n\n".join(context_parts)

        if selected_text:
            system_content = SELECTED_TEXT_PROMPT.format(selected_text=selected_text)
        else:
            system_content = SYSTEM_PROMPT

        if context:
            system_content += f"\n\nRELEVANT BOOK CONTENT:\n{context}"

        messages = [{"role": "system", "content": system_content}]
        for msg in conversation_history[-12:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": question})

        # Yield sources metadata first as a special chunk
        yield {"type": "sources", "data": sources}

        # Stream the response
        async with await self.openai.chat.completions.create(
            model=settings.OPENAI_CHAT_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=1500,
            stream=True,
        ) as stream:
            async for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield {"type": "text", "data": delta.content}

        yield {"type": "done", "data": None}


rag_service = RAGService()
