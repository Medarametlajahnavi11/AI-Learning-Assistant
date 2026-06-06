from collections.abc import AsyncIterator
from datetime import date

from openai import AsyncOpenAI

from app.core.config import settings
from app.db.supabase_client import get_supabase_admin
from app.services.chat.prompt_builder import build_system_prompt
from app.services.rag.embedding_service import EmbeddingService
from app.services.rag.retrieval_service import RetrievalService


class ChatService:
    def __init__(self) -> None:
        self.supabase = get_supabase_admin()
        
        if settings.chat_provider.lower() == "groq":
            self.llm_client = AsyncOpenAI(
                api_key=settings.groq_api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            self.model = settings.groq_model
        else:
            self.llm_client = AsyncOpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url
            )
            self.model = settings.openai_model

        self.embedding_service = EmbeddingService()
        self.retrieval_service = RetrievalService()

    async def stream_reply(
        self,
        user_id: str,
        conversation_id: str,
        message: str,
        subject: str,
        learning_level: str,
        explanation_style: str,
        learning_mode: str,
    ) -> AsyncIterator[str]:
        context_chunks: list[dict] = []
        if learning_mode == "Knowledge Vault":
            query_vector = (await self.embedding_service.embed([message]))[0]
            context_chunks = self.retrieval_service.search(user_id, query_vector, k=8)

        system_prompt = build_system_prompt(
            learning_level=learning_level,
            subject=subject,
            explanation_style=explanation_style,
            learning_mode=learning_mode,
            context_chunks=context_chunks,
        )

        self.supabase.table("messages").insert(
            {
                "conversation_id": conversation_id,
                "user_id": user_id,
                "role": "user",
                "content": message,
                "context_chunks": context_chunks,
            }
        ).execute()

        stream = await self.llm_client.chat.completions.create(
            model=self.model,
            stream=True,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
            temperature=0.4,
        )

        output_parts: list[str] = []
        async for chunk in stream:
            token = chunk.choices[0].delta.content or ""
            if token:
                output_parts.append(token)
                yield token

        answer = "".join(output_parts).strip()
        if answer:
            self.supabase.table("messages").insert(
                {
                    "conversation_id": conversation_id,
                    "user_id": user_id,
                    "role": "assistant",
                    "content": answer,
                    "context_chunks": context_chunks,
                }
            ).execute()

            self._update_analytics(user_id=user_id, learning_mode=learning_mode, subject=subject)

    def _update_analytics(self, user_id: str, learning_mode: str, subject: str) -> None:
        today = date.today().isoformat()
        record_resp = self.supabase.table("learning_analytics").select("*").eq("user_id", user_id).eq("date_key", today).limit(1).execute()
        existing = (record_resp.data or [None])[0]
        if not existing:
            payload = {
                "user_id": user_id,
                "date_key": today,
                "questions_asked": 1,
                "vault_usage_count": 1 if learning_mode == "Knowledge Vault" else 0,
                "global_usage_count": 1 if learning_mode == "Global Scholar" else 0,
                "topics_covered": [subject],
                "xp_earned": 10,
            }
            self.supabase.table("learning_analytics").insert(payload).execute()
            return

        topics = list(set(existing.get("topics_covered", []) + [subject]))
        self.supabase.table("learning_analytics").update(
            {
                "questions_asked": existing.get("questions_asked", 0) + 1,
                "vault_usage_count": existing.get("vault_usage_count", 0)
                + (1 if learning_mode == "Knowledge Vault" else 0),
                "global_usage_count": existing.get("global_usage_count", 0)
                + (1 if learning_mode == "Global Scholar" else 0),
                "topics_covered": topics,
                "xp_earned": existing.get("xp_earned", 0) + 10,
            }
        ).eq("id", existing["id"]).execute()
