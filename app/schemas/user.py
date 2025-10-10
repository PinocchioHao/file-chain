from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    ecc_public_key: str
    ecdsa_public_key: str
    # 私钥仅在注册时一次性返回给客户端保存
    ecc_private_key: str
    ecdsa_private_key: str

    class Config:
        orm_mode = True
