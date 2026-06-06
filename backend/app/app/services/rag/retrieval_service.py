from typing import Any

from app.app.db.supabase_client import get_supabase_admin


class RetrievalService:
    def __init__(self) -> None:
        self.supabase = get_supabase_admin()

    def search(self, user_id: str, query_embedding: list[float], k: int = 8) -> list[dict[str, Any]]:
        payload = {
            "p_user_id": user_id,
            "p_query_embedding": query_embedding,
            "p_match_count": k,
        }
        response = self.supabase.rpc("match_document_chunks", payload).execute()
        return response.data or []
