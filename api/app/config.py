from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./data/civic_fix.db"
    jwt_secret: str = "change-me-in-production-min-32-chars!!"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7
    upload_dir: str = "./data/uploads"
    cors_origins: str = "http://localhost:20640,http://127.0.0.1:20640"
    city_default: str = "moscow"
    redis_url: str = "redis://localhost:20645/0"
    mos_id_enabled: bool = False
    mos_id_client_id: str = ""
    mos_id_client_secret: str = ""
    mos_id_redirect_uri: str = "http://localhost:20640/api/auth/mos-id/callback"
    telegram_bot_token: str = ""
    esia_enabled: bool = False


settings = Settings()
