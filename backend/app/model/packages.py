from datetime import datetime
from sqlalchemy import Table, Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from app.config.database import Base

# Association table between packages and features
package_features = Table(
    "package_features",
    Base.metadata,
    Column("package_id", Integer, ForeignKey("packages.id", ondelete="CASCADE"), primary_key=True),
    Column("feature_id", Integer, ForeignKey("features.id", ondelete="CASCADE"), primary_key=True),
)

class Package(Base):
    __tablename__ = "packages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String)
    price = Column(Numeric(10, 2), nullable=False)
    credits_awarded = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship để lấy list features của gói này
    features = relationship("Feature", secondary=package_features, lazy="joined")