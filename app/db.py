# app/db.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 创建数据库引擎
engine = create_engine(settings.DB_URL, echo=True)

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM 基类
Base = declarative_base()

# FastAPI 依赖项：获取数据库 session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
