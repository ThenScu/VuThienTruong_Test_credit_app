from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from typing import List, Optional
from datetime import datetime

# Lớp cơ sở chứa các trường chung
class PackageBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    credits_awarded: int

# Lớp dùng để nhận dữ liệu khi Admin tạo Package mới
class PackageCreate(PackageBase):
    feature_ids: List[int] = [] # Danh sách ID của các tính năng muốn gán vào gói

# Lớp dùng để format dữ liệu trả về cho Client
class PackageResponse(PackageBase):
    id: int
    created_at: datetime
    
class FeatureResponse(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str] = None


class PackageResponse(PackageBase):
    id: int
    created_at: datetime
    features: List[FeatureResponse] = []
    # ConfigDict(from_attributes=True) cho phép Pydantic đọc data trực tiếp từ SQLAlchemy Model (giống ModelMapper)
    model_config = ConfigDict(from_attributes=True)