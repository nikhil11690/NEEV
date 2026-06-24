from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from Nikhil.database import get_db, Worker, EmployerMCQ

router = APIRouter()


class MCQSubmission(BaseModel):
    worker_name: str
    employer_name: str
    q1_satisfaction: int        # 1–5: Overall satisfaction
    q2_unexpected: str          # Text: how did worker handle unexpected situations
    q3_would_rehire: bool       # Yes/No
    q4_skill_accuracy: int      # 1–5: Did skills match what was claimed


def _recency_weighted_trust(mcqs: list[EmployerMCQ], ai_score: float) -> float:
    """
    Trust score formula:
    - Each MCQ gets a weight = 1 / (days_since_submission + 1)
      → recent MCQs matter more than old ones
    - Raw MCQ score = weighted avg of (q1 + q4) / 2 + rehire bonus
    - Final trust = 30% AI interview + 70% employer MCQ score
    """
    if not mcqs:
        return round(ai_score, 2)

    now = datetime.now(timezone.utc)
    total_weight = 0.0
    weighted_sum = 0.0

    for mcq in mcqs:
        # Make timezone-aware for comparison
        created = mcq.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)

        days_ago = max((now - created).days, 0)
        weight = 1.0 / (days_ago + 1)   # Day 0 = weight 1.0, Day 30 = weight ~0.032

        # Score this MCQ out of 100
        satisfaction_score = (mcq.q1_satisfaction / 5) * 100
        accuracy_score = (mcq.q4_skill_accuracy / 5) * 100
        rehire_bonus = 10 if mcq.q3_would_rehire else 0
        mcq_score = (satisfaction_score + accuracy_score) / 2 + rehire_bonus
        mcq_score = min(mcq_score, 100)  # cap at 100

        weighted_sum += mcq_score * weight
        total_weight += weight

    employer_score = weighted_sum / total_weight if total_weight > 0 else 0.0

    # Final blended trust score
    trust = (ai_score * 0.30) + (employer_score * 0.70)
    return round(min(trust, 100), 2)


@router.post("/employer-mcq")
def submit_employer_mcq(mcq: MCQSubmission, db: Session = Depends(get_db)):
    """
    Employer submits 4 MCQ answers about a worker after hiring them.
    Trust score is recalculated immediately with recency weighting.
    """
    # Validate score ranges
    if not (1 <= mcq.q1_satisfaction <= 5):
        raise HTTPException(status_code=400, detail="q1_satisfaction must be 1–5")
    if not (1 <= mcq.q4_skill_accuracy <= 5):
        raise HTTPException(status_code=400, detail="q4_skill_accuracy must be 1–5")

    worker = db.query(Worker).filter(
        Worker.name == mcq.worker_name
    ).first()

    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found in database")

    # Save MCQ
    new_mcq = EmployerMCQ(
        worker_name=mcq.worker_name,
        employer_name=mcq.employer_name,
        q1_satisfaction=mcq.q1_satisfaction,
        q2_unexpected=mcq.q2_unexpected,
        q3_would_rehire=mcq.q3_would_rehire,
        q4_skill_accuracy=mcq.q4_skill_accuracy,
        created_at=datetime.utcnow()
    )
    db.add(new_mcq)
    db.flush()  # get the MCQ in DB before recalculating

    # Recalculate trust with ALL MCQs for this worker (recency-weighted)
    all_mcqs = db.query(EmployerMCQ).filter(
        EmployerMCQ.worker_name == mcq.worker_name
    ).order_by(EmployerMCQ.created_at.asc()).all()

    new_trust = _recency_weighted_trust(all_mcqs, worker.ai_validation_score)
    worker.trust_score = new_trust
    db.commit()

    return {
        "success": True,
        "worker_name": mcq.worker_name,
        "new_trust_score": new_trust,
        "total_mcq_reviews": len(all_mcqs),
        "message": "Review submitted and trust score updated."
    }


@router.get("/employer-mcqs/{worker_name}")
def get_worker_mcqs(worker_name: str, db: Session = Depends(get_db)):
    """Fetch all MCQ reviews for a worker (for display on verify page)."""
    mcqs = db.query(EmployerMCQ).filter(
        EmployerMCQ.worker_name == worker_name
    ).order_by(EmployerMCQ.created_at.desc()).all()

    return {
        "worker_name": worker_name,
        "total": len(mcqs),
        "reviews": [
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
    }
