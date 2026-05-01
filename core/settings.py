from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # App
    APP_NAME: str  = "API Starter"
    APP_ENV:  str  = "development"
    DEBUG:    bool = False

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Database
    POSTGRES_HOST:     str = "localhost"
    POSTGRES_PORT:     int = 5432
    POSTGRES_USER:     str
    POSTGRES_PASSWORD: str
    POSTGRES_DB:       str

    # Auth
    SECRET_KEY:                  str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # Seed admin (created on startup if missing)
    ADMIN_EMAIL:    str
    ADMIN_PASSWORD: str
    ADMIN_NAME:     str = "Administrateur"

    # Mail (Brevo SMTP or any SMTP)
    MAIL_SERVER:   str  = "smtp-relay.brevo.com"
    MAIL_PORT:     int  = 587
    MAIL_USERNAME: str  = ""
    MAIL_PASSWORD: str  = ""
    MAIL_FROM:     str  = ""
    MAIL_STARTTLS: bool = True

    # MinIO (S3-compatible storage)
    MINIO_ENDPOINT:   str  = "minio:9000"
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET:     str  = "app"
    MINIO_SECURE:     bool = False
    MINIO_PUBLIC_URL: str  = "http://localhost:9000"

    # Redis (Huey task queue)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"


settings = Settings()
