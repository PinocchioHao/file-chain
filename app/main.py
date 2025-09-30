# app/main.py
from fastapi import FastAPI
from app.db import Base, engine
from app.api import auth   # 导入路由文件
from app.api import file
from app.api import request

# 创建数据库表（只会在第一次时生效）
# Base.metadata.create_all(bind=engine)

# FastAPI 应用
app = FastAPI(title="FileChain API")

# 挂载路由
app.include_router(auth.router)
app.include_router(file.router)
app.include_router(request.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to my Demo!"}