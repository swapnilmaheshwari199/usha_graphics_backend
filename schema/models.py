from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    company: str
    role: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    company: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

# class ItemCreate(BaseModel):
#     title: str
#     description: Optional[str] = None

# class ItemResponse(BaseModel):
#     id: int
#     title: str
#     description: Optional[str]
#     owner_id: int
#     created_at: datetime

