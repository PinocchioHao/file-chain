from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.user import UserCreate, UserResponse
from app.schemas.user import UserLogin
from app.services.user_service import login_user
from app.services.user_service import register_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    result = register_user(db, user_in)
    if not result:
        raise HTTPException(status_code=400, detail="User already exists")
    return UserResponse(
        id=result.id,
        username=result.username,
        ecc_public_key=result.ecc_public_key,
        ecdsa_public_key=result.ecdsa_public_key
    )


@router.post("/login")
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    token = login_user(db, user_in)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return token


@router.post("/logout")
def logout(token: str, db: Session = Depends(get_db)):
    # 简单：前端直接丢弃 token
    # 严格：把 token 加入黑名单
    return {"msg": "Logged out successfully, 前端清除token"}
