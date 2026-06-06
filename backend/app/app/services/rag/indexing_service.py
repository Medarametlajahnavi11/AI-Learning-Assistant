from app.db.supabase_client import get_supabase_admin
from app.services.rag.embedding_service import EmbeddingService
from app.services.rag.document_parser import parse_document
from app.utils.text import chunk_text


class IndexingService:
    def __init__(self) -> None:
        self.supabase = get_supabase_admin()
        self.embedding_service = EmbeddingService()

    async def index_document(
        self,
        user_id: str,
        document_id: str,
        filename: str,
        content_type: str,
        content: bytes,
    ) -> dict:
        self.supabase.table("uploaded_documents").update(
            {
                "embedding_status": "processing",
                "indexing_status": "processing",
                "processing_status": "chunking",
            }
        ).eq("document_id", document_id).execute()

        text = parse_document(content, content_type)
        chunks = chunk_text(text)

        self.supabase.table("uploaded_documents").update(
            {"processing_status": "vectorizing"}
        ).eq("document_id", document_id).execute()

        vectors = await self.embedding_service.embed(chunks)

        records = []
        for idx, (chunk, vector) in enumerate(zip(chunks, vectors)):
            records.append(
                {
                    "document_id": document_id,
                    "user_id": user_id,
                    "chunk_index": idx,
                    "chunk_text": chunk,
                    "embedding": vector,
                    "metadata": {"filename": filename, "source": "upload"},
                }
            )

        if records:
            self.supabase.table("document_chunks").insert(records).execute()

        self.supabase.table("uploaded_documents").update(
            {
                "embedding_status": "completed",
                "indexing_status": "completed",
                "processing_status": "indexed",
            }
        ).eq("document_id", document_id).execute()

        return {
            "document_id": document_id,
            "chunks": len(chunks),
            "status": "completed",
        }
