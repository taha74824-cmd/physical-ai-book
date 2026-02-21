from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from typing import Optional
import json
import uuid

from app.core.database import get_db
from app.models.chat import Conversation, Message
from app.services.rag import rag_service

router = APIRouter(prefix="/chat", tags=["chat"])


# --- Request/Response Models ---

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str
    selected_text: Optional[str] = None  # Text selected by the user in the book


class ChatResponse(BaseModel):
    conversation_id: str
    message_id: str
    answer: str
    sources: list[dict]


class ConversationListItem(BaseModel):
    id: str
    title: Optional[str]
    created_at: str
    message_count: int


# --- Endpoints ---

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Send a message to the RAG chatbot.
    Optionally include selected_text to ask about a specific passage.
    """
    # Get or create conversation
    if request.conversation_id:
        conv = await db.get(Conversation, request.conversation_id)
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conv = Conversation(id=str(uuid.uuid4()))
        db.add(conv)
        await db.flush()

    # Fetch conversation history
    history_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conv.id)
        .order_by(Message.created_at)
    )
    history = history_result.scalars().all()
    history_dicts = [{"role": m.role, "content": m.content} for m in history]

    # Generate answer via RAG
    answer, sources = await rag_service.generate_answer(
        question=request.message,
        conversation_history=history_dicts,
        selected_text=request.selected_text,
    )

    # Save user message
    user_msg = Message(
        conversation_id=conv.id,
        role="user",
        content=request.message,
        selected_text=request.selected_text,
    )
    db.add(user_msg)

    # Save assistant message
    assistant_msg = Message(
        conversation_id=conv.id,
        role="assistant",
        content=answer,
        sources=sources,
    )
    db.add(assistant_msg)
    await db.commit()

    # Set conversation title from first message
    if not conv.title and len(history) == 0:
        conv.title = request.message[:80]
        await db.commit()

    return ChatResponse(
        conversation_id=conv.id,
        message_id=assistant_msg.id,
        answer=answer,
        sources=sources,
    )


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Stream a RAG chatbot response (Server-Sent Events).
    """
    if request.conversation_id:
        conv = await db.get(Conversation, request.conversation_id)
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conv = Conversation(id=str(uuid.uuid4()))
        db.add(conv)
        await db.flush()
        await db.commit()

    history_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conv.id)
        .order_by(Message.created_at)
    )
    history = history_result.scalars().all()
    history_dicts = [{"role": m.role, "content": m.content} for m in history]

    # Save user message immediately
    user_msg = Message(
        conversation_id=conv.id,
        role="user",
        content=request.message,
        selected_text=request.selected_text,
    )
    db.add(user_msg)
    await db.commit()

    async def generate():
        full_answer = []
        sources = []
        conversation_id = conv.id

        # Send conversation_id first
        yield f"data: {json.dumps({'type': 'conversation_id', 'data': conversation_id})}\n\n"

        async for chunk in rag_service.stream_answer(
            question=request.message,
            conversation_history=history_dicts,
            selected_text=request.selected_text,
        ):
            if chunk["type"] == "sources":
                sources = chunk["data"]
                yield f"data: {json.dumps({'type': 'sources', 'data': sources})}\n\n"
            elif chunk["type"] == "text":
                full_answer.append(chunk["data"])
                yield f"data: {json.dumps({'type': 'text', 'data': chunk['data']})}\n\n"
            elif chunk["type"] == "done":
                # Save assistant message
                async with db:
                    assistant_msg = Message(
                        conversation_id=conversation_id,
                        role="assistant",
                        content="".join(full_answer),
                        sources=sources,
                    )
                    db.add(assistant_msg)
                    await db.commit()

                yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/conversations", response_model=list[ConversationListItem])
async def list_conversations(
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """List recent conversations."""
    result = await db.execute(
        select(Conversation)
        .order_by(desc(Conversation.created_at))
        .limit(limit)
    )
    conversations = result.scalars().all()

    items = []
    for conv in conversations:
        msg_result = await db.execute(
            select(Message).where(Message.conversation_id == conv.id)
        )
        msg_count = len(msg_result.scalars().all())
        items.append(
            ConversationListItem(
                id=conv.id,
                title=conv.title,
                created_at=str(conv.created_at),
                message_count=msg_count,
            )
        )

    return items


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get all messages in a conversation."""
    conv = await db.get(Conversation, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()

    return [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "selected_text": m.selected_text,
            "sources": m.sources,
            "created_at": str(m.created_at),
        }
        for m in messages
    ]


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a conversation and all its messages."""
    conv = await db.get(Conversation, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    await db.delete(conv)
    await db.commit()
    return {"message": "Conversation deleted"}
