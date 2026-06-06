from pydantic import BaseModel


class ProfileResponse(BaseModel):
    user_id: str
    full_name: str
    learning_level: str
    preferred_explanation_style: str
    preferred_learning_mode: str
    subjects: list[str]
    xp_points: int
    learning_streak: int
    daily_goal: int


class ProfileUpdatePayload(BaseModel):
    learning_level: str
    preferred_explanation_style: str
    preferred_learning_mode: str
    subjects: list[str]
    daily_goal: int
