import os
import hashlib
from sqlalchemy.orm import Session
from app.models.file import File

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_file_to_disk(file, stored_filename: str) -> str:
    file_path = os.path.join(UPLOAD_DIR, stored_filename)
    with open(file_path, "wb") as f:
        content = file.file.read()
        f.write(content)
    return file_path, content

def create_file_record(db: Session, owner_id: int, owner_name: str, filename: str, stored_filename: str, signature, ecc_aes_key, content: bytes):
    file_hash = hashlib.sha256(content).hexdigest()

    db_file = File(
        filename=filename,
        stored_filename=stored_filename,
        hash=file_hash,
        signature=signature,
        file_ecc_aes_key=ecc_aes_key,
        owner_id=owner_id,
        owner_name = owner_name
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

def list_files(db: Session):
    return db.query(File).all()

def get_file(db: Session, file_id: int):
    return db.query(File).filter(File.id == file_id).first()
