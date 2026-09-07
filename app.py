from flask import Flask, render_template, request, redirect, url_for, abort
from flask_login import LoginManager, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from models import db, User, Service, Gedung, Perangkat
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

PILIHAN_LANTAI = {"1","2","3","4","4.5","5","6"}
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
	data_service = db.session.execute(
		db.select(Service).order_by(Service.id.desc())
	).scalars().all()
	total_service = len(data_service)
	total_menunggu = sum(1 for service in data_service if service.status_service == "Menunggu")
	total_selesai = sum(1 for service in data_service if service.status_service == "Selesai")

	return render_template(
		"dashboard.html",
		total_service=total_service,
		total_menunggu=total_menunggu,
		total_selesai=total_selesai
	)

@app.route("/service")
@login_required
def service():
    data_service = db.session.execute(db.select(Service).order_by(Service.id.desc())).scalars().all()
    data_gedung = db.session.execute(db.select(Gedung).order_by(Gedung.id, Gedung.kampus, Gedung.nama_gedung, Gedung.lantai, Gedung.ruang)).scalars().all()
    data_perangkat = db.session.execute(db.select(Perangkat).order_by(Perangkat.id.desc())).scalars().all()
    return render_template(
        "service/index.html",
        data_service=data_service,
        data_gedung=data_gedung,
        data_perangkat=data_perangkat,
    )

@app.route("/service/tambah", methods=["POST"])
@login_required
def service_tambah():
	gedung = get_gedung_or_404()
	perangkat_id = request.form.get("perangkat_id","").strip()
	gedung_id = request.form.get("gedung_id", "").strip()
	status_service = request.form.get("status_service", "").strip()
	tgl_perbaikan = request.form.get("tgl_perbaikan", "").strip()
	tgl_perbaikan_selanjutnya = request.form.get("tgl_perbaikan_selanjutnya", "").strip()
	keterangan = request.form.get("keterangan", "").strip()
	if not perangkat_id or not gedung_id or not status_service or not tgl_perbaikan or not tgl_perbaikan_selanjutnya:
		return redirect(url_for("service"))
	service = Service(
		perangkat_id=perangkat_id,
		gedung_id=gedung_id,
		status_service=status_service,
		tgl_perbaikan=parse_date(tgl_perbaikan),
		tgl_perbaikan_selanjutnya=parse_date(tgl_perbaikan_selanjutnya),
		keterangan=keterangan or None
	)
	db.session.add(service)
	db.session.commit()
	return redirect(url_for("service"))

@app.route("/service/edit/<int:id>", methods=["POST"])
@login_required
def service_edit(id):
	service = db.get_or_404(Service, id)
	gedung = get_gedung_or_404()
	perangkat_id = request.form.get("perangkat_id","").strip()
	gedung_id = request.form.get("gedung_id", "").strip()
	status_service = request.form.get("status_service", "").strip()
	tgl_perbaikan = request.form.get("tgl_perbaikan", "").strip()
	tgl_perbaikan_selanjutnya = request.form.get("tgl_perbaikan_selanjutnya", "").strip()
	keterangan = request.form.get("keterangan", "").strip()
	if not perangkat_id or not gedung_id or not status_service or not tgl_perbaikan or not tgl_perbaikan_selanjutnya:
	    return redirect(url_for("service"))

	service.perangkat_id=perangkat_id
	service.gedung_id=gedung_id
	service.status_service=status_service
	service.tgl_perbaikan=parse_date(tgl_perbaikan)
	service.tgl_perbaikan_selanjutnya=parse_date(tgl_perbaikan_selanjutnya)
	service.keterangan=keterangan or None

	db.session.commit()
	return redirect(url_for("service"))

@app.route("/service/hapus/<int:id>", methods=["POST"])
@login_required
def service_hapus(id):
	service = db.get_or_404(Service, id)
	db.session.delete(service)
	db.session.commit()

	return redirect(url_for("service"))

@app.route("/gedung")
@login_required
def gedung():
	data_gedung = db.session.execute(
		db.select(Gedung).order_by(Gedung.id.desc())
	).scalars().all()

	return render_template(
		"gedung/index.html",
		data_gedung=data_gedung,
	)

@app.route("/gedung/tambah", methods=["POST"])
@login_required
def gedung_tambah():
	lantai = request.form.get("lantai")
	if lantai not in PILIHAN_LANTAI:
		abort(404)
	kampus = request.form.get("kampus","").strip()
	nama_gedung = request.form.get("nama_gedung", "").strip()
	lantai = request.form.get("lantai", "").strip()
	ruang = request.form.get("ruang", "").strip()
	keterangan = request.form.get("keterangan", "").strip()
	if not kampus or not nama_gedung or not lantai or not ruang:
		return redirect(url_for("gedung"))
	gedung = Gedung(
		kampus=kampus,
		nama_gedung=nama_gedung,
		lantai=lantai,
		ruang=ruang,
		keterangan=keterangan or None
	)
	db.session.add(gedung)
	db.session.commit()
	return redirect(url_for("gedung"))

@app.route("/gedung/edit/<int:id>", methods=["POST"])
@login_required
def gedung_edit(id):
	gedung = db.get_or_404(Gedung, id)
	lantai = request.form.get("lantai")
	if lantai not in PILIHAN_LANTAI:
		abort(404)
	kampus = request.form.get("kampus","").strip()
	nama_gedung = request.form.get("nama_gedung", "").strip()
	lantai = request.form.get("lantai", "").strip()
	ruang = request.form.get("ruang", "").strip()
	keterangan = request.form.get("keterangan", "").strip()
	if not kampus or not nama_gedung or not lantai or not ruang:
		return redirect(url_for("gedung"))

	gedung.kampus=kampus
	gedung.nama_gedung=nama_gedung
	gedung.lantai=lantai
	gedung.ruang=ruang
	gedung.keterangan=keterangan or None

	db.session.commit()
	return redirect(url_for("gedung"))

@app.route("/gedung/hapus/<int:id>", methods=["POST"])
@login_required
def gedung_hapus(id):
	gedung = db.get_or_404(Gedung, id)
	db.session.delete(gedung)
	db.session.commit()

	return redirect(url_for("gedung"))

@app.route("/perangkat")
@login_required
def perangkat():
	data_perangkat = db.session.execute(
		db.select(Perangkat).order_by(Perangkat.id.desc())
	).scalars().all()

	return render_template(
		"perangkat/index.html",
		data_perangkat=data_perangkat,
	)

@app.route("/perangkat/tambah", methods=["POST"])
@login_required
def perangkat_tambah():
	perangkat = request.form.get("perangkat","").strip()
	merek = request.form.get("merek", "").strip()
	type = request.form.get("type", "").strip()
	if not perangkat or not merek or not type:
		return redirect(url_for("perangkat"))
	perangkat = Perangkat(
		perangkat=perangkat,
		merek=merek,
		type=type,
	)
	db.session.add(perangkat)
	db.session.commit()
	return redirect(url_for("perangkat"))

@app.route("/perangkat/edit/<int:id>", methods=["POST"])
@login_required
def perangkat_edit(id):
	perangkat = db.get_or_404(Perangkat, id)
	nama_perangkat = request.form.get("perangkat","").strip()
	merek = request.form.get("merek", "").strip()
	type = request.form.get("type", "").strip()
	if not perangkat or not merek or not type:
		return redirect(url_for("perangkat"))

	perangkat.perangkat=nama_perangkat
	perangkat.merek=merek
	perangkat.type=type

	db.session.commit()
	return redirect(url_for("perangkat"))

@app.route("/perangkat/hapus/<int:id>", methods=["POST"])
@login_required
def perangkat_hapus(id):
	perangkat = db.get_or_404(Perangkat, id)
	db.session.delete(perangkat)
	db.session.commit()

	return redirect(url_for("perangkat"))

@app.route("/logout", methods=["POST"])
@login_required
def logout():
	logout_user()
	return redirect(url_for("login"))

def get_gedung_or_404():
    gedung_id = request.form.get("gedung_id", type=int)
    if not gedung_id:
        abort(404)
    return db.get_or_404(Gedung, gedung_id)

@app.errorhandler(404)
def page_not_found(error):
    return render_template("errors/404.html"), 404

if __name__ == "__main__":
	with app.app_context():
		db.create_all()

	app.run(debug=True)