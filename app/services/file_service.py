import hashlib
import os

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.file import File

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def save_file_to_disk(file: UploadFile, stored_filename: str):
    file_path = os.path.join(UPLOAD_DIR, stored_filename)
    content = await file.read()  # 现在可以 await
    with open(file_path, "wb") as f:
        f.write(content)
    return file_path, content


def save_bytes_to_disk(content: bytes, stored_filename: str) -> str:
    file_path = os.path.join(UPLOAD_DIR, stored_filename)
    with open(file_path, "wb") as f:
        f.write(content)
    return file_path


def create_file_record(db: Session, owner_id: int, owner_name: str, filename: str, stored_filename: str, signature: str,
                       content: bytes):
    file_hash = hashlib.sha256(content).hexdigest()

    db_file = File(
        filename=filename,
        stored_filename=stored_filename,
        hash=file_hash,
        signature=signature,
        owner_id=owner_id,
        owner_name=owner_name
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file


def list_files(db: Session):
    return db.query(File).all()


def get_file(db: Session, file_id: int):
    return db.query(File).filter(File.id == file_id).first()
