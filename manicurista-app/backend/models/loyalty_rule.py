from sqlalchemy import Column, String, Integer, Numeric, Boolean, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from database import Base
import uuid


class LoyaltyRule(Base):
    __tablename__ = "loyalty_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True))  # null = global rule - [[Sistemas-Fidelizacion]]
    type = Column(String(20), nullable=False)  # punch-card, rebooking
    trigger_count = Column(Integer, nullable=False)
    service_filter = Column(UUID(as_uuid=True))  # null = all services
    reward_type = Column(String(20), nullable=False)  # discount, free-service
    reward_value = Column(Numeric(5,2), nullable=False)
    rebooking_days = Column(Integer)  # for rebooking type
    active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<LoyaltyRule(id={self.id}, type='{self.type}')>"