# app/models/blockchain.py
from sqlalchemy import Column, BigInteger, String, JSON, DateTime
from sqlalchemy.sql import func
from app.db import Base

class BlockchainRecord(Base):
    __tablename__ = "blockchain_record"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tx_hash = Column(String(66), nullable=False)
    user_id = Column(BigInteger, nullable=False)
    user_name = Column(String(255), nullable=False)
    action = Column(String(50), nullable=False)          # upload / request_submit / request_approve / key_share
    payload = Column(JSON)                                # tx['data'] 对应业务信息
    created_at = Column(DateTime(timezone=True), server_default=func.now())
