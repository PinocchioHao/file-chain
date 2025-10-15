from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth
from app.api import file
from app.api import request

app = FastAPI(title="FileChain API")

# 添加 CORS 中间件
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://13.237.197.44:8899",  # 前端服务地址
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许的前端地址
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)

# 挂载路由
app.include_router(auth.router)
app.include_router(file.router)
app.include_router(request.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to my Demo!"}
