from fastapi import APIRouter

from app.api.v1 import auth, chat, dashboard, documents, history, profile

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(profile.router)
api_router.include_router(documents.router)
api_router.include_router(chat.router)
api_router.include_router(history.router)
api_router.include_router(dashboard.router)
