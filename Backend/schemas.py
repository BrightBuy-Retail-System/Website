# Backend/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional

# Schema for incoming registration request
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    phonenum: Optional[str] = None

# Schema for incoming login request
class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

# Schema for response returned to client (never return password!)
class UserResponse(BaseModel):
    id: int
    email: str
    phonenum: Optional[str]

    class Config:
        from_attributes = True

# Schema for JWT Token response
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
