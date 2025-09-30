from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from app.db import Base

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)          # 原始文件名
    stored_filename = Column(String(255), nullable=False)   # 保存到磁盘的文件名
    hash = Column(String(64), nullable=False)               # 文件SHA-256
    signature = Column(Text, nullable=False)                # 文件签名
    file_ecc_aes_key = Column(Text, nullable=False)         # ECC加密后的AES密钥
    owner_id = Column(Integer, nullable=False)
    owner_name = Column(String(100), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
