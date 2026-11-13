import os
from io import BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode import qr

def generate_pdf_ticket(booking_data: dict) -> bytes:
    """
    Generates an enterprise-grade RedBus E-Ticket / Boarding Pass PDF in memory.
    Returns bytes compatible with PDF magic bytes %PDF.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    story = []
    styles = getSampleStyleSheet()

    # Custom Palette
    primary_red = colors.HexColor("#D84E55")
    dark_text = colors.HexColor("#1A1A1A")
    gray_bg = colors.HexColor("#F8F9FA")
    border_color = colors.HexColor("#E2E8F0")

    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=primary_red,
        spaceAfter=4
    )
    
    subhead_style = ParagraphStyle(
        'SubheadStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor("#64748B")
    )

    label_style = ParagraphStyle(
        'LabelStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=colors.HexColor("#64748B")
    )

    val_style = ParagraphStyle(
        'ValStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=dark_text
    )

    # 1. Header Banner
    pnr = booking_data.get("pnr", "RB-99882211")
    story.append(Paragraph("redBus", header_style))
    story.append(Paragraph("E-TICKET / BOARDING PASS - CONFIRMED", subhead_style))
    story.append(Spacer(1, 15))
    story.append(HRFlowable(width="100%", thickness=2, color=primary_red, spaceAfter=15))

    # 2. Main Ticket Meta
    pnr_table_data = [
        [
            Paragraph("BOOKING REFERENCE (PNR)", label_style),
            Paragraph("JOURNEY DATE", label_style),
            Paragraph("TICKET STATUS", label_style)
        ],
        [
            Paragraph(f"<font color='#D84E55' size=14><b>{pnr}</b></font>", val_style),
            Paragraph(str(booking_data.get("travel_date", datetime.now().strftime("%d %b %Y"))), val_style),
            Paragraph("<font color='#2E7D32'><b>CONFIRMED [VALID]</b></font>", val_style)
        ]
    ]
    t_meta = Table(pnr_table_data, colWidths=[200, 180, 160])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), gray_bg),
        ('BOX', (0,0), (-1,-1), 1, border_color),
        ('PADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 15))

    # 3. Route & Bus Operator Details
    src_city = booking_data.get("src") or booking_data.get("source", "Bangalore")
    dst_city = booking_data.get("dst") or booking_data.get("destination", "Chennai")
    dep_time = booking_data.get("departure", "09:00 PM")
    arr_time = booking_data.get("arrival", "05:30 AM")

    route_data = [
        [
            Paragraph("BUS OPERATOR & SERVICE", label_style),
            Paragraph("FROM (SOURCE)", label_style),
            Paragraph("TO (DESTINATION)", label_style)
        ],
        [
            Paragraph(f"<b>{booking_data.get('bus_name', 'SRS Travels')}</b><br/><font size=9 color='#64748B'>{booking_data.get('bus_type', 'Multi-Axle Volvo AC Sleeper')}</font>", val_style),
            Paragraph(f"<b>{src_city}</b><br/><font size=9 color='#64748B'>Boarding: {dep_time}</font>", val_style),
            Paragraph(f"<b>{dst_city}</b><br/><font size=9 color='#64748B'>Dropping: {arr_time}</font>", val_style)
        ]
    ]
    t_route = Table(route_data, colWidths=[200, 170, 170])
    t_route.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('BOX', (0,0), (-1,-1), 1, border_color),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    story.append(t_route)
    story.append(Spacer(1, 15))

    # 4. Passenger & Seat Information
    seat_str = booking_data.get("seat") or booking_data.get("seat_no", "L2")
    passengers = booking_data.get("passengers", [{
        "name": booking_data.get("passenger_name", "Ranjith Kumar"),
        "gender": booking_data.get("passenger_gender", "Male"),
        "age": booking_data.get("passenger_age", 24),
        "seat": seat_str
    }])

    pass_table_rows = [
        [
            Paragraph("PASSENGER NAME", label_style),
            Paragraph("GENDER / AGE", label_style),
            Paragraph("SEAT NUMBER", label_style),
            Paragraph("BASE FARE", label_style)
        ]
    ]
    total_fare = booking_data.get("fare", 950)
    fare_per_seat = total_fare // max(len(passengers), 1)

    for p in passengers:
        pass_table_rows.append([
            Paragraph(f"<b>{p.get('name')}</b>", val_style),
            Paragraph(f"{p.get('gender')} / {p.get('age')} yrs", val_style),
            Paragraph(f"<font color='#D84E55'><b>Seat {p.get('seat')}</b></font>", val_style),
            Paragraph(f"INR {fare_per_seat}", val_style)
        ])

    pass_table_rows.append([
        Paragraph("<b>TOTAL AMOUNT PAID (INCL. GST)</b>", val_style),
        Paragraph("", val_style),
        Paragraph("", val_style),
        Paragraph(f"<font color='#D84E55' size=13><b>INR {total_fare}</b></font>", val_style)
    ])

    t_pass = Table(pass_table_rows, colWidths=[200, 140, 100, 100])
    t_pass.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), gray_bg),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#FEF2F2")),
        ('LINEBELOW', (0,0), (-1,0), 1, primary_red),
        ('BOX', (0,0), (-1,-1), 1, border_color),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(t_pass)
    story.append(Spacer(1, 20))

    # 5. Security QR Code & Verification Block
    qr_code = qr.QrCodeWidget(f"REDBUS:PNR={pnr};SEAT={seat_str};PASSENGER={booking_data.get('passenger_name','Ranjith')};STATUS=CONFIRMED")
    qr_drawing = Drawing(80, 80)
    qr_drawing.add(qr_code)

    terms_text = (
        "<b>Important Travel Instructions:</b><br/>"
        "&bull; Please carry this E-Ticket and a valid Government Photo ID during boarding.<br/>"
        "&bull; Reporting time is 15 minutes prior to the scheduled departure time.<br/>"
        "&bull; 24x7 Customer Support: 1800-419-7332 | support@redbus.in<br/>"
        "&bull; Generated automatically by RedBus AI &amp; Test Automation Architecture."
    )
    terms_para = Paragraph(terms_text, ParagraphStyle('Terms', fontName='Helvetica', fontSize=8, leading=11, textColor=colors.HexColor("#475569")))

    qr_table = Table([[qr_drawing, terms_para]], colWidths=[100, 440])
    qr_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 5),
        ('BACKGROUND', (0,0), (-1,-1), gray_bg),
        ('BOX', (0,0), (-1,-1), 1, border_color)
    ]))
    story.append(qr_table)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
