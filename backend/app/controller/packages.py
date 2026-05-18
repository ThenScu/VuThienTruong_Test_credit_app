from sqlalchemy.orm import Session
from app.model import Package, Feature
from app.dto.packages import PackageCreate

def create_package(db: Session, package_data: PackageCreate):
    """Tạo một gói credits mới kèm tính năng"""
    # 1. Khởi tạo đối tượng Package
    db_package = Package(
        name=package_data.name,
        description=package_data.description,
        price=package_data.price,
        credits_awarded=package_data.credits_awarded
    )
    
    # 2. Xử lý gán tính năng (Features) nếu có truyền lên feature_ids
    if package_data.feature_ids:
        # Lấy tất cả các Feature có ID nằm trong mảng truyền lên
        features = db.query(Feature).filter(Feature.id.in_(package_data.feature_ids)).all()
        # Nối vào danh sách features của gói (SQLAlchemy sẽ tự lo việc thêm vào bảng trung gian)
        db_package.features.extend(features)
    
    # 3. Lưu vào DB
    db.add(db_package)
    db.commit()
    db.refresh(db_package)
    
    return db_package