from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from Nikhil.database import get_db, CommunityEndorsement

router = APIRouter()

class EndorsementRequest(BaseModel):
    worker_name: str
    endorser_name: str
    endorser_role: str
    relationship_duration: str
    comment: str

@router.post("/community-verify")
def add_endorsement(request: EndorsementRequest, db: Session = Depends(get_db)):
    new_endorsement = CommunityEndorsement(
        worker_name=request.worker_name,
        endorser_name=request.endorser_name,
        endorser_role=request.endorser_role,
        relationship_duration=request.relationship_duration,
        comment=request.comment
    )
    db.add(new_endorsement)
    db.commit()

    return {
        "message": "Endorsement added",
        "worker": request.worker_name,
        "endorsed_by": request.endorser_name
    }


@router.get("/endorsements/{worker_name}")
def get_endorsements(worker_name: str, db: Session = Depends(get_db)):
    endorsements = db.query(CommunityEndorsement).filter(
        CommunityEndorsement.worker_name == worker_name
    ).all()

    return {
        "worker_name": worker_name,
        "endorsement_count": len(endorsements),
        "endorsements": [
            {
                "endorser_name": e.endorser_name,
                "endorser_role": e.endorser_role,
                "relationship_duration": e.relationship_duration,
                "comment": e.comment
            }
            for e in endorsements
        ]
    }