import datetime

from sqlalchemy import Column, DateTime, Integer, Numeric, String
from sqlalchemy.orm import relationship
from app.config.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    balance = Column(Numeric(10, 2), default=0.00, nullable=False)

    # Lấy các tính năng user đã unlock
    unlocked_features = relationship("UserFeature", back_populates="user")