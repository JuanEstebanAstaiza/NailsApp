from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import date, time, timedelta

from database import get_db
from models.appointment import Appointment
from models.client import Client
from models.service import Service
from models.loyalty_rule import LoyaltyRule
from schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentResponse

router = APIRouter(prefix="/api/appointments", tags=["Citas"])


def calculate_loyalty_discount(db: Session, client_id: uuid.UUID, service_id: uuid.UUID) -> tuple[float, str]:
    """Calculate loyalty discount for a client - [[Sistemas-Fidelizacion]]"""
    
    # Get all active loyalty rules for this client (or global rules)
    rules = db.query(LoyaltyRule).filter(
        LoyaltyRule.active == True,
        (LoyaltyRule.client_id == client_id) | (LoyaltyRule.client_id == None)
    ).all()
    
    # Check punch-card rules
    for rule in rules:
        if rule.type == "punch-card":
            if rule.service_filter:
                # Count appointments for this specific service
                count = db.query(Appointment).filter(
                    Appointment.client_id == client_id,
                    Appointment.service_id == rule.service_filter,
                    Appointment.status == "completed"
                ).count()
            else:
                # Count all appointments
                count = db.query(Appointment).filter(
                    Appointment.client_id == client_id,
                    Appointment.status == "completed"
                ).count()
            
            if count >= rule.trigger_count:
                if rule.reward_type == "discount":
                    return (float(rule.reward_value) / 100, f"Punch Card: {rule.reward_value}% descuento")
                elif rule.reward_type == "free-service":
                    # Get the service price for free service calculation
                    service = db.query(Service).filter(Service.id == service_id).first()
                    if service:
                        return (1.0, f"Punch Card: Servicio gratis ({rule.trigger_count} citas completadas)")
    
    # Check rebooking rules
    for rule in rules:
        if rule.type == "rebooking" and rule.rebooking_days:
            client = db.query(Client).filter(Client.id == client_id).first()
            if client and client.last_appointment_date:
                days_since_last = (date.today() - client.last_appointment_date).days
                if days_since_last <= rule.rebooking_days:
                    return (float(rule.reward_value) / 100, f"Rebooking: {rule.reward_value}% descuento")
    
    return (0.0, "")


@router.get("/", response_model=List[AppointmentResponse])
def list_appointments(
    date_filter: Optional[date] = None,
    client_id: Optional[uuid.UUID] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Listar citas con filtros"""
    query = db.query(Appointment)
    
    if date_filter:
        query = query.filter(Appointment.date == date_filter)
    if client_id:
        query = query.filter(Appointment.client_id == client_id)
    if status:
        query = query.filter(Appointment.status == status)
    
    appointments = query.offset(skip).limit(limit).all()
    return appointments


@router.post("/", response_model=AppointmentResponse)
def create_appointment(
    appointment_data: AppointmentCreate, 
    db: Session = Depends(get_db)
):
    """Crear nueva cita + auto-apply loyalty discount - [[Sistemas-Fidelizacion]]"""
    
    # Check for time conflicts
    existing = db.query(Appointment).filter(
        Appointment.date == appointment_data.date,
        Appointment.time == appointment_data.time,
        Appointment.status == "scheduled"
    ).first()
    
    if existing:
        raise HTTPException(status_code=409, detail="Ya existe una cita en ese horario")
    
    # Get service details for duration and price
    service = db.query(Service).filter(Service.id == appointment_data.service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    
    # Calculate loyalty discount - [[Sistemas-Fidelizacion]]
    discount_rate, discount_reason = calculate_loyalty_discount(
        db, appointment_data.client_id, appointment_data.service_id
    )
    
    price = float(service.price)
    final_price = price * (1 - discount_rate) if discount_rate > 0 else price
    
    # Create appointment with loyalty discount applied
    appointment = Appointment(
        client_id=appointment_data.client_id,
        service_id=appointment_data.service_id,
        date=appointment_data.date,
        time=appointment_data.time,
        duration=service.duration,
        price=price,
        discount_applied=discount_rate * 100 if discount_rate > 0 else 0,
        final_price=final_price,
        status="scheduled",
        notes=appointment_data.notes
    )
    
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(appointment_id: uuid.UUID, db: Session = Depends(get_db)):
    """Obtener cita por ID"""
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    return appointment


@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: uuid.UUID, 
    appointment_data: AppointmentUpdate, 
    db: Session = Depends(get_db)
):
    """Actualizar cita"""
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    
    # Check for time conflicts (if date/time changed)
    if appointment_data.date or appointment_data.time:
        new_date = appointment_data.date or appointment.date
        new_time = appointment_data.time or appointment.time
        
        existing = db.query(Appointment).filter(
            Appointment.id != appointment_id,
            Appointment.date == new_date,
            Appointment.time == new_time,
            Appointment.status == "scheduled"
        ).first()
        
        if existing:
            raise HTTPException(status_code=409, detail="Ya existe una cita en ese horario")
    
    update_data = appointment_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(appointment, key, value)
    
    db.commit()
    db.refresh(appointment)
    return appointment


@router.put("/{appointment_id}/complete", response_model=AppointmentResponse)
def complete_appointment(
    appointment_id: uuid.UUID, 
    db: Session = Depends(get_db)
):
    """Marcar cita como completada y trigger loyalty check - [[Sistemas-Fidelizacion]]"""
    
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    
    # Update status to completed
    appointment.status = "completed"
    
    # Increment client's appointments count for loyalty - [[Sistemas-Fidelizacion]]
    client = db.query(Client).filter(Client.id == appointment.client_id).first()
    if client:
        client.appointments_count += 1
        client.last_appointment_date = appointment.date
    
    db.commit()
    db.refresh(appointment)
    return appointment


@router.delete("/{appointment_id}")
def cancel_appointment(appointment_id: uuid.UUID, db: Session = Depends(get_db)):
    """Cancelar cita"""
    
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    
    # Update status to cancelled instead of deleting
    appointment.status = "cancelled"
    
    db.commit()
    return {"message": "Cita cancelada"}