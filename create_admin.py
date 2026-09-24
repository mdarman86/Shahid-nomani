from dotenv import load_dotenv
import os

from argon2 import PasswordHasher

from app import app
from extensions import db
from models import Admin


load_dotenv()

username = os.getenv("ADMIN_USERNAME")
password = os.getenv("ADMIN_PASSWORD")

if not username or not password:
    print("ERROR: ADMIN_USERNAME or ADMIN_PASSWORD is missing from .env")
    raise SystemExit(1)

hasher = PasswordHasher()


with app.app_context():

    admin = Admin.query.filter_by(username=username).first()

    if admin:
        admin.password_hash = hasher.hash(password)

        db.session.commit()

        print("Admin password updated successfully.")

    else:
        admin = Admin(
            username=username,
            password_hash=hasher.hash(password)
        )

        db.session.add(admin)
        db.session.commit()

        print("Admin account created successfully.")