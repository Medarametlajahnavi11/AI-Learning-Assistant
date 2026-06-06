from fastapi import APIRouter, Depends

from app.app.core.security import CurrentUser, require_user
from app.app.db.supabase_client import get_supabase_admin

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
supabase = get_supabase_admin()


@router.get("/overview")
async def dashboard_overview(user: CurrentUser = Depends(require_user)):
    profile = supabase.table("user_profiles").select("xp_points, learning_streak").eq("user_id", user.user_id).limit(1).execute().data
    docs = supabase.table("uploaded_documents").select("document_id", count="exact").eq("user_id", user.user_id).execute().count or 0
    messages = supabase.table("messages").select("id", count="exact").eq("user_id", user.user_id).eq("role", "user").execute().count or 0
    analytics = supabase.table("learning_analytics").select("*").eq("user_id", user.user_id).order("date_key", desc=True).limit(7).execute().data or []

    latest_profile = (profile or [{"xp_points": 0, "learning_streak": 0}])[0]
    all_topics = set()
    vault_usage = 0
    global_usage = 0
    for row in analytics:
        all_topics.update(row.get("topics_covered", []))
        vault_usage += row.get("vault_usage_count", 0)
        global_usage += row.get("global_usage_count", 0)

    return {
        "questions_asked": messages,
        "documents_uploaded": docs,
        "learning_streak": latest_profile.get("learning_streak", 0),
        "subjects_learned": len(all_topics),
        "total_xp": latest_profile.get("xp_points", 0),
        "vault_usage_count": vault_usage,
        "global_usage_count": global_usage,
        "weekly": analytics,
    }
