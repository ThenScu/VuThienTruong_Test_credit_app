import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

from backend.app.config.security import get_password_hash

# Tải biến môi trường từ file .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Khởi tạo Engine kết nối PostgreSQL
engine = create_engine(DATABASE_URL)

# Tạo SessionFactory - Quản lý các phiên giao dịch với DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base model để các bảng (User, Package...) kế thừa
Base = declarative_base()

# ---------------------------------------------------------
# Hàm lấy DB Session (Dependency) - Chống Connection Leak
# ---------------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------------------------------------
# Hàm Seeding và tạo bảng (Nhét import vào trong để né Circular Import)
# ---------------------------------------------------------
def seed_everything():
    # 1. Import các model ở đây để tránh lỗi vòng tròn (Circular Import)
    from app.model.users import User
    from app.model.packages import Package
    from app.model.features import Feature
    from app.model.transactions import Transaction
    from app.model.user_features import UserFeature
    
    # (Nếu bro có hàm băm password trong security.py thì bỏ comment dòng dưới và sửa lại path)
    # from app.config.security import get_password_hash
    
    # 2. Tạo tất cả các bảng vào database dựa trên cấu trúc Model
    Base.metadata.create_all(bind=engine)
    
    # 3. Bắt đầu phiên làm việc để nạp dữ liệu mẫu
    db = SessionLocal()
    try:
        # --- SEED TÀI KHOẢN ADMIN ---
        admin_exists = db.query(User).filter(User.username == "admin").first()
        if not admin_exists:
            admin_user = User(
                username="admin", 
                email="admin@gmail.com",  #
                hashed_password=get_password_hash("Admin123"), 
                balance=1000000,
                tier="admin"
            )
            db.add(admin_user)
            print("🚀 Đã khởi tạo tài khoản Admin thành công!")

        # --- SEED CÁC GÓI CREDITS (PACKAGES) ---
        if not db.query(Package).first():
            pkg_basic = Package(name="Gói Cơ Bản", price=50000, credits=50)
            pkg_pro = Package(name="Gói Chuyên Nghiệp", price=150000, credits=200)
            pkg_vip = Package(name="Gói Tối Thượng", price=500000, credits=1000)
            
            db.add_all([pkg_basic, pkg_pro, pkg_vip])
            print("🚀 Đã khởi tạo các gói Package thành công!")
            
        # --- SEED TÍNH NĂNG (FEATURES) ---
        if not db.query(Feature).first():
            feat_1 = Feature(name="Tải tài liệu PDF", cost=10)
            feat_2 = Feature(name="Mở khóa Video Premium", cost=50)
            
            db.add_all([feat_1, feat_2])
            print("🚀 Đã khởi tạo các Features thành công!")

        # Lưu toàn bộ vào DB
        db.commit()
        print("✅ Quá trình Seeding hoàn tất mượt mà!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Lỗi khi Seeding dữ liệu: {e}")
    finally:
        db.close()