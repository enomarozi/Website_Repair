from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True, nullable=False)
	password = db.Column(db.String(255), nullable=False)

class Barang(db.Model):
	__tablename__ = "barang"
	id = db.Column(db.Integer, primary_key=True)
	nama_barang = db.Column(db.String(150), nullable=False)
	status_barang = db.Column(db.String(50), nullable=False, default="Menunggu")
	posisi = db.Column(db.String(150), nullable=False)
	tgl_diperbaiki = db.Column(db.Date, nullable=False)
	tgl_perbaikan_selanjutnya = db.Column(db.Date, nullable=False)
	keterangan = db.Column(db.Text, nullable=False)