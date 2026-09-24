import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent

# Load .env before reading environment variables
load_dotenv(BASE_DIR / ".env")


def get_required_env(name):
    value = os.getenv(name)

    if value is None:
        raise RuntimeError(
            f"Required environment variable is missing: {name}"
        )

    value = value.strip()

    if not value:
        raise RuntimeError(
            f"Required environment variable is empty: {name}"
        )

    return value


def get_is_production():
    """
    Detect production mode.

    Local development:
        APP_ENV=development

    Production:
        APP_ENV=production

    Render can also be detected through its RENDER environment
    variable, but APP_ENV remains the main application setting.
    """

    app_env = os.getenv(
        "APP_ENV",
        "development",
    ).strip().lower()

    render_environment = os.getenv(
        "RENDER",
        "",
    ).strip().lower()

    return (
        app_env == "production"
        or render_environment == "true"
    )


def normalize_database_url(database_url):
    """
    Normalize supported database URLs.

    SQLite remains unchanged.

    PostgreSQL URLs are explicitly configured to use
    Psycopg 3 through the SQLAlchemy psycopg dialect.
    """

    database_url = database_url.strip()

    # Old Render / Heroku-style PostgreSQL URL
    if database_url.startswith("postgres://"):
        return database_url.replace(
            "postgres://",
            "postgresql+psycopg://",
            1,
        )

    # Standard PostgreSQL URL
    if database_url.startswith("postgresql://"):
        return database_url.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1,
        )

    # Already using Psycopg 3
    if database_url.startswith(
        "postgresql+psycopg://"
    ):
        return database_url

    # SQLite or any other supported SQLAlchemy URL
    return database_url


class Config:

    # =====================================================
    # APPLICATION ENVIRONMENT
    # =====================================================

    APP_ENV = os.getenv(
        "APP_ENV",
        "development",
    ).strip().lower()

    IS_PRODUCTION = get_is_production()


    # =====================================================
    # SECURITY
    # =====================================================

    SECRET_KEY = get_required_env(
        "SECRET_KEY"
    )


    # =====================================================
    # DATABASE
    # =====================================================

    DATABASE_URL = get_required_env(
        "DATABASE_URL"
    )

    SQLALCHEMY_DATABASE_URI = (
        normalize_database_url(
            DATABASE_URL
        )
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False


    # =====================================================
    # SESSION / COOKIE SECURITY
    # =====================================================

    SESSION_COOKIE_HTTPONLY = True

    SESSION_COOKIE_SECURE = IS_PRODUCTION

    SESSION_COOKIE_SAMESITE = "Lax"

    REMEMBER_COOKIE_HTTPONLY = True

    REMEMBER_COOKIE_SECURE = IS_PRODUCTION

    REMEMBER_COOKIE_SAMESITE = "Lax"


    # =====================================================
    # UPLOAD LIMIT
    # =====================================================

    MAX_CONTENT_LENGTH = (
        100 * 1024 * 1024
    )


    # =====================================================
    # LOCAL UPLOAD FOLDER
    # =====================================================

    UPLOAD_FOLDER = (
        BASE_DIR
        / "static"
        / "uploads"
    )


    # =====================================================
    # CLOUDINARY
    # =====================================================

    CLOUDINARY_CLOUD_NAME = get_required_env(
        "CLOUDINARY_CLOUD_NAME"
    )

    CLOUDINARY_API_KEY = get_required_env(
        "CLOUDINARY_API_KEY"
    )

    CLOUDINARY_API_SECRET = get_required_env(
        "CLOUDINARY_API_SECRET"
    )


    # =====================================================
    # BOOK ORDER WHATSAPP
    # =====================================================

    ORDER_WHATSAPP_NUMBER = os.getenv(
        "ORDER_WHATSAPP_NUMBER",
        "",
    ).strip()