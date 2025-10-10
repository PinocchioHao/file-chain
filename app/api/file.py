import os
from fastapi import APIRouter, UploadFile, Depends, HTTPException, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import datetime

from app.db import get_db
from app.services import file_service
from app.schemas.file import FileOut
from app.core.security import get_current_user
from app.models.user import User
from app.core.crypto import (
    load_public_key_from_der_b64,
    aes_gcm_encrypt,
    ecies_encrypt_for_public_key,
)
from app.services.blockchain_service import record_file_upload
import base64
import json
import os

router = APIRouter(prefix="/file", tags=["file"])


# 🔹 上传文件
@router.post("/upload", response_model=FileOut)
async def upload_file(
    file: UploadFile,
    signature: str = Form(...),  # 客户端提供 Base64(ASN.1 DER) 签名
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    stored_filename = f"{timestamp}_{file.filename}"

    # 读取原始文件字节
    content: bytes = await file.read()

    # TODO 文件用用户ECDSA私钥签名，得到的signature稍后入库（已实现：由客户端传入的 Base64 编码 DER 签名）
    signature_b64 = signature

    # TODO 文件加密得到加密后的文件，将AES用用户的ECC私钥加密（已实现：AES-GCM加密 + ECIES封装AES）
    aes_key = os.urandom(32)
    nonce, ciphertext = aes_gcm_encrypt(content, aes_key)

    # 将密文保存到磁盘
    file_service.save_bytes_to_disk(ciphertext, stored_filename)

    # 3) 用用户 ECC 公钥“封装/加密” AES 密钥（ECIES 简化版）
    ecc_pub = load_public_key_from_der_b64(current_user.ecc_public_key)
    wrapped = ecies_encrypt_for_public_key(ecc_pub, aes_key)
    ecc_aes_key_json = json.dumps(wrapped)

    # 写数据库记录（hash 使用明文内容的 SHA-256，便于后续完整性校验）
    db_file = file_service.create_file_record(
        db,
        owner_id=current_user.id,
        owner_name=current_user.username,
        filename=file.filename,
        stored_filename=stored_filename,
        signature=signature_b64,
        ecc_aes_key=ecc_aes_key_json,
        content=content,
    )
    # TODO 上传成功后记录文件元信息到区块链（已实现：写入 logs/chain_log.jsonl，后续可替换为真实链SDK）
    record_file_upload(db_file.id, current_user.id, db_file.hash)
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
