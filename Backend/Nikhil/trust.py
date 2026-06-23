from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from Nikhil.database import get_db, Review

router = APIRouter()

class EmployerReview(BaseModel):
    worker_name: str
    rating: int
    feedback: str
    skill_level: str
    claimed_experience_years: int


@router.post("/add-review")
def add_review(review: EmployerReview, db: Session = Depends(get_db)):
    new_review = Review(
        worker_name=review.worker_name,
        rating=review.rating,
        feedback=review.feedback,
        skill_level=review.skill_level,
        claimed_experience_years=review.claimed_experience_years
    )
    db.add(new_review)
    db.commit()
    
    return {"message": "Review added", "worker": review.worker_name}


class TrustScoreRequest(BaseModel):
    worker_name: str
    ai_validation_score: float
    identity_score: float
    profile_completeness: float


@router.post("/trust-score")
def calculate_trust_score(request: TrustScoreRequest, db: Session = Depends(get_db)):
    reviews = db.query(Review).filter(
        func.lower(Review.worker_name) == func.lower(request.worker_name)
    ).all()
    
    employer_score = 0.0

    if reviews:
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
        employer_score = (avg_rating / 5) * 100
        trust_score = (
            request.ai_validation_score * 0.30 +
            employer_score * 0.40 +
            request.identity_score * 0.20 +
            request.profile_completeness * 0.10
        )
    else:
        trust_score = request.ai_validation_score

    return {
        "worker_name": request.worker_name,
        "trust_score": round(trust_score, 2),
        "employer_reviews_count": len(reviews),
        "employer_score": round(employer_score, 2)
    }


class FraudCheckRequest(BaseModel):
    worker_name: str
    claimed_experience_years: int


@router.post("/fraud-check")
def fraud_check(request: FraudCheckRequest, db: Session = Depends(get_db)):
    reviews = db.query(Review).filter(
        func.lower(Review.worker_name) == func.lower(request.worker_name)
    ).all()
    
    if not reviews:
        return {
            "fraud_risk": "unknown",
            "reason": "No employer reviews yet"
        }

    fraud_flags = []

    for review in reviews:
        if request.claimed_experience_years >= 5 and review.skill_level == "beginner":
            fraud_flags.append(
                f"Claims {request.claimed_experience_years} years but rated beginner by employer"
            )
        if review.rating <= 2 and request.claimed_experience_years >= 7:
            fraud_flags.append(
                f"Low rating ({review.rating}/5) despite high experience claim"
            )

    if len(fraud_flags) == 0:
        return {"fraud_risk": "low", "reason": "No inconsistencies found"}
    elif len(fraud_flags) == 1:
        return {"fraud_risk": "medium", "flags": fraud_flags}
    else:
        return {"fraud_risk": "high", "flags": fraud_flags}


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    from Nikhil.database import Worker, Verification
    
    total_reviews = db.query(Review).count()
    total_verifications = db.query(Verification).count()
    
    fraud_high = db.query(Review).filter(
        Review.skill_level == "beginner",
        Review.claimed_experience_years >= 5
    ).count()
    
    avg_rating = db.query(Review).all()
    avg = round(sum(r.rating for r in avg_rating) / len(avg_rating), 2) if avg_rating else 0
    
    return {
        "total_reviews": total_reviews,
        "total_verifications": total_verifications,
        "fraud_cases_detected": fraud_high,
        "average_employer_rating": avg,
        "platform": "NEEV Skill Passport",
        "status": "live"
    }