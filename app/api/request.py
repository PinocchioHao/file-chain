from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db import get_db
from app.schemas.request import FileRequestCreate, FileRequestResponse, FileRequestApprove
from app.services.blockchain_service import record_request_submit, record_request_approve
from app.services.request_service import create_request, get_requests_with_users, approve_request

router = APIRouter(prefix="/requests", tags=["requests"])


# 发起请求
@router.post("/", response_model=FileRequestResponse)
def request_file_access(request: FileRequestCreate, db: Session = Depends(get_db),
                        current_user=Depends(get_current_user)):
    file_request = create_request(db, current_user.id, request)
    if file_request:
        record_request_submit(file_request.id, file_request.file_id, file_request.requester_id, file_request.owner_id)
    # TODO 区块链
    return file_request


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


# 审批请求
@router.post("/approve", response_model=FileRequestResponse)
def approve_file_request(approve_data: FileRequestApprove, db: Session = Depends(get_db),
                         current_user=Depends(get_current_user)):
    request = approve_request(db, approve_data, current_user.id)
    if request:
        record_request_approve(request.id, request.status.value)
    else:
        raise HTTPException(status_code=404, detail="Request not found or not authorized")
    # TODO 区块链
    return request
