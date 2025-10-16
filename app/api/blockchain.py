# app/api/blockchain.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.db import get_db
from app.models.blockchain import BlockchainRecord
from app.schemas.blockchain import BlockchainRecordOut

router = APIRouter(prefix="/blockchain", tags=["Blockchain"])

@router.get("/", response_model=list[BlockchainRecordOut])
def get_blockchain_records(
    db: Session = Depends(get_db),
    username: Optional[str] = Query(None, description="发起人用户名（模糊匹配，匹配 user_name 列）"),
    tx_hash: Optional[str] = Query(None, description="交易哈希（模糊匹配）"),
    action: Optional[str] = Query(None, description="动作筛选"),
    start_time: Optional[datetime] = Query(None, description="开始时间（ISO 格式）"),
    end_time: Optional[datetime] = Query(None, description="结束时间（ISO 格式）"),
):
    """
    简单直接的区块链记录查询：
    - username -> 模糊匹配 blockchain_record.user_name
    - tx_hash  -> 模糊匹配 blockchain_record.tx_hash
    - action   -> 精确匹配
    - start_time / end_time -> 时间范围筛选
    返回按 created_at 降序排序的记录列表
    """
    q = db.query(BlockchainRecord)

    if username:
        q = q.filter(BlockchainRecord.user_name.ilike(f"%{username}%"))
    if tx_hash:
        q = q.filter(BlockchainRecord.tx_hash.ilike(f"%{tx_hash}%"))
    if action:
        q = q.filter(BlockchainRecord.action == action)
    if start_time:
        q = q.filter(BlockchainRecord.created_at >= start_time)
    if end_time:
        q = q.filter(BlockchainRecord.created_at <= end_time)

    rows = q.order_by(BlockchainRecord.created_at.desc()).all()
    return rows
