from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json
import qrcode
import io
import base64
from Nikhil.database import get_db, Worker

router = APIRouter()


# ── Request models ────────────────────────────────────────────────────────────

class WorkerCredential(BaseModel):
    name: str
    skills: list[str]
    nsqf_levels: list[int]
    experience_years: int = 0
    ai_validation_score: float = 0.0   # set by validate.py after interview

class SkillUpdateRequest(BaseModel):
    worker_id: str          # permanent ID — frontend stores this after first generation
    new_skills: list[str]
    new_nsqf_levels: list[int]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_qr_base64(worker_id: str) -> str:
    """
    QR encodes ONLY the worker_id.
    All profile data lives in DB and is fetched at verify time.
    This means skills can change freely without breaking the QR.
    """
    qr_img = qrcode.make(worker_id)
    buf = io.BytesIO()
    qr_img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/generate-credential")
def generate_credential(worker: WorkerCredential, db: Session = Depends(get_db)):
    """
    First call  → creates worker row, generates permanent QR, stores it.
    Repeat call → returns the SAME stored QR (worker_id never changes).
    Interview gate: if ai_validation_score == 0, credential is issued but
    interview_completed stays False — frontend should enforce interview first.
    """
    existing = db.query(Worker).filter(
        Worker.name == worker.name
    ).first()

    if existing:
        # Worker already exists — return stored QR, never regenerate
        return {
            "worker_id": existing.worker_id,
            "qr_code_base64": existing.qr_base64,
            "interview_completed": existing.interview_completed,
            "message": "existing_worker"
        }

    # New worker — generate permanent QR
    import uuid
    new_id = str(uuid.uuid4())
    qr_b64 = _make_qr_base64(new_id)

    interview_done = worker.ai_validation_score > 0

    new_worker = Worker(
        worker_id=new_id,
        name=worker.name,
        skills=json.dumps(worker.skills),
        nsqf_levels=json.dumps(worker.nsqf_levels),
        experience_years=worker.experience_years,
        ai_validation_score=worker.ai_validation_score,
        trust_score=worker.ai_validation_score,   # initial trust = AI score
        qr_base64=qr_b64,
        interview_completed=interview_done
    )
    db.add(new_worker)
    db.commit()
    db.refresh(new_worker)

    return {
        "worker_id": new_worker.worker_id,
        "qr_code_base64": qr_b64,
        "interview_completed": interview_done,
        "message": "new_worker"
    }


@router.post("/update-skills")
def update_skills(req: SkillUpdateRequest, db: Session = Depends(get_db)):
    """
    Worker can add new skills (e.g. learned driving).
    QR stays the same — only DB profile changes.
    """
    worker = db.query(Worker).filter(Worker.worker_id == req.worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    worker.skills = json.dumps(req.new_skills)
    worker.nsqf_levels = json.dumps(req.new_nsqf_levels)
    db.commit()

    return {
        "success": True,
        "worker_id": worker.worker_id,
        "updated_skills": req.new_skills,
        "qr_unchanged": True,
        "message": "Skills updated. QR code remains the same."
    }


@router.post("/complete-interview")
def mark_interview_complete(
    worker_id: str,
    ai_score: float,
    db: Session = Depends(get_db)
):
    """Called by validate.py flow once interview is done and scored."""
    worker = db.query(Worker).filter(Worker.worker_id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    worker.interview_completed = True
    worker.ai_validation_score = ai_score
    db.commit()

    return {"success": True, "interview_completed": True, "ai_score": ai_score}
