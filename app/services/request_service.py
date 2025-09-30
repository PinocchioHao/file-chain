from sqlalchemy.orm import Session
from app.models.request import FileRequest, RequestStatus
from app.models.user import User
from app.models.file import File
from app.schemas.request import FileRequestCreate, FileRequestApprove

def create_request(db: Session, requester_id: int, req: FileRequestCreate):
    # 找文件 owner_id
    file = db.query(File).filter(File.id == req.file_id).first()
    if not file:
        return None
    new_req = FileRequest(
        file_id=req.file_id,
        requester_id=requester_id,
        owner_id=file.owner_id
    )
    db.add(new_req)
    db.commit()
    db.refresh(new_req)
    return new_req

def get_requests_by_requester(db: Session, requester_id: int):
    return db.query(FileRequest).filter(FileRequest.requester_id == requester_id).all()

def get_requests_by_owner(db: Session, owner_id: int):
    return db.query(FileRequest).filter(FileRequest.owner_id == owner_id, FileRequest.status == RequestStatus.pending).all()

def approve_request(db: Session, approve_data: FileRequestApprove, owner_id: int):
    req = db.query(FileRequest).filter(FileRequest.id == approve_data.request_id, FileRequest.owner_id == owner_id).first()
    if not req:
        return None

    if approve_data.decision == RequestStatus.approved:
        req.status = RequestStatus.approved
        # 查 owner 公钥
        owner = db.query(User).filter(User.id == owner_id).first()
        req.owner_ecc_public_key = owner.ecc_public_key if owner else None
        # 查文件加密 AES
        file = db.query(File).filter(File.id == req.file_id).first()
        req.encrypted_aes_key = file.file_ecc_aes_key if file else None
    else:
        req.status = RequestStatus.rejected

    db.commit()
    db.refresh(req)
    return req
