from io import BytesIO
from decimal import Decimal
from flask import send_file
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from models import db, Perbaikan

def generate_perbaikan_pdf(tanggal):
    data = db.session.execute(db.select(Perbaikan).where(Perbaikan.tgl_perbaikan == tanggal).order_by(Perbaikan.id.asc())).scalars().all()
    if not data:
        return None
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=6*mm, leftMargin=6*mm, topMargin=8*mm, bottomMargin=8*mm)
    styles = getSampleStyleSheet()
    header = ParagraphStyle("header", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=6.5, leading=7, alignment=TA_CENTER)
    cell = ParagraphStyle("cell", parent=styles["Normal"], fontName="Helvetica", fontSize=6.5, leading=7.5, alignment=TA_LEFT)
    center = ParagraphStyle("center", parent=cell, alignment=TA_CENTER)
    right = ParagraphStyle("right", parent=cell, alignment=TA_RIGHT)
    title = ParagraphStyle("title", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=11, leading=13, alignment=TA_CENTER)
    sub = ParagraphStyle("sub", parent=title, fontSize=8, leading=10)
    elements = [Paragraph("LAPORAN SERVIS AC", title), Paragraph(f"Tanggal Perbaikan: {tanggal.strftime('%d/%m/%Y')}", sub)]
    rows = [[Paragraph("No", header), Paragraph("Tanggal", header), Paragraph("LOKASI", header), Paragraph("Merek AC", header), Paragraph("Type", header), Paragraph("Unit", header), Paragraph("Uraian<br/>Pekerjaan", header), Paragraph("Stn", header), Paragraph("Vol", header), Paragraph("Harga<br/>Satuan (Rp)", header), Paragraph("Jumlah<br/>Harga (Rp)", header)]]
    spans = []
    row_number = 1
    nomor = 1
    for item in data:
        details = item.details
        if not details:
            continue
        perangkat = item.perangkat
        gedung = item.gedung
        lokasi = f"{gedung.nama_gedung}, Lantai {gedung.lantai}, Ruang {gedung.ruang}"
        start_row = row_number
        for index, detail in enumerate(details):
            if index == 0:
                main_data = [Paragraph(str(nomor), center), Paragraph(item.tgl_perbaikan.strftime("%d/%m/%Y"), center), Paragraph(lokasi, cell), Paragraph(perangkat.merek, cell), Paragraph(perangkat.type, center), Paragraph("1", center)]
            else:
                main_data = ["", "", "", "", "", ""]
            harga = Decimal(detail.harga_satuan or 0)
            total = Decimal(detail.total_harga or 0)
            rows.append(main_data + [Paragraph(detail.uraian, cell), Paragraph(str(detail.satuan), center), Paragraph(detail.vol, center), Paragraph(f"{harga:,.0f}".replace(",", "."), right), Paragraph(f"{total:,.0f}".replace(",", "."), right)])
            row_number += 1
        end_row = row_number - 1
        if len(details) > 1:
            for col in range(6):
                spans.append(("SPAN", (col, start_row), (col, end_row)))
        nomor += 1
    widths = [8*mm, 20*mm, 43*mm, 25*mm, 18*mm, 12*mm, 55*mm, 12*mm, 14*mm, 30*mm, 32*mm]
    table = Table(rows, colWidths=widths, repeatRows=1)
    table.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.5,colors.black),("BACKGROUND",(0,0),(-1,0),colors.HexColor("#d9d9d9")),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),("LEFTPADDING",(0,0),(-1,-1),3),("RIGHTPADDING",(0,0),(-1,-1),3),*spans]))
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return send_file(buffer, mimetype="application/pdf", as_attachment=False, download_name=f"laporan_perbaikan_{tanggal.strftime('%Y-%m-%d')}.pdf")
