from fastapi import FastAPI, Depends
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session
from typing import List
from app.controller import transactions as transaction_controller
from app.config.database import engine, Base, get_db
from app.config.security import get_password_hash, verify_password, create_access_token

from app.model.users import User
from app.model.transactions import Transaction
from app.model.packages import Package
from app.model.features import Feature

from app.dto.packages import PackageResponse, PackageCreate
from app.dto.transactions import BuyPackageRequest, TransactionResponse
from app.dto.users import UserProfileResponse, UserCreate, Token

from app.controller import packages as package_controller

from app.api_guard import get_current_user
from app.api_guard import require_feature_and_credit


def wait_for_db(engine, retries: int = 10, delay_seconds: int = 1):
    """Wait for the database to become available before running migrations or
    calling create_all. This prevents startup crashes when Postgres is still
    initializing (common in docker-compose setups).

    Retries connection attempts `retries` times with `delay_seconds` pauses.
    """
    import time
    from sqlalchemy.exc import OperationalError

    attempt = 0
    while attempt < retries:
        try:
            with engine.connect():
                return True
        except OperationalError:
            attempt += 1
            time.sleep(delay_seconds)
            delay_seconds = min(delay_seconds * 2, 10)
    # Final attempt, let exception bubble to provide context
    with engine.connect():
        return True


if wait_for_db(engine):
    Base.metadata.create_all(bind=engine)

app = FastAPI(title="SaaS Credit Management API", version="1.0")

@app.get("/")
def read_root():
    return {"message": "Hệ thông đang chạy tốt"}

# ===================================================
# Các API cua package và transaction (Dành cho cả user và admin, nhưng admin sẽ có thêm API tạo gói)
# ===================================================
@app.get("/api/packages", response_model=List[PackageResponse])
def read_packages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lấy danh sách các gói credits để hiển thị cho user"""
    return package_controller.get_packages(db=db, skip=skip, limit=limit)

@app.post("/api/packages", response_model=PackageResponse)
def create_package(package: PackageCreate, db: Session = Depends(get_db)):
    """API cho admin tạo gói credit mới"""
    return package_controller.create_package(db=db, package_data=package)

@app.post("/api/transactions/buy", response_model=TransactionResponse)
def buy_credits_package(request: BuyPackageRequest, db: Session = Depends(get_db)):
    """API cho phép User mua gói credits và unlock tính năng"""
    return transaction_controller.buy_package(db=db, request=request)

# ===================================================
# Các API cua user
# ===================================================

@app.get("/api/users/me", response_model=UserProfileResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """API lấy thông tin Profile và các tính năng đang sở hữu"""
    # Móc danh sách feature_code từ bảng trung gian ra
    features_list = [uf.feature.code for uf in current_user.unlocked_features]
    
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "balance": current_user.balance,
        "unlocked_features": features_list
    }

@app.get("/api/users/me/transactions", response_model=List[TransactionResponse])
def get_my_transactions(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """API lấy lịch sử nạp/trừ tiền của User (Mới nhất xếp lên đầu)"""
    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .order_by(Transaction.created_at.desc()) # Sắp xếp giảm dần theo thời gian
        .all()
    )
    return transactions

# ===================================================
# API sử dụng dịch vụ (tự động trừ credit)
# ===================================================

@app.get("/api/services/generate-image")
def generate_ai_image(
    # Yêu cầu phải có quyền IMAGE_GEN và ví phải có ít nhất 10 credit
    current_user: User = Depends(require_feature_and_credit(feature_code="IMAGE_GEN", credit_cost=100))
):
    """API giả lập tạo ảnh AI, mỗi lần bấm bay 10 credit"""
    
    # ... Luồng giả lập gọi API Midjourney hoặc AI tạo ảnh ...
    
    return {
        "status": "success",
        "message": "Ting ting! Đã render xong 1 bức ảnh siêu nét!",
        "cost": 100,
        "remaining_balance": current_user.balance # Tiền đã bị trừ bởi Middleware
    }

# ===================================================
# API Đăng ký và Đăng nhập 
# ===================================================

@app.post("/api/auth/register", response_model=UserProfileResponse)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """API Đăng ký: Nhận pass thô -> Băm ra -> Lưu vào DB"""
    # Check xem username hoặc email đã tồn tại chưa
    db_user = db.query(User).filter((User.username == user_data.username) | (User.email == user_data.email)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username hoặc Email đã được sử dụng")
    
    # Băm cái password ra trước khi lưu
    hashed_password = get_password_hash(user_data.password)
    
    # Tạo user mới (vừa đẻ ra tặng luôn 5000 credit làm vốn khởi nghiệp)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        balance=0 
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "balance": new_user.balance,
        "unlocked_features": []  
    }

@app.post("/api/auth/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    """API Đăng nhập: Trả về thẻ bài JWT"""
    # Tìm user trong DB bằng username
    user = db.query(User).filter(User.username == form_data.username).first()
    
    # Kiểm tra user có tồn tại và pass có khớp với pass đã băm không
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản hoặc mật khẩu sai",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Qua ải thành công -> Dập Token xuất xưởng
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {"access_token": access_token, "token_type": "bearer"}