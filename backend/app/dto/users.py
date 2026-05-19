import re
from typing import List
from pydantic import BaseModel, Field, field_validator

# ==========================================
# 1. DTO Trả về thông tin User 
# ==========================================
class UserProfileResponse(BaseModel):
    id: int
    username: str
    email: str
    tier: str
    balance: float  # Tiền tệ để kiểu số thực cho chuẩn Model
    unlocked_features: List[str] = []

    class Config:
        from_attributes = True

# ==========================================
# 2. DTO Đăng ký (Regex)
# ==========================================
class UserCreate(BaseModel):
    username: str = Field(
        ..., 
        min_length=3, 
        max_length=20, 
        pattern=r"^[a-zA-Z0-9_]+$",
        description="Username chỉ gồm chữ, số và dấu gạch dưới"
    )
    
    email: str = Field(
        ..., 
        pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
        description="Phải là một địa chỉ email hợp lệ"
    )
    
    password: str = Field(
        ..., 
        min_length=6,
        description="Mật khẩu phải từ 6 ký tự, có ít nhất 1 chữ IN HOA và 1 chữ số"
    )

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError('Password yếu quá bro! Phải có ít nhất 1 chữ IN HOA.')
        if not re.search(r"\d", v):
            raise ValueError('Password chưa đủ độ lú! Phải có ít nhất 1 chữ số.')
        return v

# ==========================================
# 3. DTO Token Đăng nhập
# ==========================================
class Token(BaseModel):
    access_token: str
    token_type: str