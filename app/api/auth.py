from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import register_user
from app.schemas.user import UserLogin
from app.services.user_service import login_user
from app.db import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    user = register_user(db, user_in)
    if not user:
        raise HTTPException(status_code=400, detail="User already exists")
    return user


@router.post("/login")
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    token = login_user(db, user_in)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": token, "token_type": "bearer"}


@router.post("/logout")
def logout(token: str, db: Session = Depends(get_db)):
    # 简单：前端直接丢弃 token
    # 严格：把 token 加入黑名单
    return {"msg": "Logged out successfully, 前端清除token"}

