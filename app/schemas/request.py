from datetime import datetime
from enum import Enum
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
    encrypted_aes_key: str


class FileRequestResponse(BaseModel):
    id: int
    file_id: int
    requester_id: int
    owner_id: int
    status: RequestStatus
    requester_ecc_public_key: str
    encrypted_aes_key: str
    file_name: str
    signature: str
    requester_username: str
    owner_username: str
    created_at: datetime
    updated_at: datetime
    tx_hash: str

    class Config:
        from_attributes = True