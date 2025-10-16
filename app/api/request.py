from typing import Optional, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db import get_db
from app.schemas.request import FileRequestCreate, FileRequestResponse, FileRequestApprove, RequestStatus
from app.services.blockchain_service import record_request_submit, record_request_approve
from app.services.request_service import create_request, get_requests_with_users, approve_request

router = APIRouter(prefix="/requests", tags=["requests"])


# 发起请求
@router.post("/", response_model=FileRequestResponse)
def request_file_access(request: FileRequestCreate, db: Session = Depends(get_db),
                        current_user=Depends(get_current_user)):
    # 本地处理
    file_request = create_request(db, current_user.id, request)
    # 推区块链
    tx_hash = record_request_submit(
        db,
        file_request.id,
        current_user.id,
        current_user.username,
        file_request.owner_id,
        file_request.file_id
    )
    # 返回包含 tx_hash 的对象
    resp = FileRequestResponse.from_orm(file_request)
    resp.tx_hash = tx_hash
    return resp



# 审批请求
@router.post("/approve", response_model=FileRequestResponse)
def approve_file_request(approve_data: FileRequestApprove, db: Session = Depends(get_db),
                         current_user=Depends(get_current_user)):
    # 本地处理
    request = approve_request(db, approve_data, current_user.id)
    # 推区块链
    tx_hash = record_request_approve(db, request.id, current_user.id, current_user.username, request.status.value, request.encrypted_aes_key)

    # 返回包含 tx_hash 的对象
    resp = FileRequestResponse.from_orm(request)
    resp.tx_hash = tx_hash
    return resp



# 查看我的申请
@router.get("/my", response_model=list[FileRequestResponse])
def view_my_requests(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    rows = get_requests_with_users(db, current_user.id, for_owner=False)
    result = []
    for req, file_name, signature, requester_username, owner_username in rows:
        result.append(FileRequestResponse(
            **req.__dict__,
            file_name=file_name,
            signature=signature,
            requester_username=requester_username,
            owner_username=owner_username
        ))
    return result


# 查看待审批请求
@router.get("/pending", response_model=list[FileRequestResponse])
def view_pending_requests(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    rows = get_requests_with_users(db, current_user.id, for_owner=True)
    result = []
    for req, file_name, signature, requester_username, owner_username in rows:
        result.append(FileRequestResponse(
            **req.__dict__,
            file_name=file_name,
            signature=signature,
            requester_username=requester_username,
            owner_username=owner_username
        ))
    return result


@router.get("/requests", response_model=list[FileRequestResponse])
def view_requests(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    for_owner: bool = Query(False, description="是否作为文件拥有者查看"),
    status: Optional[List[RequestStatus]] = Query(None, description="筛选状态，可多次传 status=approved&status=rejected")
):
    """
    通用请求查询接口：
    - for_owner=True 时返回作为文件拥有者相关的请求（可加 status 过滤）
    - for_owner=False 时返回作为申请者（我的申请）
    - status 可传多次以做 IN 过滤
    """
    # 如果后端的 service get_requests_with_users 支持 status 参数，直接透传；
    # 否则在这里处理转换并使用已有 service（假设 service 支持 status optional）
    # 我们假设 get_requests_with_users(db, user_id, for_owner, status) 接受 status: Optional[List[str]]
    status_values = None
    if status:
        # status elements are RequestStatus enum instances -> 转成字符串值
        status_values = [s.value if hasattr(s, "value") else str(s) for s in status]

    rows = get_requests_with_users(db, current_user.id, for_owner=for_owner, status=status_values)

    result = [
        FileRequestResponse(
            **req.__dict__,
            file_name=file_name,
            signature=signature,
            requester_username=requester_username,
            owner_username=owner_username
        )
        for req, file_name, signature, requester_username, owner_username in rows
    ]
    return result
