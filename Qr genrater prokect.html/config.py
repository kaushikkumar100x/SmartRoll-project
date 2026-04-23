"""Application configuration."""
import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ.get("SESSION_SECRET", "dev-secret-change-me")
    DATABASE = os.environ.get("DATABASE_PATH", os.path.join(os.path.dirname(__file__), "smartroll.db"))
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", os.path.join(os.path.dirname(__file__), "uploads"))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {"pdf"}

    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # QR token expiry (seconds)
    QR_EXPIRY_SECONDS = 30
    JWT_SECRET = os.environ.get("JWT_SECRET", "jwt-dev-secret-change-me")
    JWT_EXPIRY_HOURS = 8
