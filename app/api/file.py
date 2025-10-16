import os
from datetime import datetime

from fastapi import APIRouter, UploadFile, Depends, HTTPException, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db import get_db
from app.models.user import User
from app.schemas.file import FileOut
from app.services import file_service
from app.services.blockchain_service import record_file_upload

router = APIRouter(prefix="/file", tags=["file"])


# 🔹 上传文件
@router.post("/upload", response_model=FileOut)
async def upload_file(
        file: UploadFile,
        signature: str = Form(...),  # 客户端提供签名 JSON 字符串
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    stored_filename = f"{timestamp}_{file.filename}"

    # 保存文件到磁盘
    file_path, content = await file_service.save_file_to_disk(file, stored_filename)

    # 写数据库记录（不存 AES）
    db_file = file_service.create_file_record(
        db,
        owner_id=current_user.id,
        owner_name=current_user.username,
        filename=file.filename,
        stored_filename=stored_filename,
        signature=signature,
        content=content,
    )
    # 记录区块链
    tx_hash = record_file_upload(db, db_file.id, current_user.id, current_user.username, db_file.hash, db_file.filename, db_file.signature)

    file_out = FileOut.from_orm(db_file)
    file_out.tx_hash = tx_hash
    return file_out

# 🔹 查询文件列表
@router.get("/list", response_model=list[FileOut])
def list_files(db: Session = Depends(get_db)):
    return file_service.list_files(db)


# 🔹 下载文件
@router.get("/download/{file_id}")
def download_file(file_id: int, db: Session = Depends(get_db)):
    db_file = file_service.get_file(db, file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    file_path = os.path.join("uploads", db_file.stored_filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(file_path, filename=db_file.filename)
