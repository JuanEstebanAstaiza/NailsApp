from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import date

from database import get_db
from models.loyalty_rule import LoyaltyRule
from models.client import Client
from models.service import Service
from models.appointment import Appointment
from schemas.loyalty_rule import LoyaltyRuleCreate, LoyaltyRuleUpdate, LoyaltyRuleResponse

router = APIRouter(prefix="/api/loyalty", tags=["Fidelización"])


@router.get("/rules/{rule_id}", response_model=LoyaltyRuleResponse)
def get_loyalty_rule(rule_id: uuid.UUID, db: Session = Depends(get_db)):
    """Obtener una regla de fidelización por ID"""
    rule = db.query(LoyaltyRule).filter(LoyaltyRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Regla no encontrada")
    return rule


@router.get("/rules/", response_model=List[LoyaltyRuleResponse])
def list_loyalty_rules(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Listar todas las reglas de fidelización"""
    rules = db.query(LoyaltyRule).offset(skip).limit(limit).all()
    return rules


@router.post("/rules/", response_model=LoyaltyRuleResponse)
def create_loyalty_rule(rule_data: LoyaltyRuleCreate, db: Session = Depends(get_db)):
    """Crear nueva regla de fidelización"""
    rule = LoyaltyRule(**rule_data.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.put("/rules/{rule_id}", response_model=LoyaltyRuleResponse)
def update_loyalty_rule(
    rule_id: uuid.UUID, 
    rule_data: LoyaltyRuleUpdate, 
    db: Session = Depends(get_db)
):
    """Actualizar regla de fidelización"""
    rule = db.query(LoyaltyRule).filter(LoyaltyRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Regla no encontrada")

    update_data = rule_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(rule, key, value)

    db.commit()
    db.refresh(rule)
    return rule


@router.delete("/rules/{rule_id}")
def delete_loyalty_rule(rule_id: uuid.UUID, db: Session = Depends(get_db)):
    """Eliminar regla de fidelización"""
    rule = db.query(LoyaltyRule).filter(LoyaltyRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Regla no encontrada")

    db.delete(rule)
    db.commit()
    return {"message": "Regla eliminada"}


@router.get("/status/{client_id}")
def get_loyalty_status(client_id: uuid.UUID, db: Session = Depends(get_db)):
    """Get loyalty status for a client - [[Sistemas-Fidelizacion]]"""
    
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # Get all active loyalty rules for this client (or global rules)
    rules = db.query(LoyaltyRule).filter(
        LoyaltyRule.active == True,
        (LoyaltyRule.client_id == client_id) | (LoyaltyRule.client_id == None)
    ).all()

    status_list = []

    for rule in rules:
        if rule.type == "punch-card":
            if rule.service_filter:
                count = db.query(Appointment).filter(
                    Appointment.client_id == client_id,
                    Appointment.service_id == rule.service_filter,
                    Appointment.status == "completed"
                ).count()
            else:
                count = db.query(Appointment).filter(
                    Appointment.client_id == client_id,
                    Appointment.status == "completed"
                ).count()

            progress = min(count / rule.trigger_count, 1.0) if rule.trigger_count > 0 else 0

            status_list.append({
                "rule_type": "punch-card",
                "trigger_count": rule.trigger_count,
                "current_count": count,
                "progress": round(progress * 100),
                "reward_type": rule.reward_type,
                "reward_value": float(rule.reward_value),
                "qualified": count >= rule.trigger_count,
                "service_filter_name": None
            })

            # Get service filter name if applicable
            if rule.service_filter:
                service = db.query(Service).filter(Service.id == rule.service_filter).first()
                status_list[-1]["service_filter_name"] = service.name if service else None

        elif rule.type == "rebooking":
            days_since_last = 0
            if client.last_appointment_date:
                days_since_last = (date.today() - client.last_appointment_date).days

            eligible = days_since_last <= rule.rebooking_days

            status_list.append({
                "rule_type": "rebooking",
                "rebooking_days": rule.rebooking_days,
                "days_since_last": days_since_last,
                "eligible": eligible,
                "reward_value": float(rule.reward_value),
                "last_appointment_date": client.last_appointment_date.isoformat() if client.last_appointment_date else None
            })

    return {
        "client_id": str(client.id),
        "client_name": client.name,
        "appointments_count": client.appointments_count,
        "rules_status": status_list
    }