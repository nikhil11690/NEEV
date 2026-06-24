from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from Nikhil.database import get_db, Worker, Review, Verification, CommunityEndorsement, EmployerMCQ
from Aayush.employer_mcq import _recency_weighted_trust
from datetime import datetime, timezone
import json

router = APIRouter()


class VerifyByID(BaseModel):
    worker_id: str   # Scanned from QR


@router.post("/verify")
def verify_credential(payload: VerifyByID, db: Session = Depends(get_db)):
    """
    QR contains only worker_id (UUID).
    All data is fetched fresh from DB — so skill updates are reflected instantly
    without ever changing the QR.
    """
    worker = db.query(Worker).filter(Worker.worker_id == payload.worker_id).first()

    if not worker:
        return {"valid": False, "reason": "Worker not found", "worker_data": None}

    # Log this verification
    verification = Verification(
        worker_name=worker.name,
        worker_id=worker.worker_id,
        verified_at=datetime.utcnow()
    )
    db.add(verification)
    db.commit()

    # Fetch old-style text reviews
    reviews = db.query(Review).filter(
        func.lower(Review.worker_name) == func.lower(worker.name)
    ).order_by(Review.created_at.desc()).all()

    reviews_list = [
        {
            "rating": r.rating,
            "feedback": r.feedback,
            "skill_level": r.skill_level,
            "date": r.created_at.strftime("%b %Y")
        }
        for r in reviews
    ]

    # Fetch MCQ endorsements
    mcqs = db.query(EmployerMCQ).filter(
        EmployerMCQ.worker_name == worker.name
    ).order_by(EmployerMCQ.created_at.desc()).all()

    mcq_list = [
        {
            "employer": m.employer_name,
            "satisfaction": m.q1_satisfaction,
            "skill_accuracy": m.q4_skill_accuracy,
            "would_rehire": m.q3_would_rehire,
            "unexpected_handling": m.q2_unexpected,
            "date": m.created_at.strftime("%b %Y")
        }
        for m in mcqs
    ]

    # Recency-weighted trust (recalculated live so it's always fresh)
    trust_score = _recency_weighted_trust(mcqs, worker.ai_validation_score)

    # Community endorsements
    endorsements = db.query(CommunityEndorsement).filter(
        func.lower(CommunityEndorsement.worker_name) == func.lower(worker.name)
    ).order_by(CommunityEndorsement.created_at.desc()).all()

    endorsements_list = [
        {
            "endorser": e.endorser_name,
            "role": e.endorser_role,
            "duration": e.relationship_duration,
            "comment": e.comment,
            "date": e.created_at.strftime("%b %Y")
        }
        for e in endorsements
    ]

    # Fraud detection
    fraud_flags = []
    claimed_years = worker.experience_years or 0

    for review in reviews:
        if claimed_years >= 5 and review.skill_level == "beginner":
            fraud_flags.append(f"Claims {claimed_years} yrs experience but rated beginner")
        if review.rating <= 2 and claimed_years >= 7:
            fraud_flags.append(f"Low rating ({review.rating}/5) despite {claimed_years} yr claim")

    for mcq in mcqs:
        if mcq.q1_satisfaction <= 2 and claimed_years >= 5:
            fraud_flags.append(f"Low satisfaction ({mcq.q1_satisfaction}/5) from {mcq.employer_name}")
        if mcq.q4_skill_accuracy <= 2:
            fraud_flags.append(f"Skills did not match claims (rated by {mcq.employer_name})")

    fraud_risk = "low" if len(fraud_flags) == 0 else "medium" if len(fraud_flags) <= 2 else "high"

    try:
        skills = json.loads(worker.skills) if worker.skills else []
        nsqf_levels = json.loads(worker.nsqf_levels) if worker.nsqf_levels else []
    except Exception:
        skills = []
        nsqf_levels = []

    return {
        "valid": True,
        "worker_data": {
            "worker_id": worker.worker_id,
            "name": worker.name,
            "skills": skills,
            "nsqf_levels": nsqf_levels,
            "experience_years": worker.experience_years,
            "interview_completed": worker.interview_completed,
            "ai_validation_score": worker.ai_validation_score,
            "member_since": worker.created_at.strftime("%b %Y")
        },
        "trust_score": round(trust_score, 2),
        "employer_reviews": reviews_list,
        "employer_mcqs": mcq_list,
        "employer_reviews_count": len(reviews) + len(mcqs),
        "community_endorsements": endorsements_list,
        "fraud_risk": fraud_risk,
        "fraud_flags": fraud_flags,
        "verified_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    }


@router.get("/worker/{worker_id}")
def get_worker_profile(worker_id: str, db: Session = Depends(get_db)):
    """Public profile fetch by worker_id — used by frontend after interview."""
    worker = db.query(Worker).filter(Worker.worker_id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    try:
        skills = json.loads(worker.skills) if worker.skills else []
        nsqf_levels = json.loads(worker.nsqf_levels) if worker.nsqf_levels else []
    except Exception:
        skills = []
        nsqf_levels = []

    return {
        "worker_id": worker.worker_id,
        "name": worker.name,
        "skills": skills,
        "nsqf_levels": nsqf_levels,
        "experience_years": worker.experience_years,
        "trust_score": worker.trust_score,
        "ai_validation_score": worker.ai_validation_score,
        "interview_completed": worker.interview_completed,
        "qr_base64": worker.qr_base64,
        "member_since": worker.created_at.strftime("%b %Y")
    }
