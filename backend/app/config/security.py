import os
import bcrypt
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from jose import jwt

# Nạp dữ liệu từ file .env vào hệ thống
load_dotenv()

# Khóa bí mật dùng để ký Token
SECRET_KEY = os.getenv("SECRET_KEY", "test123")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# ==========================================================
# BĂM MẬT KHẨU (bằng Bcrypt Native)
# ==========================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """So sánh pass user nhập và pass đã băm trong DB"""
    # Bcrypt yêu cầu định dạng bytes nên phải encode('utf-8')
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )

def get_password_hash(password: str) -> str:
    """Băm pass mới trước khi lưu xuống DB"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    # Decode về lại chuỗi string để lưu vào PostgreSQL
    return hashed.decode('utf-8')

# ==========================================================
# JWT TOKEN
# ==========================================================

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Hàm dập ra cái thẻ bài JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt