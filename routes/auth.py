from fastapi import APIRouter, HTTPException, status
from schema.models import LoginRequest, TokenResponse, RegisterRequest, UserResponse
from services.database import get_connection
import os
from utils.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: RegisterRequest):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (data.username, data.email))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username or email already exists")
        hashed = hash_password(data.password)
        cursor.execute(
            "INSERT INTO users (username, email, hashed_password,company,role) VALUES (%s, %s, %s,%s,%s) RETURNING id, username, email, created_at",
            (data.username, data.email, hashed,data.company,"customer")
        )
        user = cursor.fetchone()
        conn.commit()
        return dict(user)
    finally:
        cursor.close()
        conn.close()

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, username, hashed_password, company, role FROM users WHERE email = %s", (data.email,))
        user = cursor.fetchone()
        if not user or not verify_password(data.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        username = user['username']
        company = user['company']
        role = user['role']
        token = create_access_token({"sub": user["username"], "user_id": user["id"], "company": company, "role": role})
        return {"access_token": token, "token_type": "bearer","username": username,"company":company,"role":role}
    finally:
        cursor.close()
        conn.close()


