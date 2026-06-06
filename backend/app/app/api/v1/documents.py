import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.core.config import settings
from app.core.security import CurrentUser, require_user
from app.db.supabase_client import get_supabase_admin
from app.schemas.document import DocumentResponse
from app.services.rag.indexing_service import IndexingService

router = APIRouter(prefix="/documents", tags=["documents"])
supabase = get_supabase_admin()
indexer = IndexingService()


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    user: CurrentUser = Depends(require_user),
):
    content = await file.read()
    size_limit = settings.max_upload_mb * 1024 * 1024
    if len(content) > size_limit:
        raise HTTPException(status_code=413, detail="File exceeds size limit")

    document_id = str(uuid.uuid4())
    object_path = f"{user.user_id}/{document_id}_{file.filename}"

    supabase.storage.from_(settings.upload_bucket).upload(
        object_path,
        content,
        {"content-type": file.content_type or "application/octet-stream"},
    )

    supabase.table("uploaded_documents").insert(
        {
            "document_id": document_id,
            "user_id": user.user_id,
            "filename": file.filename,
            "file_path": object_path,
            "file_type": file.content_type or "application/octet-stream",
            "file_size": len(content),
            "embedding_status": "pending",
            "indexing_status": "pending",
            "processing_status": "uploaded",
        }
    ).execute()

    result = await indexer.index_document(
        user_id=user.user_id,
        document_id=document_id,
        filename=file.filename,
        content_type=file.content_type or "text/plain",
        content=content,
    )

    return result


@router.get("")
async def list_documents(user: CurrentUser = Depends(require_user)):
    response = supabase.table("uploaded_documents").select("*").eq("user_id", user.user_id).order("upload_date", desc=True).execute()
    return response.data or []


@router.delete("/{document_id}")
async def delete_document(document_id: str, user: CurrentUser = Depends(require_user)):
    row = supabase.table("uploaded_documents").select("*").eq("document_id", document_id).eq("user_id", user.user_id).limit(1).execute()
    existing = (row.data or [None])[0]
    if not existing:
        raise HTTPException(status_code=404, detail="Document not found")

    supabase.storage.from_(settings.upload_bucket).remove([existing["file_path"]])
    supabase.table("uploaded_documents").delete().eq("document_id", document_id).execute()
    return {"status": "deleted", "document_id": document_id}


@router.post("/{document_id}/reindex")
async def reindex_document(document_id: str, user: CurrentUser = Depends(require_user)):
    row = supabase.table("uploaded_documents").select("*").eq("document_id", document_id).eq("user_id", user.user_id).limit(1).execute()
    existing = (row.data or [None])[0]
    if not existing:
        raise HTTPException(status_code=404, detail="Document not found")

    download = supabase.storage.from_(settings.upload_bucket).download(existing["file_path"])
    supabase.table("document_chunks").delete().eq("document_id", document_id).execute()

    result = await indexer.index_document(
        user_id=user.user_id,
        document_id=document_id,
        filename=existing["filename"],
        content_type=existing["file_type"],
        content=download,
    )
    return result
