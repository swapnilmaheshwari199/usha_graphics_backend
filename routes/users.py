from fastapi import APIRouter, HTTPException, Depends
from schema.models import UserResponse
from services.database import get_connection
from utils.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, username, email, created_at FROM users WHERE id = %s",
            (current_user["user_id"],)
        )
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return dict(user)
    finally:
        cursor.close()
        conn.close()