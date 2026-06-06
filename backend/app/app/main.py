from fastapi import FastAPI, Security
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware

from app.app.api.v1.router import api_router
from app.app.core.config import settings
from app.app.core.rate_limit import limiter
from app.app.core.security import get_current_user

app = FastAPI(title=settings.app_name)

# Configure CORS - Must be added BEFORE other middleware
cors_origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
if settings.app_env != "production":
    # Add common local dev origins
    if "http://localhost:5173" not in cors_origins:
        cors_origins.append("http://localhost:5173")
    if "http://localhost:3000" not in cors_origins:
        cors_origins.append("http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "app": settings.app_name}


@app.get("/debug/auth")
async def debug_auth(user: dict = Security(get_current_user)):
    """Debug endpoint to test authentication"""
    return {
        "status": "authenticated",
        "user_id": user.user_id,
        "email": user.email
    }


app.include_router(api_router)
