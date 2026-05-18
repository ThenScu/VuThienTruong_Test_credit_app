# app/config/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Lấy URL từ biến môi trường (mặc định cho localhost nếu chạy không có Docker)


SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")


# Khởi tạo Engine kết nối
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Quản lý phiên làm việc với DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Class Base để các Model khác kế thừa
Base = declarative_base()

# Dependency để sử dụng trong FastAPI Routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()