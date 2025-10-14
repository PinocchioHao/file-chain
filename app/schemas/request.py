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
    encrypted_aes_key: str | None = None


class FileRequestResponse(BaseModel):
    id: int
    file_id: int
    requester_id: int
    owner_id: int
    status: RequestStatus
    requester_ecc_public_key: str | None = None
    encrypted_aes_key: str | None = None
    file_name: str | None = None
    signature: str | None = None
    requester_username: str | None = None
    owner_username: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
