from fastapi import FastAPI, Depends
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session
from typing import List
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.controller import transactions as transaction_controller
from app.config.database import engine, Base, get_db
from app.config.security import get_password_hash, verify_password, create_access_token, SECRET_KEY, ALGORITHM

from app.model.users import User
from app.model.transactions import Transaction
from app.model.packages import Package
from app.model.features import Feature

from app.dto.packages import PackageResponse, PackageCreate
from app.dto.transactions import BuyPackageRequest, TransactionResponse
from app.dto.users import UserProfileResponse, UserCreate, Token

from app.controller import packages as package_controller

from app.api_guard import get_current_user, require_feature_and_credit, get_admin_user

app = FastAPI(title="SaaS Credit Management API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     
    allow_credentials=False, 
    allow_methods=["*"], 
    allow_headers=["*"], 
)

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



@app.get("/")
def read_root():
    return {"message": "Hệ thông đang chạy tốt"}


# ===================================================
# CÁC API QUẢN LÝ GÓI CREDITS VÀ GIAO DỊCH
# ===================================================

# 1. API LIST - Lấy danh sách các gói (User & Admin đều xem được)
@app.get("/api/packages", response_model=List[PackageResponse], tags=["Quản lý Gói Credits"])
def get_all_packages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lấy danh sách các gói credits để hiển thị cho user (Thả cửa)"""
    # Trả về trực tiếp bằng SQLAlchemy (Nếu bro có package_controller thì dùng dòng dưới)
    return db.query(Package).offset(skip).limit(limit).all()


# Endpoint trả về danh sách features (dùng cho Admin UI khi tạo packages)
@app.get('/api/features', tags=["Quản lý Gói Credits"])
def list_features(db: Session = Depends(get_db)):
    return db.query(Feature).all()


# 2. API CREATE - Tạo gói mới (Chỉ Admin)
@app.post("/api/packages", response_model=PackageResponse, tags=["Quản lý Gói Credits"])
def create_package(
    package: PackageCreate, 
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user) 
):
    # Tách lấy danh sách ID của tool (features)
    feature_ids = package.feature_ids
    package_data = package.model_dump(exclude={"feature_ids"})

    new_package = Package(**package_data)
    

    if feature_ids:
        features = db.query(Feature).filter(Feature.id.in_(feature_ids)).all()
        new_package.features = features

    db.add(new_package)
    db.commit()
    db.refresh(new_package)
    return new_package


# 3. API UPDATE - Sửa thông tin gói (Chỉ Admin)
@app.put("/api/packages/{package_id}", response_model=PackageResponse, tags=["Quản lý Gói Credits"])
def update_package(
    package_id: int, 
    package_data: PackageCreate, 
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    db_package = db.query(Package).filter(Package.id == package_id).first()
    if not db_package:
        raise HTTPException(status_code=404, detail="Không tìm thấy gói credit này")
    
    # Cập nhật thông tin chữ và số
    update_data = package_data.model_dump(exclude={"feature_ids"})
    for key, value in update_data.items():
        setattr(db_package, key, value)
        

    if package_data.feature_ids is not None:
        features = db.query(Feature).filter(Feature.id.in_(package_data.feature_ids)).all()
        db_package.features = features
    
    db.commit()
    db.refresh(db_package)
    return db_package


@app.delete("/api/packages/{package_id}", tags=["Quản lý Gói Credits"])
def delete_package(
    package_id: int, 
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    db_package = db.query(Package).filter(Package.id == package_id).first()
    if not db_package:
        raise HTTPException(status_code=404, detail="Không tìm thấy gói credit này")
    
    from app.model.transactions import Transaction 
    db.query(Transaction).filter(Transaction.package_id == package_id).delete()
    
    # Nhổ cỏ xong rồi thì xóa gói luôn
    db.delete(db_package)
    db.commit()
    return {"message": "Đã xóa sạch sẽ gói và hóa đơn liên quan!"}


# 5. API BUY - User MUA GÓI (Cực kỳ quan trọng, không được xóa)
@app.post("/api/transactions/buy", response_model=TransactionResponse, tags=["Giao dịch"])
def buy_credits_package(request: BuyPackageRequest, db: Session = Depends(get_db)):
    """API cho phép User mua gói credits và unlock tính năng"""
    return transaction_controller.buy_package(db=db, request=request)

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
        "tier": current_user.tier,
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

@app.get("/api/services/basic-recon", tags=["Dịch vụ"])
def basic_recon(
    # Yêu cầu phải có quyền BASIC_RECON và ví phải có ít nhất 100 credit
    current_user: User = Depends(require_feature_and_credit(feature_code="BASIC_RECON", credit_cost=100))
):
    """API giả lập , mỗi lần bấm bay 100 credit"""
    
    
    return {
        "status": "success",
        "message": "Ting ting! Đã quét xong hệ thống",
        "cost": 100,
        "remaining_balance": current_user.balance # Tiền đã bị trừ bởi Middleware
    }

@app.get("/api/services/path-traversal", tags=["Dịch vụ"])
def path_traversal(
    # Yêu cầu phải có quyền PATH_TRAVERSAL và ví phải có ít nhất 200 credit
    current_user: User = Depends(require_feature_and_credit(feature_code="PATH_TRAVERSAL", credit_cost=200))
):
    """API giả lập , mỗi lần bấm bay 200 credit"""
    
    
    return {
        "status": "success",
        "message": "Ting ting! Đã quét xong hệ thống",
        "cost": 200,
        "remaining_balance": current_user.balance # Tiền đã bị trừ bởi Middleware
    }

@app.get("/api/services/SQLi", tags=["Dịch vụ"])
def SQLi(
    current_user: User = Depends(require_feature_and_credit(feature_code="SQLi", credit_cost=300))
):
    """API giả lập, mỗi lần bấm bay 300 credit"""   
    
    return {
        "status": "success",
        "message": "Ting ting! Đã quét xong hệ thống",
        "cost": 300,
        "remaining_balance": current_user.balance # Tiền đã bị trừ bởi Middleware
    }

@app.get("/api/services/secret-scanner" , tags=["Dịch vụ"])
def secret_scanner(
    current_user: User = Depends(require_feature_and_credit(feature_code="SECRET_SCANNER", credit_cost=500))
):
    """API giả lập, mỗi lần bấm bay 500 credit"""   
    
    return {
        "status": "success",
        "message": "Ting ting! Đã quét xong hệ thống",
        "cost": 500,
        "remaining_balance": current_user.balance # Tiền đã bị trừ bởi Middleware
    }

@app.get("/api/services/full-web-pentest", tags=["Dịch vụ"])
def full_web_pentest(
    current_user: User = Depends(require_feature_and_credit(feature_code="FULL_WEB_PENTEST", credit_cost=1000))
):
    """API giả lập, mỗi lần bấm bay 1000 credit"""   
    
    return {
        "status": "success",
        "message": "Ting ting! Đã quét xong hệ thống",
        "cost": 1000,
        "remaining_balance": current_user.balance # Tiền đã bị trừ bởi Middleware
    }

# ===================================================
# API Đăng ký và Đăng nhập 
# ===================================================

@app.post("/api/auth/register", response_model=UserProfileResponse, tags=["Login & Register"])
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
        "tier": new_user.tier,             
        "balance": float(new_user.balance),
        "unlocked_features": []  
    }

@app.post("/api/auth/login", response_model=Token, tags=["Login & Register"])
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


# ===================================================
# API Bị Khóa 
# ===================================================

@app.get("/api/users/me", response_model=UserProfileResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    """API Xem Profile: Phải lọt qua được Lính Gác mới tới đây"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "balance": current_user.balance,
        "unlocked_features": [] # Mảng tính năng (sẽ làm ở bước sau)
    }

