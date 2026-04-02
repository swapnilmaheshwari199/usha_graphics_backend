from fastapi import APIRouter, HTTPException, Depends
# from schema.models import UserResponse
from services.database import get_connection
from utils.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/fetch-all-users")
def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()
    role = current_user.get("role")
    if role != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")
    try:
        cursor.execute(
            "SELECT * FROM users where role = 'customer'",
        )
        user = cursor.fetchall()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return [dict(row) for row in user]
    finally:
        cursor.close()
        conn.close()

