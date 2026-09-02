from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True, nullable=False)
	password = db.Column(db.String(255), nullable=False)

class Service(db.Model):
	__tablename__ = "service"
	id = db.Column(db.Integer, primary_key=True)
	nama_service = db.Column(db.String(150), nullable=False)
	status_service = db.Column(db.String(50), nullable=False, default="Menunggu")
	posisi = db.Column(db.Text, nullable=False)
	tgl_perbaikan = db.Column(db.Date, nullable=False)
	tgl_perbaikan_selanjutnya = db.Column(db.Date, nullable=False)
	keterangan = db.Column(db.Text, nullable=True)

class Gedung(db.Model):
	__tablename__ = "gedung"
	id = db.Column(db.Integer, primary_key=True)
	kampus = db.Column(db.String(100), nullable=False)
	nama_gedung = db.Column(db.String(100), nullable=False)
	lantai = db.Column(db.String(3), nullable=False, default="1")
	ruang = db.Column(db.String(100), nullable=False)
	keterangan = db.Column(db.Text, nullable=True)