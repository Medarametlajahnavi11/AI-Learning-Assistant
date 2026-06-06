from pydantic import BaseModel


class AnalyticsOverview(BaseModel):
    questions_asked: int
    documents_uploaded: int
    learning_streak: int
    subjects_learned: int
    total_xp: int
    vault_usage_count: int
    global_usage_count: int
