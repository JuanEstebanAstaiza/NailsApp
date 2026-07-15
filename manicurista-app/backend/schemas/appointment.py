from __future__ import annotations

from pydantic import BaseModel, ConfigDict, field_validator
from datetime import date as dt_date, time as dt_time, datetime
from typing import Optional
import uuid


class AppointmentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    client_id: uuid.UUID
    service_id: uuid.UUID
    date: dt_date
    time: dt_time
    notes: Optional[str] = None

    @field_validator("time", mode="before")
    @classmethod
    def parse_time(cls, v):
        if isinstance(v, str):
            parts = v.split(":")
            return dt_time(int(parts[0]), int(parts[1]))
        return v


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    date: dt_date | None = None
    time: dt_time | None = None
    status: str | None = None  # scheduled, completed, cancelled
    notes: str | None = None

    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, v):
        if isinstance(v, str):
            return dt_date.fromisoformat(v)
        return v

    @field_validator("time", mode="before")
    @classmethod
    def parse_time(cls, v):
        if isinstance(v, str):
            parts = v.split(":")
            return dt_time(int(parts[0]), int(parts[1]))
        return v


class AppointmentResponse(AppointmentBase):
    id: uuid.UUID
    duration: int
    price: float
    discount_applied: float
    final_price: float
    status: str
    created_at: datetime
