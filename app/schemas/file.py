from datetime import datetime
from pydantic import BaseModel


class FileBase(BaseModel):
    filename: str


class FileCreate(FileBase):
    stored_filename: str
    hash: str
    signature: str


class FileOut(FileBase):
    id: int
    stored_filename: str
    hash: str
    signature: str
    owner_id: int
    owner_name: str
    uploaded_at: datetime

    class Config:
        orm_mode = True
