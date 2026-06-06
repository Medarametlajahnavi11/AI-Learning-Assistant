from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="AI Learning Assistant", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    cors_origins: str = Field(default="http://localhost:5173", alias="CORS_ORIGINS")

    supabase_url: str = Field(default="https://your-project-ref.supabase.co", alias="SUPABASE_URL")
    supabase_anon_key: str = Field(default="SUPABASE_ANON_KEY_PLACEHOLDER", alias="SUPABASE_ANON_KEY")
    supabase_service_role_key: str = Field(default="SUPABASE_SERVICE_ROLE_KEY_PLACEHOLDER", alias="SUPABASE_SERVICE_ROLE_KEY")
    supabase_jwt_secret: str = Field(default="SUPABASE_JWT_SECRET_PLACEHOLDER", alias="SUPABASE_JWT_SECRET")
    supabase_jwks_json: str | None = Field(default=None, alias="SUPABASE_JWKS_JSON")

    chat_provider: str = Field(default="openai", alias="CHAT_PROVIDER")
    openai_api_key: str = Field(default="OPENAI_API_KEY_PLACEHOLDER", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4.1-mini", alias="OPENAI_MODEL")
    openai_base_url: str | None = Field(default=None, alias="OPENAI_BASE_URL")

    groq_api_key: str | None = Field(default=None, alias="GROQ_API_KEY")
    groq_model: str = Field(default="mixtral-8x7b-32768", alias="GROQ_MODEL")

    huggingface_api_key: str = Field(default="HF_API_KEY_PLACEHOLDER", alias="HUGGINGFACE_API_KEY")
    embedding_provider: str = Field(default="openai", alias="EMBEDDING_PROVIDER")
    embedding_model: str = Field(default="text-embedding-3-small", alias="EMBEDDING_MODEL")

    upload_bucket: str = Field(default="learning-documents", alias="SUPABASE_STORAGE_BUCKET")
    max_upload_mb: int = Field(default=25, alias="MAX_UPLOAD_MB")

    rate_limit_per_minute: int = Field(default=60, alias="RATE_LIMIT_PER_MINUTE")


settings = Settings()
