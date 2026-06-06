from fastapi import APIRouter, HTTPException, status

from app.app.schemas.auth import AuthResponse, LoginPayload, SignUpPayload
from app.app.services.auth.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])
service = AuthService()


@router.post("/signup", response_model=AuthResponse)
async def signup(payload: SignUpPayload) -> AuthResponse:
    try:
        auth_data = service.signup(
            email=payload.account.email,
            password=payload.account.password,
            metadata={"full_name": payload.account.full_name},
        )
        service.save_profile_and_preferences(
            auth_data["user_id"],
            {
                "full_name": payload.account.full_name,
                "learning_level": payload.learning.learning_level,
                "preferred_explanation_style": payload.preferences.preferred_explanation_style,
                "preferred_learning_mode": payload.preferences.preferred_learning_mode,
                "subjects": payload.preferences.subjects,
            },
        )
        return AuthResponse(
            user_id=auth_data["user_id"],
            access_token=auth_data["access_token"],
            refresh_token=auth_data["refresh_token"],
            requires_confirmation=auth_data["requires_confirmation"],
        )
    except Exception as exc:
        print(f"Signup error details: {str(exc)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginPayload) -> AuthResponse:
    try:
        auth_data = service.login(payload.email, payload.password)
        return AuthResponse(
            user_id=auth_data["user_id"],
            access_token=auth_data["access_token"],
            refresh_token=auth_data["refresh_token"],
        )
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
