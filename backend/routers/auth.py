from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
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
bearer_scheme = HTTPBearer()

# ── helpers ──────────────────────────────────────────────────────────────────

def create_access_token(user_id: int) -> str:
    """Create a JWT that expires in 30 minutes."""
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }
    return jwt.encode(payload, os.getenv("SECRET_KEY"), algorithm="HS256")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: Session = Depends(get_db)
):
    """Read the JWT from the request header and return the logged-in user."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
        user_id = int(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# ── endpoints ─────────────────────────────────────────────────────────────────

@router.post("/signup", response_model=UserResponse, status_code=201)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = pwd_context.hash(request.password)
    new_user = User(email=request.email, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not pwd_context.verify(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(user.id)
    return TokenResponse(access_token=token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
