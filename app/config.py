from typing import List, Optional
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Firebase service account (sin archivo, vía ENV)
    FIREBASE_PROJECT_ID: str
    FIREBASE_CLIENT_EMAIL: str
    FIREBASE_CLIENT_ID: str
    FIREBASE_PRIVATE_KEY_ID: str
    FIREBASE_PRIVATE_KEY: str
    FIREBASE_AUTH_URI: str = "https://accounts.google.com/o/oauth2/auth"
    FIREBASE_TOKEN_URI: str = "https://oauth2.googleapis.com/token"
    FIREBASE_AUTH_PROVIDER_X509_CERT_URL: str = "https://www.googleapis.com/oauth2/v1/certs"
    FIREBASE_CLIENT_X509_CERT_URL: Optional[str] = None
    BYPASS_DAILY: bool = False
    BYPASS_SECRET: Optional[str] = None

    # Seguridad
    HASH_SECRET: str
    REQUIRE_CAPTCHA: bool = False
    RECAPTCHA_SECRET: Optional[str] = None

    # Lógica de negocio
    SHARDS: int = 20
    RATE_LIMIT_PER_MINUTE: int = 20
    TIMEZONE: str = "America/La_Paz"
    MAX_TOKENS_PER_PHRASE: int = 3
    MIN_LEN: int = 2
    MAX_LEN: int = 40

    # Server
    ALLOWED_ORIGINS: List[AnyHttpUrl] = []
    APP_NAME: str = "WordCloud API"
    APP_ENV: str = "dev"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
