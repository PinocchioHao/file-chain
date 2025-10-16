from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy.orm import aliased

from app.models.file import File
from app.models.request import FileRequest, RequestStatus
from app.models.user import User
from app.schemas.request import FileRequestCreate, FileRequestApprove


def create_request(db: Session, requester_id: int, req: FileRequestCreate):
    # 找文件
    file = db.query(File).filter(File.id == req.file_id).first()
    if not file:
        return None

    # 获取申请者 ECC 公钥
    requester = db.query(User).filter(User.id == requester_id).first()
    ecc_pub = requester.ecc_public_key if requester else None

    new_req = FileRequest(
        file_id=req.file_id,
        requester_id=requester_id,
        owner_id=file.owner_id,
        requester_ecc_public_key=ecc_pub
    )
    db.add(new_req)
    db.commit()
    db.refresh(new_req)
    return new_req


def get_requests_by_requester(db: Session, requester_id: int):
    # 查询我的申请，同时获取 requester 用户名和文件名
    return (
        db.query(
            FileRequest,
            File.filename.label("file_name"),
            User.username.label("requester_username")  # 申请人用户名
        )
        .join(File, File.id == FileRequest.file_id)
        .join(User, User.id == FileRequest.requester_id)
        .filter(FileRequest.requester_id == requester_id)
        .all()
    )


# def get_requests_by_owner(db: Session, owner_id: int):
#     # 查询待审批请求，同时获取文件拥有者用户名和文件名
#     return (
#         db.query(
#             FileRequest,
#             File.filename.label("file_name"),
#             User.username.label("owner_username")  # 文件拥有者用户名
#         )
#         .join(File, File.id == FileRequest.file_id)
#         .join(User, User.id == FileRequest.owner_id)
#         .filter(FileRequest.owner_id == owner_id, FileRequest.status == RequestStatus.pending)
#         .all()
#     )
#
#
# def get_requests_with_users(db: Session, user_id: int, for_owner: bool = False):
#     """
#     获取请求记录，同时联表文件表和申请人/拥有者信息
#     - for_owner=False: 查询我的申请
#     - for_owner=True: 查询待审批请求
#     """
#     requester_alias = aliased(User)
#     owner_alias = aliased(User)
#
#     query = (
#         db.query(
#             FileRequest,
#             File.filename.label("file_name"),
#             File.signature.label("signature"),
#             requester_alias.username.label("requester_username"),
#             owner_alias.username.label("owner_username")
#         )
#         .join(File, File.id == FileRequest.file_id)
#         .join(requester_alias, requester_alias.id == FileRequest.requester_id)
#         .join(owner_alias, owner_alias.id == FileRequest.owner_id)
#     )
#
#     if for_owner:
#         query = query.filter(FileRequest.owner_id == user_id, FileRequest.status == RequestStatus.pending)
#     else:
#         query = query.filter(FileRequest.requester_id == user_id)
#
#     return query.all()


def approve_request(db: Session, approve_data: FileRequestApprove, owner_id: int):
    req = db.query(FileRequest).filter(
        FileRequest.id == approve_data.request_id,
        FileRequest.owner_id == owner_id
    ).first()
    if not req:
        return None

    if approve_data.decision == RequestStatus.approved:
        req.status = RequestStatus.approved
        req.encrypted_aes_key = approve_data.encrypted_aes_key
    else:
        req.status = RequestStatus.rejected

    db.commit()
    db.refresh(req)
    return req


def get_requests_with_users(db, user_id: int, for_owner: bool = False, status: Optional[List[str]] = None):
    requester_alias = aliased(User)
    owner_alias = aliased(User)

    query = (
        db.query(
            FileRequest,
            File.filename.label("file_name"),
            File.signature.label("signature"),
            requester_alias.username.label("requester_username"),
            owner_alias.username.label("owner_username")
        )
        .join(File, File.id == FileRequest.file_id)
        .join(requester_alias, requester_alias.id == FileRequest.requester_id)
        .join(owner_alias, owner_alias.id == FileRequest.owner_id)
    )

    if for_owner:
        # owner 查看：默认关注 owner_id
        query = query.filter(FileRequest.owner_id == user_id)
    else:
        query = query.filter(FileRequest.requester_id == user_id)

    # 支持 status 多值过滤
    if status:
        query = query.filter(FileRequest.status.in_(status))

    # 如果是 for_owner 并且不指定 status，通常想看所有包括 pending/approved/rejected
    return query.order_by(FileRequest.created_at.desc()).all()
