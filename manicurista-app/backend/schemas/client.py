from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from datetime import date as dt_date, datetime
from typing import Optional
import uuid


class ClientBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None
    custom_timeframe: Optional[int] = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None
    custom_timeframe: Optional[int] = None


class ClientResponse(ClientBase):
    id: uuid.UUID
    appointments_count: int
    last_appointment_date: dt_date | None = None
    created_at: datetime
