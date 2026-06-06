from pydantic import BaseModel


class DocumentReindexPayload(BaseModel):
    document_id: str


class DocumentResponse(BaseModel):
    document_id: str
    filename: str
    file_type: str
    embedding_status: str
    indexing_status: str
    processing_status: str
    upload_date: str
