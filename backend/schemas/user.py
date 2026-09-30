from datetime import datetime
from pydantic import BaseModel,EmailStr,Field

class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(...,min_length = 8)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str 

class UserResponse(BaseModel):
    id : int
    email : EmailStr
    created_at: datetime