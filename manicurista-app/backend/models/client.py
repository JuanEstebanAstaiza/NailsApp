from sqlalchemy import Column, String, Text, Integer, Date, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from database import Base
import uuid


class Client(Base):
    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    phone = Column(String(20))
    email = Column(String(100))
    notes = Column(Text)
    custom_timeframe = Column(Integer)  # Client Accommodations - [[Tendencias-Apps-Manicurista]]
    appointments_count = Column(Integer, default=0)  # Loyalty tracking - [[Sistemas-Fidelizacion]]
    last_appointment_date = Column(Date)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Client(id={self.id}, name='{self.name}')>"