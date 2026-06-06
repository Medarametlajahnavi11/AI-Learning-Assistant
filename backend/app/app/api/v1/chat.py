import datetime as dt
import json
import uuid
from typing import AsyncIterator

import bleach
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.app.core.security import CurrentUser, require_user
from app.app.db.supabase_client import get_supabase_admin
from app.app.schemas.chat import ChatRequest, CreateConversationRequest
from app.app.services.chat.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])
supabase = get_supabase_admin()
service = ChatService()


@router.post("/conversations")
async def create_conversation(payload: CreateConversationRequest, user: CurrentUser = Depends(require_user)):
    conv_id = str(uuid.uuid4())
    supabase.table("conversations").insert(
        {
            "id": conv_id,
            "user_id": user.user_id,
            "title": payload.title,
            "subject": payload.subject,
            "learning_level": payload.learning_level,
            "explanation_style": payload.explanation_style,
            "learning_mode": payload.learning_mode,
        }
    ).execute()
    return {"conversation_id": conv_id}


@router.post("/stream")
async def stream_chat(payload: ChatRequest, user: CurrentUser = Depends(require_user)):
    conversation_id = payload.conversation_id or str(uuid.uuid4())
    if not payload.conversation_id:
        supabase.table("conversations").insert(
            {
                "id": conversation_id,
                "user_id": user.user_id,
                "title": payload.message[:60],
                "subject": payload.subject,
                "learning_level": payload.learning_level,
                "explanation_style": payload.explanation_style,
                "learning_mode": payload.learning_mode,
            }
        ).execute()

    clean_message = bleach.clean(payload.message, strip=True)

    async def event_stream() -> AsyncIterator[str]:
        yield f"data: {json.dumps({'type': 'meta', 'conversation_id': conversation_id})}\n\n"
        async for token in service.stream_reply(
            user_id=user.user_id,
            conversation_id=conversation_id,
            message=clean_message,
            subject=payload.subject,
            learning_level=payload.learning_level,
            explanation_style=payload.explanation_style,
            learning_mode=payload.learning_mode,
        ):
            yield f"data: {json.dumps({'type': 'token', 'value': token})}\n\n"

        yield f"data: {json.dumps({'type': 'done', 'at': dt.datetime.utcnow().isoformat()})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/conversations")
async def list_conversations(user: CurrentUser = Depends(require_user), q: str | None = None):
    query = supabase.table("conversations").select("*").eq("user_id", user.user_id).order("updated_at", desc=True)
    if q:
        query = query.ilike("title", f"%{q}%")
    response = query.execute()
    return response.data or []


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(conversation_id: str, user: CurrentUser = Depends(require_user)):
    response = (
        supabase.table("messages")
        .select("*")
        .eq("conversation_id", conversation_id)
        .eq("user_id", user.user_id)
        .order("created_at", desc=False)
        .execute()
    )
    return response.data or []


@router.get("/conversations/{conversation_id}/export")
async def export_conversation(conversation_id: str, user: CurrentUser = Depends(require_user)):
    messages = (
        supabase.table("messages")
        .select("role, content, created_at")
        .eq("conversation_id", conversation_id)
        .eq("user_id", user.user_id)
        .order("created_at", desc=False)
        .execute()
    ).data or []

    lines = [f"# Conversation {conversation_id}"]
    for msg in messages:
        lines.append(f"\n## {msg['role'].title()} ({msg['created_at']})\n")
        lines.append(msg["content"])

    return {"conversation_id": conversation_id, "markdown": "\n".join(lines)}
