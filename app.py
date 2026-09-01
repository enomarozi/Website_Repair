from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from models import db, User

import os

load_dotenv()
secret_key = os.getenv("SECRET_KEY")
if not secret_key:
	raise RuntimeError(
		"SECRET_KEY belum diatur di .env"
	)

app = Flask(__name__)

app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db_repair.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = secret_key

db.init_app(app)

csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Silahkan login dahulu."

@login_manager.user_loader
def load_user(user_id):
	return db.session.get(User, int(user_id))

limiter = Limiter(
	key_func=get_remote_address,
	app=app,
	default_limits=[],
)
print(limiter)

@app.route("/")
def index():
	return redirect(url_for("dashboard"))

@app.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
	if request.method == "POST":
		username = request.form.get("username","").strip()
		password = request.form.get("password","")
		user = db.session.execute(
			db.select(User).filter_by(username=username)
		).scalar_one_or_none()
		if user and check_password_hash(user.password, password):
			login_user(user)
			return redirect(url_for("dashboard"))
		return render_template(
			"login.html",
			error="Username atau password salah."
		)
	return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
	return render_template("dashboard.html")

@app.route("/logout", methods=["POST"])
@login_required
def logout():
	logout_user()
	return redirect(url_for("login"))


if __name__ == "__main__":
	with app.app_context():
		db.create_all()

	app.run(debug=True)