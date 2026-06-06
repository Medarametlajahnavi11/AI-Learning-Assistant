from fastapi import FastAPI, Security
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.rate_limit import limiter
from app.core.security import get_current_user

app = FastAPI(title=settings.app_name)

# Configure CORS
cors_origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]

# Add Vercel and local origins explicitly
extra_origins = [
    "https://ai-learning-assistant-zeta-five.vercel.app",
    "http://localhost:5173",
    "http://localhost:3000"
]
for origin in extra_origins:
    if origin not in cors_origins:
        cors_origins.append(origin)

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
