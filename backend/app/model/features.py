from sqlalchemy import Column, Integer, Numeric, String
from sqlalchemy.orm import relationship
from app.config.database import Base

class Feature(Base):
    __tablename__ = "features"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True) # VD: 'IMAGE_GEN'
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)