from sqlalchemy.orm import Session

from app.core.security import verify_password, create_access_token
from app.models.user import User
from app.schemas.user import UserCreate
from app.schemas.user import UserLogin


def login_user(db: Session, user_in: UserLogin):
    user = db.query(User).filter(User.username == user_in.username).first()
    if not user:
        return None
    if not verify_password(user_in.password, user.password_hash):
        return None

    token = create_access_token({"sub": str(user.id)})

    # 返回 access_token + 用户信息
    return {
        "access_token": token,
        "token_type": "bearer",
        "username": user.username,
        "id": user.id
    }


def register_user(db: Session, user_in: UserCreate):
    # 1. 检查用户是否存在
    existing = db.query(User).filter(User.username == user_in.username).first()
    if existing:
        return None

    # 4. 存数据库（仅存公钥）
    new_user = User(
        username=user_in.username,
        password_hash=hashed_pw,
        ecc_public_key=user_in.ecc_public_key,
        ecdsa_public_key=user_in.ecdsa_public_key,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    # return new_user, ecc_private_key, ecdsa_private_key
    return new_user
