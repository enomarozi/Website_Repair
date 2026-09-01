from app import app
from models import  db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()

with app.app_context():
	user = User(
		username="admin",
		password=generate_password_hash("12345678")
	)
	db.session.add(user)
	db.session.commit()
