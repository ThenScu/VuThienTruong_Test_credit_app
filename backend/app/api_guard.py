# app/api_guard.py
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError # Đảm bảo bro đã cài thư viện này (pip install python-jose)
from app.config.database import get_db
from app.model.users import User

# === CẤU HÌNH JWT === (Bro nhớ sửa lại SECRET_KEY cho khớp với file Auth của bro nhé)
SECRET_KEY = os.getenv("SECRET_KEY", "test123")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# Khai báo cổng kiểm tra thẻ bài (Cái này gọi ra cái ổ khóa trên Swagger)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# 1. HÀM LÍNH GÁC: GIẢI MÃ TOKEN (Thay cho cái fix cứng ID=1 cũ)
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token fake hoặc không hợp lệ",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = str(payload.get("sub")) # Có thể là "user_id" tùy lúc bro tạo Token
        if user_id is None or user_id == "None":
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user

# 2. TRẠM THU PHÍ VÀ KIỂM TRA QUYỀN (BẢNG PHONG THẦN)
def require_feature_and_credit(feature_code: str, credit_cost: int):
    def dependency(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        # BẢNG PHONG THẦN
        tier_permissions = {
            "new": [],
            "starter": ["BASIC_RECON", "PATH_TRAVERSAL"],
            "pro": ["BASIC_RECON", "PATH_TRAVERSAL", "SQLi", "SECRET_SCANNER"],
            "business": ["BASIC_RECON", "PATH_TRAVERSAL", "SQLi", "SECRET_SCANNER", "FULL_WEB_PENTEST"]
        }
        
        user_tier = current_user.tier.lower() if current_user.tier else "starter"
        allowed_features = tier_permissions.get(user_tier, ["BASIC_RECON"])

        # CHẶN CỬA QUYỀN
        if feature_code not in allowed_features:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Chức năng {feature_code} này đã bị khóa đối với gói {user_tier.upper()}! Lên đời cao để mở khóa."
            )

        # CHẶN CỬA TIỀN
        if float(current_user.balance) < credit_cost:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Không đủ credit! Cần {credit_cost} credit, ví còn có {current_user.balance}."
            )
            
        # TRỪ TIỀN
        current_user.balance = float(current_user.balance) - credit_cost
        db.commit()
        db.refresh(current_user)
        
        return current_user
    return dependency

def get_admin_user(current_user: User = Depends(get_current_user)):
    """Lính gác VIP: Check đích danh cột tier trong Database"""
    # Nếu rảnh khuôn tier không phải admin thì đá văng ra ngay
    if current_user.tier != "admin":
        raise HTTPException(
            status_code=403, 
            detail="Bạn không có quyền truy cập vào tài nguyên này. Chỉ Admin mới được phép."
        )
    return current_user