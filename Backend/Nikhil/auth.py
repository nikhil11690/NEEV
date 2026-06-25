from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from Nikhil.database import get_db
import hashlib
import secrets
from datetime import datetime

router = APIRouter()

# Simple token store (in-memory — demo ke liye theek hai)
# Production mein Redis ya DB mein store karenge
active_tokens = {}

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str  # "worker" ya "employer"

class LoginRequest(BaseModel):
    email: str
    password: str

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token() -> str:
    return secrets.token_hex(32)

@router.post("/signup")
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    from Nikhil.database import AuthUser
    
    # Email already exists check
    existing = db.query(AuthUser).filter(
        AuthUser.email == request.email
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Role validate
    if request.role not in ["worker", "employer"]:
        raise HTTPException(status_code=400, detail="Role must be 'worker' or 'employer'")
    
    # New user create
    new_user = AuthUser(
        name=request.name,
        email=request.email,
        password_hash=hash_password(request.password),
        role=request.role,
        created_at=datetime.utcnow()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Token generate
    token = generate_token()
    active_tokens[token] = {
        "user_id": new_user.id,
        "name": new_user.name,
        "email": new_user.email,
        "role": new_user.role
    }
    
    return {
        "success": True,
        "token": token,
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "role": new_user.role
        },
        "message": "Account created successfully"
    }

@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    from Nikhil.database import AuthUser
    
    user = db.query(AuthUser).filter(
        AuthUser.email == request.email
    ).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Email not found")
    
    if user.password_hash != hash_password(request.password):
        raise HTTPException(status_code=401, detail="Wrong password")
    
    # Token generate
    token = generate_token()
    active_tokens[token] = {
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    }
    
    return {
        "success": True,
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }

@router.post("/logout")
def logout(token: str):
    if token in active_tokens:
        del active_tokens[token]
    return {"success": True, "message": "Logged out"}

@router.get("/me")
def get_me(token: str):
    if token not in active_tokens:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return active_tokens[token]