from pydantic import BaseModel, EmailStr, Field, field_validator

from app.app.utils.enums import EXPLANATION_STYLES, LEARNING_LEVELS, LEARNING_MODES


class SignUpStep1(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=120)


class SignUpStep2(BaseModel):
    learning_level: str

    @field_validator("learning_level")
    @classmethod
    def validate_level(cls, value: str) -> str:
        if value not in LEARNING_LEVELS:
            raise ValueError("Invalid learning level")
        return value


class SignUpStep3(BaseModel):
    subjects: list[str]
    preferred_explanation_style: str
    preferred_learning_mode: str


class SignUpPayload(BaseModel):
    account: SignUpStep1
    learning: SignUpStep2
    preferences: SignUpStep3


class LoginPayload(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str = "bearer"
    user_id: str
    requires_confirmation: bool = False


class PreferencesUpdatePayload(BaseModel):
    learning_level: str
    subjects: list[str]
    preferred_explanation_style: str
    preferred_learning_mode: str
