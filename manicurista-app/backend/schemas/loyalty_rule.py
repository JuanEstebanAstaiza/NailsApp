from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
import uuid


class LoyaltyRuleBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    client_id: Optional[uuid.UUID] = None  # null = global rule - [[Sistemas-Fidelizacion]]
    type: str  # punch-card, rebooking
    trigger_count: int
    service_filter: Optional[uuid.UUID] = None  # null = all services
    reward_type: str  # discount, free-service
    reward_value: float
    rebooking_days: Optional[int] = None


class LoyaltyRuleCreate(LoyaltyRuleBase):
    pass


class LoyaltyRuleUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    client_id: Optional[uuid.UUID] = None
    type: Optional[str] = None
    trigger_count: Optional[int] = None
    service_filter: Optional[uuid.UUID] = None
    reward_type: Optional[str] = None
    reward_value: Optional[float] = None
    rebooking_days: Optional[int] = None
    active: Optional[bool] = None


class LoyaltyRuleResponse(LoyaltyRuleBase):
    id: uuid.UUID
    active: bool
    created_at: datetime
