from io import BytesIO
from decimal import Decimal
from pathlib import Path
from flask import send_file, current_app
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4, portrait
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from models import db, Perbaikan

def generate_perbaikan_pdf(tanggal, nomor, hal):
    data = db.session.execute(
        db.select(Perbaikan)
        .where(Perbaikan.tgl_perbaikan == tanggal)
        .order_by(Perbaikan.id.asc())
    ).scalars().all()

    if not data:
        return None

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=portrait(A4),
        rightMargin=6*mm,
        leftMargin=6*mm,
        topMargin=6*mm,
        bottomMargin=8*mm
    )

    styles = getSampleStyleSheet()

    company = ParagraphStyle(
        "company",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=11,
        textColor=colors.HexColor("#087f23"),
        alignment=TA_LEFT
    )

    address = ParagraphStyle(
        "address",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=6.5,
        leading=7.5,
        alignment=TA_LEFT
    )

    invoice = ParagraphStyle(
        "invoice",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=20,
        textColor=colors.HexColor("#087f23"),
        alignment=TA_LEFT
    )

    normal = ParagraphStyle(
        "normal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7,
        leading=8,
        alignment=TA_LEFT
    )

    normal_bold = ParagraphStyle(
        "normal_bold",
        parent=normal,
        fontName="Helvetica-Bold"
    )

    date_style = ParagraphStyle(
        "date",
        parent=normal,
        alignment=TA_RIGHT
    )

    recipient = ParagraphStyle(
        "recipient",
        parent=normal,
        leading=8.5,
        alignment=TA_LEFT
    )

    header = ParagraphStyle(
        "header",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=6.5,
        leading=7,
        alignment=TA_CENTER
    )

    cell = ParagraphStyle(
        "cell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=6.5,
        leading=7.5,
        alignment=TA_LEFT
    )

    center = ParagraphStyle(
        "center",
        parent=cell,
        alignment=TA_CENTER
    )

    right = ParagraphStyle(
        "right",
        parent=cell,
        alignment=TA_RIGHT
    )

    elements = []

    logo_path = Path(current_app.root_path) / "static" / "images" / "logo_aksi.png"

    if logo_path.exists():
        logo = Image(str(logo_path), width=42*mm, height=20*mm)
    else:
        logo = Paragraph("", normal)

    company_info = [
        Paragraph("PT ANDALAS KONSULTAN<br/>SARANA INFRASTRUKTUR", company),
        Spacer(1, 1*mm),
        Paragraph(
            "Alamat: Sayap Kanan, Gedung Direktorat Pengembangan Usaha dan Bisnis,<br/>"
            "Komplek Kampus Unand, Limau Manis, Padang",
            address
        )
    ]

    top_header = Table(
        [
            [
                Table(
                    [[logo], [company_info]],
                    colWidths=[95*mm]
                ),
                Paragraph(
                    f"Padang, {tanggal.strftime('%-d %B %Y')}<br/><br/>"
                    "<b>Kepada Yth:</b><br/>"
                    "Bapak Pejabat Pembuat Komitmen (PPK)<br/>"
                    "Rektorat Universitas Andalas",
                    recipient
                )
            ]
        ],
        colWidths=[95*mm, 96*mm]
    )

    top_header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    elements.append(top_header)
    elements.append(Spacer(1, 2*mm))

    invoice_header = Table(
        [
            [
                Paragraph("I N V O I C E", invoice),
                Paragraph(f"Nomor: <b>{nomor} - AKSI/{tanggal.strftime('%m/%Y')}</b>", normal)
            ],
            [
                Paragraph(f"<b>Hal:</b> {hal}", normal),
                ""
            ]
        ],
        colWidths=[125*mm, 66*mm]
    )

    invoice_header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 0), (0, 0), "LEFT"),
        ("ALIGN", (1, 0), (1, 0), "LEFT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))

    elements.append(invoice_header)
    elements.append(Spacer(1, 3*mm))

    rows = [[
        Paragraph("No", header),
        Paragraph("Tanggal", header),
        Paragraph("LOKASI", header),
        Paragraph("Merek AC", header),
        Paragraph("Type", header),
        Paragraph("Unit", header),
        Paragraph("Uraian<br/>Pekerjaan", header),
        Paragraph("Stn", header),
        Paragraph("Vol", header),
        Paragraph("Harga<br/>Satuan (Rp)", header),
        Paragraph("Jumlah<br/>Harga (Rp)", header)
    ]]

    spans = []
    row_number = 1
    nomor = 1

    for item in data:
        details = item.details

        if not details:
            continue

        perangkat = item.perangkat
        gedung = item.gedung

        lokasi = (
            f"{gedung.gedung}, "
            f"Lantai {gedung.lantai}, "
            f"Ruang {gedung.ruang}"
        )

        start_row = row_number

        for index, detail in enumerate(details):
            if index == 0:
                main_data = [
                    Paragraph(str(nomor), center),
                    Paragraph(item.tgl_perbaikan.strftime("%d/%m/%Y"), center),
                    Paragraph(lokasi, cell),
                    Paragraph(perangkat.merek, cell),
                    Paragraph(perangkat.type, center),
                    Paragraph("1", center)
                ]
            else:
                main_data = ["", "", "", "", "", ""]

            harga = Decimal(detail.harga_satuan or 0)
            total = Decimal(detail.total_harga or 0)

            rows.append(
                main_data + [
                    Paragraph(detail.uraian, cell),
                    Paragraph(str(detail.satuan), center),
                    Paragraph(detail.vol, center),
                    Paragraph(
                        f"{harga:,.0f}".replace(",", "."),
                        right
                    ),
                    Paragraph(
                        f"{total:,.0f}".replace(",", "."),
                        right
                    )
                ]
            )

            row_number += 1

        end_row = row_number - 1

        if len(details) > 1:
            for col in range(6):
                spans.append(
                    ("SPAN", (col, start_row), (col, end_row))
                )

        nomor += 1

    widths = [
        6*mm,
        15*mm,
        28*mm,
        18*mm,
        14*mm,
        8*mm,
        36*mm,
        8*mm,
        10*mm,
        24*mm,
        24*mm
    ]

    table = Table(
        rows,
        colWidths=widths,
        repeatRows=1
    )

    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d9d9d9")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        *spans
    ]))

    elements.append(table)

    doc.build(elements)

    buffer.seek(0)

    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=False,
        download_name=f"laporan_perbaikan_{tanggal.strftime('%Y-%m-%d')}.pdf"
    )