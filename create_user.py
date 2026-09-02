from app import app
from models import db, User, Service
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()

    username = "admin"
    password = "12345678"

    user = User.query.filter_by(username=username).first()

    if user:
        print(f"User '{username}' sudah ada.")
    else:
        user = User(
            username=username,
            password=generate_password_hash(password)
        )

        db.session.add(user)
        db.session.commit()

        print(f"User '{username}' berhasil dibuat.")