# app/core/security.py
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User

# 使用 HTTPBearer 替代 OAuth2PasswordBearer，避免 Swagger 误认为 OAuth2 密码流
security = HTTPBearer()

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

SECRET_KEY = "supersecret"  # 改成 config.py 读取（保持你们原注释/常量不动）
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain, hashed):
    """
    首选使用 bcrypt 校验；
    若 hashed 不是有效 bcrypt（例如旧数据存的是明文），则回退到明文比对，保证老用户临时可登录。
    你们把旧密码全部迁移为 hash 后，可改回：return pwd_context.verify(plain, hashed)
    """
    # try:
    #     # 如果 hashed 是合法的 hash，会直接在这里校验并返回 True/False
    #     return pwd_context.verify(plain, hashed)
    # except Exception:
    #     # 兼容旧数据（明文存储的情况）：临时回退
    #     return plain == hashed

    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 从 HTTPAuthorizationCredentials 对象中提取真正的 token
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user
