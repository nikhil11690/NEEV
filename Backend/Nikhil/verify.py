from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from Nikhil.hasher import hash_dict
from Nikhil.database import get_db, Review, Verification
from datetime import datetime

router = APIRouter()

class VerifyPayload(BaseModel):
    data: dict
    hash: str

@router.post("/verify")
def verify_credential(payload: VerifyPayload, db: Session = Depends(get_db)):
    # Step 1: Hash check
    recalculated_hash = hash_dict(payload.data)
    is_valid = recalculated_hash == payload.hash

    if not is_valid:
        return {
            "valid": False,
            "reason": "Data has been tampered",
            "worker_data": None
        }

    worker_name = payload.data.get("name", "")

    # Step 2: Verification record save karo DB mein
    verification = Verification(
        worker_name=worker_name,
        qr_hash=payload.hash,
        verified_at=datetime.utcnow()
    )
    db.add(verification)
    db.commit()

    # Step 3: Employer reviews nikalo
    reviews = db.query(Review).filter(
        func.lower(Review.worker_name) == func.lower(worker_name)
    ).all()
    
    employer_score = 0.0
    reviews_list = []

    if reviews:
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
        employer_score = (avg_rating / 5) * 100
        reviews_list = [
            {
                "rating": r.rating,
                "feedback": r.feedback,
                "skill_level": r.skill_level
            }
            for r in reviews
        ]

    # Step 4: Trust score calculate karo
    # identity aur profile default values demo ke liye
    identity_score = 75.0
    profile_completeness = 60.0
    ai_score = payload.data.get("ai_validation_score", 70.0)

    if reviews:
        trust_score = (
            ai_score * 0.30 +
            employer_score * 0.40 +
            identity_score * 0.20 +
            profile_completeness * 0.10
        )
    else:
        trust_score = ai_score

    # Step 5: Fraud check
    fraud_flags = []
    claimed_years = payload.data.get("experience_years", 0)

    for review in reviews:
        if claimed_years >= 5 and review.skill_level == "beginner":
            fraud_flags.append(f"Claims {claimed_years} years but rated beginner")
        if review.rating <= 2 and claimed_years >= 7:
            fraud_flags.append(f"Low rating ({review.rating}/5) despite high experience claim")

    if len(fraud_flags) == 0:
        fraud_risk = "low"
    elif len(fraud_flags) == 1:
        fraud_risk = "medium"
    else:
        fraud_risk = "high"

    return {
        "valid": True,
        "worker_data": payload.data,
        "trust_score": round(trust_score, 2),
        "employer_reviews": reviews_list,
        "employer_reviews_count": len(reviews),
        "fraud_risk": fraud_risk,
        "fraud_flags": fraud_flags,
        "verified_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    }