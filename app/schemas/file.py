from pydantic import BaseModel
from datetime import datetime

class FileBase(BaseModel):
    filename: str

class FileCreate(FileBase):
    stored_filename: str
    hash: str
    signature: str
    file_ecc_aes_key: str

class FileOut(FileBase):
    id: int
    stored_filename: str
    hash: str
    signature: str
    file_ecc_aes_key: str
    owner_id: int
    owner_name: str
    uploaded_at: datetime

    class Config:
        orm_mode = True
