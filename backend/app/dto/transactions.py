from pydantic import BaseModel, ConfigDict
from uuid import UUID
from decimal import Decimal
from datetime import datetime

class BuyPackageRequest(BaseModel):
    user_id: int     # Lấy ID của user 
    package_id: int  # ID gói muốn mua

class TransactionResponse(BaseModel):
    id: UUID
    user_id: int
    package_id: int
    package_name: str
    amount: Decimal
    credits_added: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)