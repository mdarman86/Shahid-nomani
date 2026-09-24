from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect


# =========================================================
# DATABASE
# =========================================================

db = SQLAlchemy()


# =========================================================
# DATABASE MIGRATIONS
# =========================================================

migrate = Migrate()


# =========================================================
# CSRF PROTECTION
# =========================================================

csrf = CSRFProtect()


# =========================================================
# LOGIN MANAGER
# =========================================================

login_manager = LoginManager()

login_manager.login_view = "admin.login"

login_manager.login_message = (
    "Please login to access the admin panel."
)