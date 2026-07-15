from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
import uuid


class ServiceBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    category: Optional[str] = None
    duration: int  # minutes
    price: float
    color: Optional[str] = "#FF69B4"
    loyalty_eligible: bool = True


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: Optional[str] = None
    category: Optional[str] = None
    duration: Optional[int] = None
    price: Optional[float] = None
    color: Optional[str] = None
    loyalty_eligible: Optional[bool] = None


class ServiceResponse(ServiceBase):
    id: uuid.UUID
    created_at: datetime
