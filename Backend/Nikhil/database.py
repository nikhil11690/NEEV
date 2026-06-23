from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

engine = create_engine("sqlite:///neev.db", connect_args={"check_same_thread": False})

Base = declarative_base()

class Worker(Base):
    __tablename__ = "workers"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)
    skills = Column(String)  # JSON string
    experience_years = Column(Integer, default=0)
    trust_score = Column(Float, default=0.0)
    ai_validation_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True)
    worker_name = Column(String, index=True)
    rating = Column(Integer)
    feedback = Column(String)
    skill_level = Column(String)
    claimed_experience_years = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class Verification(Base):
    __tablename__ = "verifications"
    
    id = Column(Integer, primary_key=True)
    worker_name = Column(String, index=True)
    qr_hash = Column(String)
    verified_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()