from sqlalchemy import Column, Integer, String, DateTime, func
from app.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    # ECC (密钥共享)
    ecc_public_key = Column(String(255), nullable=False)
    ecc_private_key = Column(String(255), nullable=False)

    # ECDSA (签名)
    ecdsa_public_key = Column(String(255), nullable=False)
    ecdsa_private_key = Column(String(255), nullable=False)

    created_at = Column(DateTime, server_default=func.now())
