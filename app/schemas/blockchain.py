# app/schemas/blockchain.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any

class BlockchainRecordOut(BaseModel):
    id: int
    tx_hash: str
    user_id: int
    user_name: str
    action: str
    payload: Optional[Any] = None
    created_at: datetime

    class Config:
        orm_mode = True
