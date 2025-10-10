from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import get_password_hash
from app.core.crypto import (
    generate_ecc_keypair,
    serialize_private_key_der_b64,
    serialize_public_key_der_b64,
)
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

    # 2. TODO 密码 hash - 报错，有问题（已实现：使用 get_password_hash 进行 bcrypt 哈希）
    hashed_pw = get_password_hash(user_in.password)

    # 3. TODO 生成 ECC/ECDSA 密钥对 - 生成的不完整（已实现：两套 EC(SECP256R1)，私钥仅返回给客户端）
    ecc_priv_obj, ecc_pub_obj = generate_ecc_keypair()
    ecdsa_priv_obj, ecdsa_pub_obj = generate_ecc_keypair()

    ecc_public_key = serialize_public_key_der_b64(ecc_pub_obj)
    ecc_private_key = serialize_private_key_der_b64(ecc_priv_obj)
    ecdsa_public_key = serialize_public_key_der_b64(ecdsa_pub_obj)
    ecdsa_private_key = serialize_private_key_der_b64(ecdsa_priv_obj)

    # 4. 存数据库（仅存公钥）
    new_user = User(
        username=user_in.username,
        password_hash=hashed_pw,
        ecc_public_key=ecc_public_key,
        ecdsa_public_key=ecdsa_public_key,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user, ecc_private_key, ecdsa_private_key
