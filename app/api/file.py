import os
from fastapi import APIRouter, UploadFile, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import datetime

from app.db import get_db
from app.services import file_service
from app.schemas.file import FileOut
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/file", tags=["file"])


# 🔹 上传文件
@router.post("/upload", response_model=FileOut)
async def upload_file(
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    stored_filename = f"{timestamp}_{file.filename}"

    # TODO 文件用用户ECDSA私钥签名，得到的signature稍后入库
    # TODO 文件加密得到加密后的文件，将AES用用户的ECC私钥加密
    # 🔹 这里先用dummy数据，后续替换成真实加密/签名逻辑
    dummy_signature = f"signature_of_{file.filename}"
    dummy_ecc_aes_key = f"ecc_encrypted_aes_key_for_{file.filename}"


    # 上传（先存明文，TODO 后面替换成加密文件）
    file_path, content = file_service.save_file_to_disk(file, stored_filename)

    # 生成签名和加密AES密钥（dummy）
    db_file = file_service.create_file_record(
        db,
        owner_id=current_user.id,
        owner_name=current_user.username,
        filename=file.filename,
        stored_filename=stored_filename,
        signature=dummy_signature,
        ecc_aes_key=dummy_ecc_aes_key,
        content=content
    )
    # TODO 上传成功后记录文件元信息到区块链
    return db_file


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
