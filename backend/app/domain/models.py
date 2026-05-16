from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.infrastructure.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

    # quan hệ 1-1 với bảng UserCredit
    credits = relationship("UserCredit", back_populates="user", uselist=False)

class Package(Base):
    __tablename__ = "packages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    credits_amount = Column(Integer, nullable=False)    

class UserCredit(Base):
    __tablename__ = "user_credits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    current_balance = Column(Integer, default=0)

    # quan hệ 1-1 với bảng User
    user = relationship("User", back_populates="credits")