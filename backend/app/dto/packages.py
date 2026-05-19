from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from typing import List, Optional
from datetime import datetime

class PackageBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    credits_awarded: int

class PackageCreate(PackageBase):
    feature_ids: List[int] = [] 

class FeatureResponse(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str] = None

# CHỈ GIỮ LẠI ĐÚNG 1 CLASS PackageResponse NÀY THÔI NHÉ BRO:
class PackageResponse(PackageBase):
    id: int
    created_at: Optional[datetime] = None 
    features: List[FeatureResponse] = []
    
    model_config = ConfigDict(from_attributes=True)