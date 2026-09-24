from datetime import datetime

from flask_login import UserMixin

from extensions import db


# =========================================================
# ADMIN
# =========================================================

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# =========================================================
# ARTICLE
# =========================================================

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(220), nullable=False)
    summary = db.Column(db.Text)
    content = db.Column(db.Text)
    image = db.Column(db.String(500))

    # Kept only for compatibility with old database records.
    # New articles are text-only and do not upload/use PDF.
    pdf = db.Column(db.String(500))

    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# =========================================================
# BAYAN
# =========================================================

class Bayan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(220), nullable=False)
    description = db.Column(db.Text)
    upload_type = db.Column(db.String(30), default="online")
    platform = db.Column(db.String(50))
    video_url = db.Column(db.String(1000))
    video_file = db.Column(db.String(500))
    thumbnail = db.Column(db.String(500))
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# =========================================================
# BOOK
# =========================================================

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(220), nullable=False)
    author = db.Column(db.String(180), default="Shahid Nomani")
    description = db.Column(db.Text)
    image = db.Column(db.String(500))
    book_type = db.Column(db.String(30), default="order")
    pdf = db.Column(db.String(500))
    buy_link = db.Column(db.String(1000))
    price = db.Column(db.Integer)
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# =========================================================
# URDU ADAB
# =========================================================

class Adab(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), default="Other")
    title = db.Column(db.String(220), nullable=False)
    summary = db.Column(db.Text)
    content = db.Column(db.Text)
    image = db.Column(db.String(500))
    pdf = db.Column(db.String(500))
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# =========================================================
# GALLERY
# =========================================================

class GalleryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(500), nullable=False)
    caption = db.Column(db.String(300))
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# =========================================================
# CONTACT MESSAGE
# =========================================================

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(180), nullable=False)
    message = db.Column(db.Text, nullable=False)
    reply = db.Column(db.Text)
    status = db.Column(db.String(30), default="New")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    replied_at = db.Column(db.DateTime)