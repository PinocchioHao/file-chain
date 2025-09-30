from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class RequestStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class FileRequestCreate(BaseModel):
    file_id: int

class FileRequestResponse(BaseModel):
    id: int
    file_id: int
    requester_id: int
    owner_id: int
    status: RequestStatus
    owner_ecc_public_key: str | None = None
    encrypted_aes_key: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class FileRequestApprove(BaseModel):
    request_id: int
    decision: RequestStatus   # "approved" or "rejected"
