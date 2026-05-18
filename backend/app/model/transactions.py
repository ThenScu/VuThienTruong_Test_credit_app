import uuid
from datetime import datetime

from sqlalchemy import UUID, Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from app.config.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"))
    package_id = Column(Integer, ForeignKey("packages.id"))
    amount = Column(Numeric(10, 2), nullable=False)
    credits_added = Column(Integer, nullable=False)
    status = Column(String(20), default="PENDING") # PENDING, SUCCESS, FAILED
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    package = relationship("Package")

    @property
    def package_name(self) -> str:
        """Tự động móc tên gói thông qua mối quan hệ ngoại khóa"""
        return self.package.name if self.package else "Gói không xác định"