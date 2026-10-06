from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.user import SignupRequest, UserResponse, LoginRequest, TokenResponse
from passlib.context import CryptContext
from jose import jwt
import os
from datetime import datetime, timedelta, timezone

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"])

# ── helpers ──────────────────────────────────────────────────────────────────

def create_access_token(user_id: int) -> str:
    """Create a JWT that expires in 30 minutes."""
    payload = {
        "sub": str(user_id),          # "sub" = subject = who this token is for
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)  # expiry time
    }
    return jwt.encode(payload, os.getenv("SECRET_KEY"), algorithm="HS256")

# ── endpoints ─────────────────────────────────────────────────────────────────

@router.post("/signup", response_model=UserResponse, status_code=201)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    # Is this email already taken?
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password, then save the user
    hashed = pwd_context.hash(request.password)
    new_user = User(email=request.email, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # Step 1: find the user by email
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Step 2: check the password matches the stored hash
    if not pwd_context.verify(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Step 3: create and return a token
    token = create_access_token(user.id)
    return TokenResponse(access_token=token, token_type="bearer")
