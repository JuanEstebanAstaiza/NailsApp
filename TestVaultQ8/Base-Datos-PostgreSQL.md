# Base de Datos - PostgreSQL para Gestión de Citas de Manicurista

**Tags:** #postgresql #database #sql #schema #migrations #alembic #orm

---

## Referencias Cruzadas

- [[Arquitectura-App]] - Estructura general del proyecto y schemas
- [[Backend-FastAPI]] - Models SQLAlchemy ORM
- [[Tendencias-Apps-Manicurista]] - Client Accommodations (custom_timeframe)
- [[Sistemas-Fidelizacion]] - Loyalty tracking (appointments_count, rebooking)

---

## Configuración de PostgreSQL

### Instalación en Windows:
1. Descargar desde https://www.postgresql.org/download/windows/
2. Instalar con password para el usuario `postgres`
3. Crear database `nailbook`:
```sql
CREATE DATABASE nailbook;
```

### Variables de entorno (.env):
```env
DATABASE_URL=postgresql://postgres:tu_password@localhost:5432/nailbook
SECRET_KEY=tu-secret-key-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## Schema de Base de Datos (SQL)

### Tabla: clients

```sql
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    notes TEXT,
    custom_timeframe INTEGER,  -- Client Accommodations - [[Tendencias-Apps-Manicurista]]
    appointments_count INTEGER DEFAULT 0,  -- Loyalty tracking - [[Sistemas-Fidelizacion]]
    last_appointment_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_clients_name ON clients(name);
```

### Tabla: services

```sql
CREATE TABLE services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50),  -- manicure, pedicure, nail-art, combo
    duration INTEGER NOT NULL,  -- minutes
    price NUMERIC(10,2) NOT NULL,
    color VARCHAR(7) DEFAULT '#FF69B4',  -- For calendar visual - [[Tendencias-Apps-Manicurista]]
    loyalty_eligible BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_services_category ON services(category);
```

### Tabla: appointments

```sql
CREATE TABLE appointments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    service_id UUID NOT NULL REFERENCES services(id) ON DELETE RESTRICT,
    date DATE NOT NULL,
    time TIME NOT NULL,
    duration INTEGER NOT NULL,  -- minutes from service
    price NUMERIC(10,2) NOT NULL,
    discount_applied NUMERIC(5,2) DEFAULT 0,
    final_price NUMERIC(10,2),
    status VARCHAR(20) DEFAULT 'scheduled',  -- scheduled, completed, cancelled
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Unique constraint: no double booking same time
    CONSTRAINT unique_appointment_time UNIQUE (date, time)
);

-- Índices para queries rápidos - [[Arquitectura-App]]
CREATE INDEX idx_appointments_date ON appointments(date);
CREATE INDEX idx_appointments_client_id ON appointments(client_id);
CREATE INDEX idx_appointments_service_id ON appointments(service_id);
CREATE INDEX idx_appointments_status ON appointments(status);
```

### Tabla: loyalty_rules

```sql
CREATE TABLE loyalty_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,  -- null = global rule - [[Sistemas-Fidelizacion]]
    type VARCHAR(20) NOT NULL,  -- punch-card, rebooking
    trigger_count INTEGER NOT NULL,
    service_filter UUID REFERENCES services(id) ON DELETE SET NULL,  -- null = all services
    reward_type VARCHAR(20) NOT NULL,  -- discount, free-service
    reward_value NUMERIC(5,2) NOT NULL,
    rebooking_days INTEGER,  -- for rebooking type
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índice para queries de fidelización - [[Sistemas-Fidelizacion]]
CREATE INDEX idx_loyalty_rules_client_id ON loyalty_rules(client_id);
```

---

## Migrations con Alembic

### Inicializar Alembic:
```bash
cd backend
alembic init alembic
```

### Configurar alembic/env.py:
```python
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig
from config import get_settings
from database import Base

settings = get_settings()

config = config_ini_section  # from alembic.ini

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.get_main_option("sqlalchemy.url"):
    engine = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

fileConfig(config.config_file)

target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### Generar migration inicial:
```bash
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

---

## Queries Útiles

### Citas de hoy:
```sql
SELECT a.*, c.name as client_name, s.name as service_name
FROM appointments a
JOIN clients c ON a.client_id = c.id
JOIN services s ON a.service_id = s.id
WHERE a.date = CURRENT_DATE AND a.status != 'cancelled'
ORDER BY a.time;
```

### Citas de la semana:
```sql
SELECT a.*, c.name as client_name, s.name as service_name
FROM appointments a
JOIN clients c ON a.client_id = c.id
JOIN services s ON a.service_id = s.id
WHERE a.date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
  AND a.status != 'cancelled'
ORDER BY a.date, a.time;
```

### Clientas con citas completadas (para fidelización):
```sql
SELECT c.*, COUNT(a.id) as completed_count
FROM clients c
LEFT JOIN appointments a ON c.id = a.client_id AND a.status = 'completed'
GROUP BY c.id;
```

### Clientas que califican para descuento:
```sql
SELECT DISTINCT c.*
FROM clients c
JOIN loyalty_rules lr ON (lr.client_id = c.id OR lr.client_id IS NULL)
JOIN appointments a ON c.id = a.client_id AND a.status = 'completed'
WHERE lr.active = TRUE
  AND lr.type = 'punch-card'
GROUP BY c.id, lr.id
HAVING COUNT(a.id) >= lr.trigger_count;
```

### Clientas elegibles para rebooking:
```sql
SELECT DISTINCT c.*
FROM clients c
JOIN loyalty_rules lr ON (lr.client_id = c.id OR lr.client_id IS NULL)
WHERE lr.active = TRUE
  AND lr.type = 'rebooking'
  AND c.last_appointment_date IS NOT NULL
  AND CURRENT_DATE - c.last_appointment_date <= lr.rebooking_days;
```

### Ingresos del día:
```sql
SELECT SUM(a.final_price) as total_revenue, COUNT(*) as completed_count
FROM appointments a
WHERE a.date = CURRENT_DATE AND a.status = 'completed';
```

---

## Datos de Ejemplo (Seed Data)

### Servicios iniciales:
```sql
INSERT INTO services (name, category, duration, price, color, loyalty_eligible) VALUES
('Manicure Básico', 'manicure', 30, 25000, '#FF69B4', TRUE),
('Manicure con Gel', 'manicure', 60, 45000, '#E91E8C', TRUE),
('Pedicure Básico', 'pedicure', 30, 25000, '#9C27B0', TRUE),
('Pedicure con Gel', 'pedicure', 60, 45000, '#7B1FA2', TRUE),
('Nail Art Simple', 'nail-art', 30, 35000, '#FFD700', TRUE),
('Nail Art Premium', 'nail-art', 60, 55000, '#FFC107', TRUE),
('Combo Manicure + Pedicure', 'combo', 90, 70000, '#E91E8C', TRUE);
```

### Regla de fidelización global:
```sql
INSERT INTO loyalty_rules (type, trigger_count, reward_type, reward_value) VALUES
('punch-card', 8, 'discount', 15),  -- Después de 8 citas, 15% descuento
('rebooking', NULL, 'discount', 10);  -- Rebooking dentro de 7 días = 10% descuento
```

---

## 📋 Progreso de Base de Datos

**Ver:** [[Progreso-Desarrollo]] para tracking del progreso actual.

### Estado:
1. ✅ Schema SQL definido arriba
2. ✅ Índices definidos - [[Arquitectura-App]]
3. ✅ Migrations con Alembic configurado
4. ✅ Queries útiles documentados
5. ⏳ Seed data definida

**Ver también:** [[Backend-FastAPI]] para los Models SQLAlchemy ORM, [[Arquitectura-App]] para el schema completo de tablas.