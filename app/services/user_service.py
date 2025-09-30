from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import get_password_hash
from app.core.crypto import generate_ecc_keypair
from app.schemas.user import UserCreate
from app.core.security import verify_password, create_access_token
from app.schemas.user import UserLogin


def login_user(db: Session, user_in: UserLogin):
    user = db.query(User).filter(User.username == user_in.username).first()
    if not user:
        return None
    if not verify_password(user_in.password, user.password_hash):
        return None

    token = create_access_token({"sub": str(user.id)})
    return token


def register_user(db: Session, user_in: UserCreate):
    # 1. 检查用户是否存在
    existing = db.query(User).filter(User.username == user_in.username).first()
    if existing:
        return None

    # 2. TODO 密码 hash - 报错，有问题
    # hashed_pw = get_password_hash(user_in.password)

    # 3. TODO 生成 ECC/ECDSA 密钥对 - 生成的不完整
    # ecc_pub, ecc_priv = generate_ecc_keypair()
    # ecdsa_pub, ecdsa_priv = generate_ecdsa_keypair()

    # 4. 存数据库
    new_user = User(
        username=user_in.username,
        password_hash=user_in.password,
        ecc_public_key="ecc_pub",
        ecc_private_key="ecc_priv",
        ecdsa_public_key="ecdsa_pub",
        ecdsa_private_key="ecdsa_priv"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
