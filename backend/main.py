# main.py
from fastapi import FastAPI
from app.config.database import engine, Base

from app.model import * 

# Lệnh này sẽ tự động tạo tất cả các bảng vào DB nếu chưa có
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SaaS Credit Platform API",
    description="Kho vũ khí công nghệ - Module quản lý gói credits và phân quyền",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Hệ thống SaaS Core đang chạy mượt mà!"}