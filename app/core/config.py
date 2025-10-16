# app/core/config.py
from pydantic_settings import BaseSettings

# 数据库，JWT等相关配置
class Settings(BaseSettings):
    DB_URL: str = "mysql+pymysql://root:@localhost:3306/file_chain"
    # DB_URL: str = "mysql+pymysql://root:StrongPass!123@13.237.197.44:3306/file_chain"
    JWT_SECRET: str = "supersecret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # 区块链相关
    ETH_NODE_URL: str = "https://ethereum-sepolia-rpc.publicnode.com"
    ETH_CHAIN_ID: int = 11155111
    ETH_SENDER_ADDRESS: str = "0x62B037E7743e81D2f6fD42eE0732d75a64E46e4C"
    ETH_PRIVATE_KEY: str = "51de9b76949bf8b9fa879c990b86161a6ea850b7efccd08d6356014d97811df7"
    ETH_RECEIVER_ADDRESS: str = "0x62B037E7743e81D2f6fD42eE0732d75a64E46e4C"

settings = Settings()


