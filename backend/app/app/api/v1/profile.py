from fastapi import APIRouter, Depends, HTTPException

from app.core.security import CurrentUser, require_user
from app.db.supabase_client import get_supabase_admin
from app.schemas.profile import ProfileResponse, ProfileUpdatePayload

router = APIRouter(prefix="/profile", tags=["profile"])
supabase = get_supabase_admin()


@router.get("", response_model=ProfileResponse)
async def get_profile(user: CurrentUser = Depends(require_user)) -> ProfileResponse:
    response = supabase.table("user_profiles").select("*").eq("user_id", user.user_id).limit(1).execute()
    data = (response.data or [None])[0]
    if not data:
        raise HTTPException(status_code=404, detail="Profile not found")
    return ProfileResponse(**data)


@router.put("", response_model=ProfileResponse)
async def update_profile(payload: ProfileUpdatePayload, user: CurrentUser = Depends(require_user)) -> ProfileResponse:
    supabase.table("user_profiles").update(payload.model_dump()).eq("user_id", user.user_id).execute()
    response = supabase.table("user_profiles").select("*").eq("user_id", user.user_id).limit(1).execute()
    data = (response.data or [None])[0]
    if not data:
        raise HTTPException(status_code=404, detail="Profile not found")
    return ProfileResponse(**data)
