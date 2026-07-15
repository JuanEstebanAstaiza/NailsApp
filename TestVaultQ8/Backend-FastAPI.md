# Backend - FastAPI para Gestión de Citas de Manicurista

**Tags:** #fastapi #backend #python #api #rest #crud #pydantic #sqlalchemy

---

## Referencias Cruzadas

- [[Arquitectura-App]] - Estructura general del proyecto
- [[Tendencias-Apps-Manicurista]] - Tendencias que inspiran el diseño
- [[Sistemas-Fidelizacion]] - Sistema de descuentos y fidelización

---

## Stack Backend

### Python + FastAPI
- Framework moderno para APIs RESTful
- Type hints con Pydantic para validación automática
- Documentación Swagger/OpenAPI generada automáticamente (`/docs`)
- Async support para operaciones concurrentes

### SQLAlchemy ORM
- ORM para PostgreSQL
- Models declarativos con type hints
- Foreign keys para integridad referencial
- Migrations con Alembic

### Pydantic Schemas
- Validación automática de requests/responses
- Type safety en toda la API
- Serialización automática a JSON

---

## Estructura del Backend

```
backend/
├── main.py                       # Entry point de FastAPI
├── config.py                     # Configuración (DB, env vars)
├── database.py                   # Conexión a PostgreSQL + SessionLocal
├── models/                       # SQLAlchemy ORM models
│   ├── client.py                 # Modelo Cliente
│   ├── service.py                # Modelo Servicio
│   ├── appointment.py            # Modelo Cita
│   └── loyalty_rule.py           # Modelo Regla de Fidelización
├── schemas/                      # Pydantic schemas (request/response)
│   ├── client.py                 # Schema Cliente
│   ├── service.py                # Schema Servicio
│   ├── appointment.py            # Schema Cita
│   └── loyalty_rule.py           # Schema Regla de Fidelización
├── routers/                      # API endpoints (CRUD)
│   ├── clients.py                # CRUD Clientes
│   ├── services.py               # CRUD Servicios
│   ├── appointments.py           # CRUD Citas + Loyalty check
│   └── loyalty.py                # CRUD Fidelización + Status
├── alembic/                      # Database migrations
│   ├── env.py
│   └── versions/                 # Migration scripts
├── requirements.txt              # Python dependencies
└── .env                          # Environment variables (no commit)
```

---

## Archivos de Configuración

### config.py

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/nailbook"
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
```

### database.py

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import get_settings

settings = get_settings()

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## Models (SQLAlchemy ORM)

### models/client.py

```python
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
```

### models/service.py

```python
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
```

### models/appointment.py

```python
from sqlalchemy import Column, String, Integer, Numeric, Date, Time, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from database import Base
import uuid

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), nullable=False)
    service_id = Column(UUID(as_uuid=True), nullable=False)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    duration = Column(Integer, nullable=False)  # minutes from service
    price = Column(Numeric(10,2), nullable=False)
    discount_applied = Column(Numeric(5,2), default=0)
    final_price = Column(Numeric(10,2))
    status = Column(String(20), default="scheduled")  # scheduled, completed, cancelled
    notes = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Foreign keys
    client = relationship("Client", back_populates="appointments")
    service = relationship("Service", back_populates="appointments")
```

### models/loyalty_rule.py

```python
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

    # Foreign keys
    client = relationship("Client", back_populates="loyalty_rules")
    service_filter_obj = relationship("Service", foreign_keys=[service_filter])
```

---

## Schemas (Pydantic)

### schemas/client.py

```python
from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
import uuid

class ClientBase(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None
    custom_timeframe: Optional[int] = None

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None
    custom_timeframe: Optional[int] = None

class ClientResponse(ClientBase):
    id: uuid.UUID
    appointments_count: int
    last_appointment_date: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True
```

### schemas/service.py

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid

class ServiceBase(BaseModel):
    name: str
    category: Optional[str] = None
    duration: int  # minutes
    price: float
    color: Optional[str] = "#FF69B4"
    loyalty_eligible: bool = True

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    duration: Optional[int] = None
    price: Optional[float] = None
    color: Optional[str] = None
    loyalty_eligible: Optional[bool] = None

class ServiceResponse(ServiceBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
```

### schemas/appointment.py

```python
from pydantic import BaseModel
from datetime import date, time, datetime
from typing import Optional
import uuid

class AppointmentBase(BaseModel):
    client_id: uuid.UUID
    service_id: uuid.UUID
    date: date
    time: time
    notes: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    date: Optional[date] = None
    time: Optional[time] = None
    status: Optional[str] = None  # scheduled, completed, cancelled
    notes: Optional[str] = None

class AppointmentResponse(AppointmentBase):
    id: uuid.UUID
    duration: int
    price: float
    discount_applied: float
    final_price: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
```

### schemas/loyalty_rule.py

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid

class LoyaltyRuleBase(BaseModel):
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

    class Config:
        from_attributes = True
```

---

## Routers (API Endpoints)

### routers/clients.py

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from database import get_db
from models.client import Client
from schemas.client import ClientCreate, ClientUpdate, ClientResponse

router = APIRouter(prefix="/api/clients", tags=["Clientes"])

@router.get("/", response_model=List[ClientResponse])
def list_clients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    clients = db.query(Client).offset(skip).limit(limit).all()
    return clients

@router.post("/", response_model=ClientResponse)
def create_client(client_data: ClientCreate, db: Session = Depends(get_db)):
    client = Client(**client_data.model_dump())
    db.add(client)
    db.commit()
    db.refresh(client)
    return client

@router.get("/{client_id}", response_model=ClientResponse)
def get_client(client_id: uuid.UUID, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return client

@router.put("/{client_id}", response_model=ClientResponse)
def update_client(client_id: uuid.UUID, client_data: ClientUpdate, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    update_data = client_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(client, key, value)
    
    db.commit()
    db.refresh(client)
    return client

@router.delete("/{client_id}")
def delete_client(client_id: uuid.UUID, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    db.delete(client)
    db.commit()
    return {"message": "Cliente eliminado"}
```

### routers/services.py

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from database import get_db
from models.service import Service
from schemas.service import ServiceCreate, ServiceUpdate, ServiceResponse

router = APIRouter(prefix="/api/services", tags=["Servicios"])

@router.get("/", response_model=List[ServiceResponse])
def list_services(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    services = db.query(Service).offset(skip).limit(limit).all()
    return services

@router.post("/", response_model=ServiceResponse)
def create_service(service_data: ServiceCreate, db: Session = Depends(get_db)):
    service = Service(**service_data.model_dump())
    db.add(service)
    db.commit()
    db.refresh(service)
    return service

@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(service_id: uuid.UUID, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return service

@router.put("/{service_id}", response_model=ServiceResponse)
def update_service(service_id: uuid.UUID, service_data: ServiceUpdate, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    
    update_data = service_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(service, key, value)
    
    db.commit()
    db.refresh(service)
    return service

@router.delete("/{service_id}")
def delete_service(service_id: uuid.UUID, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    
    db.delete(service)
    db.commit()
    return {"message": "Servicio eliminado"}
```

### routers/appointments.py (CRUD + Loyalty Check)

```python
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
                    return (rule.reward_value / 100, f"Punch Card: {rule.reward_value}% descuento")
                elif rule.reward_type == "free-service":
                    # Get the service price for free service calculation
                    service = db.query(Service).filter(Service.id == service_id).first()
                    if service:
                        return (1.0, f"Punch Card: Servicio gratis ({rule.reward_value} citas completadas)")
    
    # Check rebooking rules
    for rule in rules:
        if rule.type == "rebooking" and rule.rebooking_days:
            client = db.query(Client).filter(Client.id == client_id).first()
            if client and client.last_appointment_date:
                days_since_last = (date.today() - client.last_appointment_date).days
                if days_since_last <= rule.rebooking_days:
                    return (rule.rebooking_value / 100, f"Rebooking: {rule.rebooking_value}% descuento")
    
    return (0, "")

@router.get("/", response_model=List[AppointmentResponse])
def list_appointments(
    date_filter: Optional[date] = None,
    client_id: Optional[uuid.UUID] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
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
    """Mark appointment as completed and trigger loyalty check - [[Sistemas-Fidelizacion]]"""
    
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
    """Cancel (delete) an appointment"""
    
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    
    # Update status to cancelled instead of deleting
    appointment.status = "cancelled"
    
    db.commit()
    return {"message": "Cita cancelada"}
```

### routers/loyalty.py (CRUD + Status)

```python
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

@router.get("/rules/", response_model=List[LoyaltyRuleResponse])
def list_loyalty_rules(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    rules = db.query(LoyaltyRule).offset(skip).limit(limit).all()
    return rules

@router.post("/rules/", response_model=LoyaltyRuleResponse)
def create_loyalty_rule(rule_data: LoyaltyRuleCreate, db: Session = Depends(get_db)):
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
                "reward_value": float(rule.rebooking_value) if hasattr(rule, 'rebooking_value') else float(rule.reward_value),
                "last_appointment_date": client.last_appointment_date.isoformat() if client.last_appointment_date else None
            })
    
    return {
        "client_id": str(client.id),
        "client_name": client.name,
        "appointments_count": client.appointments_count,
        "rules_status": status_list
    }
```

---

## main.py (Entry Point)

```python
from fastapi import FastAPI
from routers import clients, services, appointments, loyalty

app = FastAPI(
    title="NailBook API",
    description="API para gestión de citas de manicurista con sistema de fidelización",
    version="1.0.0"
)

# Include routers
app.include_router(clients.router)
app.include_router(services.router)
app.include_router(appointments.router)
app.include_router(loyalty.router)

@app.get("/")
def root():
    return {
        "message": "NailBook API - Gestión de Citas para Manicurista",
        "docs": "/docs"
    }
```

---

## requirements.txt

```
fastapi==0.115.0
uvicorn==0.32.0
sqlalchemy==2.0.36
psycopg2-binary==2.9.10
pydantic==2.10.0
pydantic-settings==2.7.0
alembic==1.14.0
python-dateutil==2.9.0.post0
```

---

## 📋 Progreso de Backend

**Ver:** [[Progreso-Desarrollo]] para tracking del progreso actual.

### Módulos Backend:
1. ✅ Configuración inicial (FastAPI, PostgreSQL, Alembic) - Archivos definidos arriba
2. ⏳ Módulo 2: CRUD Clientes - `routers/clients.py` definido arriba
3. ⏳ Módulo 3: CRUD Servicios - `routers/services.py` definido arriba
4. ⏳ Módulo 5: Sistema de Fidelización - `routers/appointments.py` (loyalty check) + `routers/loyalty.py` definidos arriba
5. ⏳ Módulo 4: CRUD Citas + Loyalty Check - `routers/appointments.py` definido arriba
6. ⏳ Dashboard API

**Ver también:** [[Arquitectura-App]] para la estructura completa del proyecto, [[Sistemas-Fidelizacion]] para los detalles del sistema de descuentos.