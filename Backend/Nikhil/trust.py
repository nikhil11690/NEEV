from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

reviews_db = {} 
#  //abhi in memory h kyuki postresql roadmap mein h 

class EmployerReview(BaseModel):
    worker_name: str
    rating: int
    feedback: str
    skill_level: str
    claimed_experience_years: int


@router.post("/add-review")
def add_review(review: EmployerReview):
    if review.worker_name not in reviews_db:
        reviews_db[review.worker_name] = []
    
    reviews_db[review.worker_name].append({
        "rating": review.rating,
        "feedback": review.feedback,
        "skill_level": review.skill_level,
        "claimed_experience_years": review.claimed_experience_years
    })
    
    return {"message": "Review added", "worker": review.worker_name}

class TrustScoreRequest(BaseModel):
    worker_name: str
    ai_validation_score: float
    identity_score: float
    profile_completeness: float


@router.post("/trust-score")
def calculate_trust_score(request: TrustScoreRequest):
    employer_score = 0.0

    if request.worker_name in reviews_db:
        reviews = reviews_db[request.worker_name]
        avg_rating = sum(r["rating"] for r in reviews) / len(reviews)
        employer_score = (avg_rating / 5) * 100

    if request.worker_name in reviews_db:
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
        "employer_reviews_count": len(reviews_db.get(request.worker_name, [])),
        "employer_score": round(employer_score, 2)
    }
class FraudCheckRequest(BaseModel):
    worker_name: str
    claimed_experience_years: int


@router.post("/fraud-check")
def fraud_check(request: FraudCheckRequest):
    if request.worker_name not in reviews_db:
        return {
            "fraud_risk": "unknown",
            "reason": "No employer reviews yet"
        }

    reviews = reviews_db[request.worker_name]
    
    fraud_flags = []

    for review in reviews:
        if request.claimed_experience_years >= 5 and review["skill_level"] == "beginner":
            fraud_flags.append(
                f"Claims {request.claimed_experience_years} years but rated beginner by employer"
            )

        if review["rating"] <= 2 and request.claimed_experience_years >= 7:
            fraud_flags.append(
                f"Low rating ({review['rating']}/5) despite high experience claim"
            )

    if len(fraud_flags) == 0:
        return {"fraud_risk": "low", "reason": "No inconsistencies found"}
    elif len(fraud_flags) == 1:
        return {"fraud_risk": "medium", "flags": fraud_flags}
    else:
        return {"fraud_risk": "high", "flags": fraud_flags}