import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.orm import Session
from passlib.context import CryptContext

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

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed_everything():
    # 💥 BÍ THUẬT Ở ĐÂY: Nhét import model vào trong hàm để triệt tiêu Circular Import!
    from app.model.users import User
    from app.model.features import Feature
    from app.model.packages import Package

    db = SessionLocal()
    try:
        print("🔄 [HỆ THỐNG]: Đang rà soát và khởi tạo dữ liệu nền tảng...")

        # 1. TỰ ĐỘNG BƠM DANH SÁCH VŨ KHÍ (FEATURES)
        features_dict = {
            'BASIC_RECON': Feature(name='Basic Reconnaissance', code='BASIC_RECON'),
            'PATH_TRAVERSAL': Feature(name='Path Traversal Scanner', code='PATH_TRAVERSAL'),
            'SQLi': Feature(name='SQL Injection Tool', code='SQLi'),
            'SECRET_SCANNER': Feature(name='Secret Scanner', code='SECRET_SCANNER'),
            'FULL_WEB_PENTEST': Feature(name='Full Web Pentest', code='FULL_WEB_PENTEST')
        }

        db_features = {}
        for code, feat in features_dict.items():
            existing_feat = db.query(Feature).filter(Feature.code == code).first()
            if not existing_feat:
                db.add(feat)
                db.commit()
                db.refresh(feat)
                db_features[code] = feat
                print(f"   + Đã nạp DB: {code}")
            else:
                db_features[code] = existing_feat

        # 2. TỰ ĐỘNG TẠO SẴN ACC ADMIN TỐI CAO
        admin_user = db.query(User).filter(User.username == 'admin').first()
        if not admin_user:
            hashed_pw = pwd_context.hash("Admin123") # Mật khẩu mặc định
            new_admin = User(
                username='admin',
                email='admin@gmail.com',
                hashed_password=hashed_pw,
                balance=999999.0,
                tier='admin'
            )
            db.add(new_admin)
            db.commit()
            print("   👑 Đã tạo sẵn tài khoản 'admin' (Pass: Admin123)")

        # 3. TỰ ĐỘNG TẠO CÁC GÓI CREDIT MẶC ĐỊNH (PACKAGES) KÈM FEATURES
        packages_data = [
            {
                "name": "starter",
                "description": "Gói Tân Binh - Mở khóa Recon cơ bản",
                "price": 50000,
                "credits_awarded": 500,
                "feature_codes": ['BASIC_RECON']
            },
            {
                "name": "pro",
                "description": "Gói Chuyên Nghiệp - Đầy đủ công cụ tấn công web cơ bản",
                "price": 150000,
                "credits_awarded": 2000,
                "feature_codes": ['BASIC_RECON', 'PATH_TRAVERSAL', 'SQLi']
            },
            {
                "name": "business",
                "description": "Gói Doanh Nghiệp - Toàn diện cho pentest web nâng cao",
                "price": 500000,
                "credits_awarded": 10000,
                "feature_codes": ['BASIC_RECON', 'PATH_TRAVERSAL', 'SQLi', 'SECRET_SCANNER', 'FULL_WEB_PENTEST']
            }
        ]

        for pkg_info in packages_data:
            existing_pkg = db.query(Package).filter(Package.name == pkg_info["name"]).first()
            if not existing_pkg:
                new_pkg = Package(
                    name=pkg_info["name"],
                    description=pkg_info["description"],
                    price=pkg_info["price"],
                    credits_awarded=pkg_info["credits_awarded"]
                )
                # Lấy các feature tương ứng từ kho đã quét ở trên để gắn vào gói mang đi bán
                linked_features = [db_features[code] for code in pkg_info["feature_codes"] if code in db_features]
                new_pkg.features = linked_features
                
                db.add(new_pkg)
                db.commit()
                print(f"   🛒 Đã cấu hình showroom gói mặc định: {pkg_info['name']}")

        print("✅ [HỆ THỐNG]: Hoàn tất khởi tạo dữ liệu tự động. Sẵn sàng thực thi lệnh!")

    except Exception as e:
        print(f"❌ Lỗi tự động khởi tạo database: {e}")
    finally:
        db.close()