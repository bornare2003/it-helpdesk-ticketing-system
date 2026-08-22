import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'helpdesk.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Simple built-in admin credentials (override via env vars in production)
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

    CATEGORIES = ["Hardware", "Software", "Network", "Security"]
    PRIORITIES = ["Low", "Medium", "High"]
    STATUSES = ["Open", "In Progress", "Resolved"]


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}