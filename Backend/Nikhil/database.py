from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

engine = create_engine("sqlite:///neev.db", connect_args={"check_same_thread": False})

Base = declarative_base()


class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True)
    # Permanent unique ID — this is what goes in the QR. Never changes.
    worker_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, index=True)
    skills = Column(String)           # JSON string — can be updated freely
    nsqf_levels = Column(String)      # JSON string
    experience_years = Column(Integer, default=0)
    trust_score = Column(Float, default=0.0)
    ai_validation_score = Column(Float, default=0.0)
    # Permanent QR stored once, never regenerated
    qr_base64 = Column(Text, nullable=True)
    # Mandatory interview gate
    interview_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)
    worker_name = Column(String, index=True)
    rating = Column(Integer)
    feedback = Column(String)
    skill_level = Column(String)
    claimed_experience_years = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


class EmployerMCQ(Base):
    """
    Structured employer endorsement via MCQ.
    Replaces/supplements free-text reviews with scoreable answers.
    Recent entries carry higher weight in trust score calculation.
    """
    __tablename__ = "employer_mcqs"

    id = Column(Integer, primary_key=True)
    worker_name = Column(String, index=True)
    employer_name = Column(String)
    # Q1: Overall satisfaction 1-5
    q1_satisfaction = Column(Integer)
    # Q2: Handling of unexpected situations — text answer
    q2_unexpected = Column(String)
    # Q3: Would rehire? True/False
    q3_would_rehire = Column(Boolean)
    # Q4: Skill accuracy vs claimed — 1-5
    q4_skill_accuracy = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


class Verification(Base):
    __tablename__ = "verifications"

    id = Column(Integer, primary_key=True)
    worker_name = Column(String, index=True)
    worker_id = Column(String, index=True)   # track by stable ID too
    verified_at = Column(DateTime, default=datetime.utcnow)


class CommunityEndorsement(Base):
    __tablename__ = "endorsements"

    id = Column(Integer, primary_key=True)
    worker_name = Column(String, index=True)
    endorser_name = Column(String)
    endorser_role = Column(String)
    relationship_duration = Column(String)
    comment = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuthUser(Base):
    __tablename__ = "auth_users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String)  # "worker" ya "employer"
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
