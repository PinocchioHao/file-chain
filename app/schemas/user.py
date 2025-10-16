from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str
    ecc_public_key: str
    ecdsa_public_key: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    ecc_public_key: str
    ecdsa_public_key: str

    class Config:
        from_attributes = True