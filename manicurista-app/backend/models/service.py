from sqlalchemy import Column, String, Integer, Numeric, Boolean, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from database import Base
import uuid


class Service(Base):
    __tablename__ = "services"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    category = Column(String(50))  # manicure, pedicure, nail-art, combo
    duration = Column(Integer, nullable=False)  # minutes
    price = Column(Numeric(10,2), nullable=False)
    color = Column(String(7), default="#FF69B4")  # For calendar visual - [[Tendencias-Apps-Manicurista]]
    loyalty_eligible = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Service(id={self.id}, name='{self.name}')>"