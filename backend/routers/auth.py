from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.user import SignupRequest,UserResponse
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"])

@router.post("/signup",response_model=UserResponse,status_code=201)
def signup(request: SignupRequest,db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400,detail="Email already registered")
    hashed = pwd_context.hash(request.password)

    new_user = User(email=request.email,hashed_password= hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
