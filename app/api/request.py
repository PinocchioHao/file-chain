from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.request import FileRequestCreate, FileRequestResponse, FileRequestApprove
from app.services.request_service import create_request, get_requests_by_requester, get_requests_by_owner, approve_request
from app.services.blockchain_service import record_request_submit, record_request_approve
from app.db import get_db
from app.core.security import get_current_user

router = APIRouter(prefix="/requests", tags=["requests"])

# 1. 发起文件访问请求
@router.post("/", response_model=FileRequestResponse)
def request_file_access(request: FileRequestCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    file_request = create_request(db, current_user.id, request)
    # TODO 申请信息上区块链（已实现：写入 logs/chain_log.jsonl，后续可替换为真实链SDK）
    if file_request:
        record_request_submit(file_request.id, file_request.file_id, file_request.requester_id, file_request.owner_id)
    return file_request

# 2. 查看我的申请
@router.get("/my", response_model=list[FileRequestResponse])
def view_my_requests(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return get_requests_by_requester(db, current_user.id)

# 3. 查看待审批请求（owner用）
@router.get("/pending", response_model=list[FileRequestResponse])
def view_pending_requests(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return get_requests_by_owner(db, current_user.id)

# 4. 审批请求
@router.post("/approve", response_model=FileRequestResponse)
def approve_file_request(approve_data: FileRequestApprove, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    request = approve_request(db, approve_data, current_user.id)
    # TODO 审批信息上区块链（已实现：写入 logs/chain_log.jsonl，后续可替换为真实链SDK）
    if request:
        record_request_approve(request.id, request.status.value)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found or not authorized")
    return request
