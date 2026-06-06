from fastapi import APIRouter, Depends

from app.core.security import CurrentUser, require_user
from app.db.supabase_client import get_supabase_admin

router = APIRouter(prefix="/history", tags=["history"])
supabase = get_supabase_admin()


@router.get("/conversations")
async def conversation_history(
    user: CurrentUser = Depends(require_user),
    subject: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    q: str | None = None,
):
    query = supabase.table("conversations").select("*").eq("user_id", user.user_id)
    if subject:
        query = query.eq("subject", subject)
    if start_date:
        query = query.gte("created_at", start_date)
    if end_date:
        query = query.lte("created_at", end_date)
    if q:
        query = query.ilike("title", f"%{q}%")
    return query.order("created_at", desc=True).execute().data or []


@router.get("/export")
async def export_full_history(user: CurrentUser = Depends(require_user)):
    conversations = (
        supabase.table("conversations")
        .select("id,title,subject,created_at")
        .eq("user_id", user.user_id)
        .order("created_at", desc=True)
        .execute()
        .data
        or []
    )
    return {"count": len(conversations), "items": conversations}
