# app/core/config.py
from pydantic_settings import BaseSettings


# 数据库，JWT等相关配置
class Settings(BaseSettings):
    DB_URL: str = "mysql+pymysql://root:@localhost:3306/file_chain"
    JWT_SECRET: str = "supersecret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # class Config:
    #     env_file = ".env"


settings = Settings()
