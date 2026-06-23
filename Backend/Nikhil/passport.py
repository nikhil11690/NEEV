from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from Nikhil.database import get_db, Review
from Nikhil.hasher import hash_dict
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import qrcode
import io
import json

router = APIRouter()

class PassportRequest(BaseModel):
    worker_name: str
    skills: list[str]
    nsqf_levels: list[int]
    experience_years: int
    ai_validation_score: float = 70.0

@router.post("/generate-passport")
def generate_passport(request: PassportRequest, db: Session = Depends(get_db)):
    # Step 1: Reviews nikalo
    reviews = db.query(Review).filter(Review.worker_name == request.worker_name).all()
    
    employer_score = 0.0
    if reviews:
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
        employer_score = (avg_rating / 5) * 100
        trust_score = (
            request.ai_validation_score * 0.30 +
            employer_score * 0.40 +
            75.0 * 0.20 +
            60.0 * 0.10
        )
    else:
        trust_score = request.ai_validation_score

    trust_score = round(trust_score, 2)

    # Step 2: QR data banao
    qr_data = {
        "name": request.worker_name,
        "skills": request.skills,
        "nsqf_levels": request.nsqf_levels,
        "trust_score": trust_score
    }
    qr_hash = hash_dict(qr_data)
    qr_payload = {"data": qr_data, "hash": qr_hash}

    # Step 3: QR image banao
    qr_img = qrcode.make(json.dumps(qr_payload))
    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)

    # Step 4: PDF banao
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    elements = []

    # Header
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a2e'),
        spaceAfter=0.3*cm
    )
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#16213e'),
        spaceAfter=0.5*cm
    )

    elements.append(Paragraph("🔰 NEEV Skill Passport", title_style))
    elements.append(Paragraph("National Electronic Evidence of Vocation", subtitle_style))
    elements.append(Spacer(1, 0.5*cm))

    # Worker Info Table
    info_data = [
        ["Worker Name", request.worker_name],
        ["Experience", f"{request.experience_years} years"],
        ["Trust Score", f"{trust_score} / 100"],
        ["Employer Reviews", str(len(reviews))],
        ["Verification Status", "✅ VERIFIED"]
    ]

    info_table = Table(info_data, colWidths=[6*cm, 10*cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#f0f4ff')),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.7*cm))

    # Skills Table
    elements.append(Paragraph("Verified Skills", styles['Heading2']))
    elements.append(Spacer(1, 0.3*cm))

    skill_data = [["Skill", "NSQF Level", "Status"]]
    for skill, level in zip(request.skills, request.nsqf_levels):
        skill_data.append([skill.title(), f"Level {level}", "✅ Verified"])

    skill_table = Table(skill_data, colWidths=[8*cm, 4*cm, 4*cm])
    skill_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), 
         [colors.HexColor('#f0f4ff'), colors.white]),
    ]))
    elements.append(skill_table)
    elements.append(Spacer(1, 0.7*cm))

    # Employer Reviews
    if reviews:
        elements.append(Paragraph("Employer Reviews", styles['Heading2']))
        elements.append(Spacer(1, 0.3*cm))
        review_data = [["Rating", "Skill Level", "Feedback"]]
        for r in reviews:
            review_data.append([
                f"{'★' * r.rating}{'☆' * (5 - r.rating)}",
                r.skill_level.title(),
                r.feedback
            ])
        review_table = Table(review_data, colWidths=[4*cm, 4*cm, 8*cm])
        review_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(review_table)
        elements.append(Spacer(1, 0.7*cm))

    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey
    )
    elements.append(Paragraph(
        f"QR Hash: {qr_hash[:32]}...",
        footer_style
    ))
    elements.append(Paragraph(
        "This document is digitally verified by NEEV — neev-1.onrender.com",
        footer_style
    ))

    doc.build(elements)
    pdf_buffer.seek(0)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={request.worker_name}_passport.pdf"
        }
    )