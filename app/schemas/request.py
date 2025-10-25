from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class RequestStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class FileRequestCreate(BaseModel):
    file_id: int


class FileRequestApprove(BaseModel):
    request_id: int
    decision: RequestStatus
    encrypted_aes_key: Optional[str] = None


class FileRequestResponse(BaseModel):
    id: int
    file_id: int
    requester_id: int
    owner_id: int
    status: RequestStatus
    requester_ecc_public_key: Optional[str] = None
    encrypted_aes_key: Optional[str] = None
    file_name: Optional[str] = None
    signature: Optional[str] = None
    requester_username: Optional[str] = None
    owner_username: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    tx_hash: Optional[str] = None
    owner_ecdsa_public_key: Optional[str] = None


    class Config:
        from_attributes = True