from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import db, Att_kampus, Att_gedung, Att_lantai, Att_ruang, Att_perangkat, Att_merek

atribut = Blueprint("atribut", __name__, url_prefix="/atribut")

###### ATT KAMPUS ######

@atribut.route("/att_kampus")
@login_required
def att_kampus():
    data_kampus = db.session.execute(db.select(Att_kampus).order_by(Att_kampus.id.desc())).scalars().all()
    return render_template(
        "att_kampus/index.html",
        data_kampus=data_kampus,
    )

@atribut.route("/att_kampus/tambah", methods=["POST"])
@login_required
def att_kampus_tambah():
    nama_kampus = request.form.get("nama_kampus", "").strip()
    existing = db.session.execute(db.select(Att_kampus).where(db.func.lower(Att_kampus.nama_kampus) == nama_kampus.lower())).scalars().first()
    if existing:
        flash("Nama Kampus sudah terdaftar.", "danger")
        return redirect(url_for("atribut.att_kampus"))
    if not nama_kampus:
        return redirect(url_for("atribut.att_kampus"))
    att_kampus = Att_kampus(
        nama_kampus=nama_kampus,
    )
    db.session.add(att_kampus)
    db.session.commit()
    return redirect(url_for("atribut.att_kampus"))

@atribut.route("/att_kampus/edit/<int:id>", methods=["POST"])
@login_required
def att_kampus_edit(id):
    att_kampus = db.get_or_404(Att_kampus, id)
    nama_kampus = request.form.get("nama_kampus","").strip()
    existing = db.session.execute(db.select(Att_kampus).where(db.func.lower(Att_kampus.nama_kampus) == nama_kampus.lower())).scalars().first()
    if existing:
        flash("Nama Kampus sudah terdaftar.", "danger")
        return redirect(url_for("atribut.att_kampus"))
    if not nama_kampus:
        return redirect(url_for("atribut.att_kampus"))

    att_kampus.nama_kampus=nama_kampus

    db.session.commit()
    return redirect(url_for("atribut.att_kampus"))

@atribut.route("/att_kampus/hapus/<int:id>", methods=["POST"])
@login_required
def att_kampus_delete(id):
    att_kampus = db.get_or_404(Att_kampus, id)
    db.session.delete(att_kampus)
    db.session.commit()

    return redirect(url_for("atribut.att_kampus"))

###### ATT GEDUNG ######

@atribut.route("/att_gedung")
@login_required
def att_gedung():
    data_gedung = db.session.execute(db.select(Att_gedung).order_by(Att_gedung.id.desc())).scalars().all()
    return render_template(
        "att_gedung/index.html",
        data_gedung=data_gedung,
    )

@atribut.route("/att_gedung/tambah", methods=["POST"])
@login_required
def att_gedung_tambah():
    nama_gedung = request.form.get("nama_gedung", "").strip()
    existing = db.session.execute(db.select(Att_gedung).where(db.func.lower(Att_gedung.nama_gedung) == nama_gedung.lower())).scalars().first()
    if existing:
        flash("Nama Gedung sudah terdaftar.", "danger")
        return redirect(url_for("atribut.att_gedung"))
    if not nama_gedung:
        return redirect(url_for("atribut.att_gedung"))
    att_gedung = Att_gedung(
        nama_gedung=nama_gedung,
    )
    db.session.add(att_gedung)
    db.session.commit()
    return redirect(url_for("atribut.att_gedung"))

@atribut.route("/att_gedung/edit/<int:id>", methods=["POST"])
@login_required
def att_gedung_edit(id):
    att_gedung = db.get_or_404(Att_gedung, id)
    nama_gedung = request.form.get("nama_gedung","").strip()
    existing = db.session.execute(db.select(Att_gedung).where(db.func.lower(Att_gedung.nama_gedung) == nama_gedung.lower())).scalars().first()
    if existing:
        flash("Nama Gedung sudah terdaftar.", "danger")
        return redirect(url_for("atribut.att_gedung"))
    if not nama_gedung:
        return redirect(url_for("atribut.att_gedung"))

    att_gedung.nama_gedung=nama_gedung

    db.session.commit()
    return redirect(url_for("atribut.att_gedung"))

@atribut.route("/att_gedung/hapus/<int:id>", methods=["POST"])
@login_required
def att_gedung_delete(id):
    att_gedung = db.get_or_404(Att_gedung, id)
    db.session.delete(att_gedung)
    db.session.commit()

    return redirect(url_for("atribut.att_gedung"))

###### ATT LANTAI ######

@atribut.route("/att_lantai")
@login_required
def att_lantai():
    data_lantai = db.session.execute(db.select(Att_lantai).order_by(Att_lantai.id.desc())).scalars().all()
    return render_template(
        "att_lantai/index.html",
        data_lantai=data_lantai,
    )

@atribut.route("/att_lantai/tambah", methods=["POST"])
@login_required
def att_lantai_tambah():
    nama_lantai = request.form.get("nama_lantai", "").strip()
    existing = db.session.execute(db.select(Att_lantai).where(db.func.lower(Att_lantai.nama_lantai) == nama_lantai.lower())).scalars().first()
    if existing:
        flash("Nama Lantai sudah terdaftar.", "danger")
        return redirect(url_for("atribut.att_lantai"))
    if not nama_lantai:
        return redirect(url_for("atribut.att_lantai"))
    att_lantai = Att_lantai(
        nama_lantai=nama_lantai,
    )
    db.session.add(att_lantai)
    db.session.commit()
    return redirect(url_for("atribut.att_lantai"))

@atribut.route("/att_lantai/edit/<int:id>", methods=["POST"])
@login_required
def att_lantai_edit(id):
    att_lantai = db.get_or_404(Att_lantai, id)
    nama_lantai = request.form.get("nama_lantai","").strip()
    existing = db.session.execute(db.select(Att_lantai).where(db.func.lower(Att_lantai.nama_lantai) == nama_lantai.lower())).scalars().first()
    if existing:
        flash("Nama Lantai sudah terdaftar.", "danger")
        return redirect(url_for("atribut.att_lantai"))
    if not nama_lantai:
        return redirect(url_for("atribut.att_lantai"))

    att_lantai.nama_lantai=nama_lantai

    db.session.commit()
    return redirect(url_for("atribut.att_lantai"))

@atribut.route("/att_lantai/hapus/<int:id>", methods=["POST"])
@login_required
def att_lantai_delete(id):
    att_lantai = db.get_or_404(Att_lantai, id)
    db.session.delete(att_lantai)
    db.session.commit()

    return redirect(url_for("atribut.att_lantai"))


###### ATT RUANG ######

@atribut.route("/att_ruang")
@login_required
def att_ruang():
    data_ruang = db.session.execute(db.select(Att_ruang).order_by(Att_ruang.id.desc())).scalars().all()
    return render_template(
        "att_ruang/index.html",
        data_ruang=data_ruang,
    )

@atribut.route("/att_ruang/tambah", methods=["POST"])
@login_required
def att_ruang_tambah():
    nama_ruang = request.form.get("nama_ruang", "").strip()
    existing = db.session.execute(db.select(Att_ruang).where(db.func.lower(Att_ruang.nama_ruang) == nama_ruang.lower())).scalars().first()
    if existing:
        flash("Nama Ruang sudah terdaftar.", "danger")
        return redirect(url_for("atribut.att_ruang"))
    if not nama_ruang:
        return redirect(url_for("atribut.att_ruang"))
    att_ruang = Att_ruang(
        nama_ruang=nama_ruang,
    )
    print(att_ruang)
    db.session.add(att_ruang)
    db.session.commit()
    return redirect(url_for("atribut.att_ruang"))

@atribut.route("/att_ruang/edit/<int:id>", methods=["POST"])
@login_required
def att_ruang_edit(id):
    att_ruang = db.get_or_404(Att_ruang, id)
    nama_ruang = request.form.get("nama_ruang","").strip()
    existing = db.session.execute(db.select(Att_ruang).where(db.func.lower(Att_ruang.nama_ruang) == nama_ruang.lower())).scalars().first()
    if existing:
        flash("Nama Ruang sudah terdaftar.", "danger")
        return redirect(url_for("atribut.att_ruang"))
    if not nama_ruang:
        return redirect(url_for("atribut.att_ruang"))

    att_ruang.nama_ruang=nama_ruang

    db.session.commit()
    return redirect(url_for("atribut.att_ruang"))

@atribut.route("/att_ruang/hapus/<int:id>", methods=["POST"])
@login_required
def att_ruang_delete(id):
    att_ruang = db.get_or_404(Att_ruang, id)
    db.session.delete(att_ruang)
    db.session.commit()

    return redirect(url_for("atribut.att_ruang"))

###### ATT PERANGKAT ######

@atribut.route("/att_perangkat")
@login_required
def att_perangkat():
    data_perangkat = db.session.execute(db.select(Att_perangkat).order_by(Att_perangkat.id.desc())).scalars().all()
    return render_template(
        "att_perangkat/index.html",
        data_perangkat=data_perangkat,
    )

@atribut.route("/att_perangkat/tambah", methods=["POST"])
@login_required
def att_perangkat_tambah():
    nama_perangkat = request.form.get("nama_perangkat", "").strip()
    existing = db.session.execute(db.select(Att_perangkat).where(db.func.lower(Att_perangkat.nama_perangkat) == nama_perangkat.lower())).scalars().first()
    if existing:
        flash("Nama Perangkat sudah terdaftar.", "danger")
        return redirect(url_for("atribut.att_perangkat"))
    if not nama_perangkat:
        return redirect(url_for("atribut.att_perangkat"))
    att_perangkat = Att_perangkat(
        nama_perangkat=nama_perangkat,
    )
    print(att_perangkat)
    db.session.add(att_perangkat)
    db.session.commit()
    return redirect(url_for("atribut.att_perangkat"))

@atribut.route("/att_perangkat/edit/<int:id>", methods=["POST"])
@login_required
def att_perangkat_edit(id):
    att_perangkat = db.get_or_404(Att_perangkat, id)
    nama_perangkat = request.form.get("nama_perangkat","").strip()
    existing = db.session.execute(db.select(Att_perangkat).where(db.func.lower(Att_perangkat.nama_perangkat) == nama_perangkat.lower())).scalars().first()
    if existing:
        flash("Nama Perangkat sudah terdaftar.", "danger")
        return redirect(url_for("atribut.att_perangkat"))
    if not nama_perangkat:
        return redirect(url_for("atribut.att_perangkat"))

    att_perangkat.nama_perangkat=nama_perangkat

    db.session.commit()
    return redirect(url_for("atribut.att_perangkat"))

@atribut.route("/att_perangkat/hapus/<int:id>", methods=["POST"])
@login_required
def att_perangkat_delete(id):
    att_perangkat = db.get_or_404(Att_perangkat, id)
    db.session.delete(att_perangkat)
    db.session.commit()

    return redirect(url_for("atribut.att_perangkat"))

###### ATT MEREK ######

@atribut.route("/att_merek")
@login_required
def att_merek():
    data_merek = db.session.execute(db.select(Att_merek).order_by(Att_merek.id.desc())).scalars().all()
    return render_template(
        "att_merek/index.html",
        data_merek=data_merek,
    )

@atribut.route("/att_merek/tambah", methods=["POST"])
@login_required
def att_merek_tambah():
    nama_merek = request.form.get("nama_merek", "").strip()
    existing = db.session.execute(db.select(Att_merek).where(db.func.lower(Att_merek.nama_merek) == nama_merek.lower())).scalars().first()
    if existing:
        flash("Nama Merek sudah terdaftar.", "danger")
        return redirect(url_for("atribut.att_merek"))
    if not nama_merek:
        return redirect(url_for("atribut.att_merek"))
    att_merek = Att_merek(
        nama_merek=nama_merek,
    )
    print(att_merek)
    db.session.add(att_merek)
    db.session.commit()
    return redirect(url_for("atribut.att_merek"))

@atribut.route("/att_merek/edit/<int:id>", methods=["POST"])
@login_required
def att_merek_edit(id):
    att_merek = db.get_or_404(Att_merek, id)
    nama_merek = request.form.get("nama_merek","").strip()
    existing = db.session.execute(db.select(Att_merek).where(db.func.lower(Att_merek.nama_merek) == nama_merek.lower())).scalars().first()
    if existing:
        flash("Nama Merek sudah terdaftar.", "danger")
        return redirect(url_for("atribut.att_merek"))
    if not nama_merek:
        return redirect(url_for("atribut.att_merek"))

    att_merek.nama_merek=nama_merek

    db.session.commit()
    return redirect(url_for("atribut.att_merek"))

@atribut.route("/att_merek/hapus/<int:id>", methods=["POST"])
@login_required
def att_merek_delete(id):
    att_merek = db.get_or_404(Att_merek, id)
    db.session.delete(att_merek)
    db.session.commit()

    return redirect(url_for("atribut.att_merek"))