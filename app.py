from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from models import db, User, Barang
from datetime import date
from dotenv import load_dotenv

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

limiter = Limiter(
	key_func=get_remote_address,
	app=app,
	default_limits=[],
)

@login_manager.user_loader
def load_user(user_id):
	return db.session.get(User, int(user_id))

@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = (
    	"strict-origin-when-cross-origin"
    )
    response.headers["Content-Security-Policy"] = (
        "img-src 'self' data:; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "frame-ancestors 'none';"
    )
    return response

def parse_date(value):
	if not value:
		return None
	return date.fromisoformat(value)

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

@app.route("/barang")
@login_required
def barang():
	data_barang = db.session.execute(
		db.select(Barang).order_by(Barang.id.desc())
	).scalars().all()
	total_barang = len(data_barang)
	total_menunggu = sum(1 for barang in data_barang if barang.status_barang == "Menunggu Perbaikan")
	total_perbaikan = sum(1 for barang in data_barang if barang.status_barang == "Dalam Perbaikan")
	total_selesai = sum(1 for barang in data_barang if barang.status_barang == "Selesai")

	return render_template(
		"barang/index.html",
		data_barang=data_barang,
		total_barang=total_barang,
		total_menunggu=total_menunggu,
		total_perbaikan=total_perbaikan,
		total_selesai=total_selesai
	)

@app.route("/barang/tambah", methods=["POST"])
@login_required
def barang_tambah():
	nama_barang = request.form.get("nama_barang","").strip()
	status_barang = request.form.get("status_barang", "").strip()
	posisi = request.form.get("posisi", "").strip()
	tgl_perbaikan = request.form.get("tgl_perbaikan", "").strip()
	tgl_diperbaiki = request.form.get("tgl_diperbaiki", "").strip()
	keterangan = request.form.get("keterangan", "").strip()
	if not nama_barang or not status_barang or not posisi or not tgl_perbaikan:
		return redirect(url_for("barang"))
	barang = Barang(
		nama_barang=nama_barang,
		status_barang=status_barang,
		posisi=posisi,
		tgl_perbaikan=parse_date(tgl_perbaikan),
		tgl_diperbaiki=parse_date(tgl_diperbaiki),
		keterangan=keterangan or None
	)

	db.session.add(barang)
	db.session.commit()
	return redirect(url_for("barang"))

@app.route("/barang/edit/<int:id>", methods=["POST"])
@login_required
def barang_edit(id):
	barang = db.get_or_404(Barang, id)
	nama_barang = request.form.get("nama_barang","").strip()
	status_barang = request.form.get("status_barang", "").strip()
	posisi = request.form.get("posisi", "").strip()
	tgl_perbaikan = request.form.get("tgl_perbaikan", "").strip()
	tgl_diperbaiki = request.form.get("tgl_diperbaiki", "").strip()
	keterangan = request.form.get("keterangan", "").strip()
	if not nama_barang or not status_barang or not posisi or not tgl_perbaikan:
	    return redirect(url_for("barang"))

	barang.nama_barang=nama_barang,
	barang.status_barang=status_barang,
	barang.posisi=posisi,
	barang.tgl_perbaikan=parse_date(tgl_perbaikan),
	barang.tgl_diperbaiki=parse_date(tgl_diperbaiki),
	barang.keterangan=keterangan or None

	db.session.commit()
	return redirect(url_for("barang"))

@app.route("/barang/hapus/<int:id>", methods=["POST"])
@login_required
def barang_hapus(id):
	barang = db.get_or_404(Barang, id)
	db.session.delete(barang)
	db.session.commit()

	return redirect(url_for("barang"))

@app.route("/logout", methods=["POST"])
@login_required
def logout():
	logout_user()
	return redirect(url_for("login"))


if __name__ == "__main__":
	with app.app_context():
		db.create_all()

	app.run(debug=True)