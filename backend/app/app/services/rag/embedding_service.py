from typing import List

from huggingface_hub import InferenceClient
from openai import AsyncOpenAI

from app.app.core.config import settings


class EmbeddingService:
    def __init__(self) -> None:
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.hf_client = InferenceClient(
            token=settings.huggingface_api_key,
        )
        self.local_model = None
        
        if settings.embedding_provider.lower() == "local":
            try:
                from sentence_transformers import SentenceTransformer
                print(f"Loading local embedding model: {settings.embedding_model}")
                self.local_model = SentenceTransformer(settings.embedding_model)
            except ImportError:
                print("sentence-transformers not installed. Install with: pip install sentence-transformers")
                raise

    async def embed(self, texts: List[str]) -> List[list[float]]:
        if settings.embedding_provider.lower() == "local":
            return await self._embed_local(texts)
        elif settings.embedding_provider.lower() == "huggingface":
            return await self._embed_huggingface(texts)

        response = await self.openai_client.embeddings.create(
            model=settings.embedding_model,
            input=texts,
        )
        return [item.embedding for item in response.data]

    async def _embed_local(self, texts: List[str]) -> List[list[float]]:
        """Embed texts using a local sentence-transformers model"""
        if not self.local_model:
            raise RuntimeError("Local embedding model not initialized")
        
        # Run in threadpool to avoid blocking
        import asyncio
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None,
            self.local_model.encode,
            texts,
            False  # convert_to_tensor=False
        )
        
        return [embedding.tolist() if hasattr(embedding, "tolist") else list(embedding) for embedding in embeddings]

    async def _embed_huggingface(self, texts: List[str]) -> List[list[float]]:
        # InferenceClient.feature_extraction is synchronous in huggingface_hub, 
        # but we can wrap it if needed or use it directly as it's typically fast.
        # For large batches, it's better to run in a threadpool or use an async client.
        
        results = []
        for text in texts:
            embedding = self.hf_client.feature_extraction(
                text,
                model=settings.embedding_model,
            )
            results.append(embedding.tolist() if hasattr(embedding, "tolist") else embedding)
        
        return results
