# Arquitectura del Sistema - App Manicurista

**Tags:** #arquitectura #fastapi #postgresql #vuejs #tailwindcss #punch-card #loyalty #appointment-management #nail-salon

**Created:** 2026-06-10
**Last Updated:** 2026-06-10

---

## Resumen Ejecutivo

Arquitectura de una app web para manejar citas como manicurista con sistema de fidelización (punch-card) que aplica descuentos después de X citas. Basada en tendencias de apps como GlossGenius, Vagaro y Fresha para nail salons.

**Referencias:** [[Tendencias-Apps-Manicurista]], [[Sistemas-Fidelizacion]]

---

## Stack Tecnológico

### Backend
| Componente | Tecnología | Justificación |
|------------|-----------|---------------|
| Framework | FastAPI | Async, auto-docs (Swagger), type hints, rápido desarrollo |
| ORM | SQLAlchemy 2.0 | Mapeo objeto-relacional, migrations con Alembic |
| Base de Datos | PostgreSQL | UUID nativo, JSONB, robusto para producción |
| Testing | pytest + TestClient | Tests integration con base SQLite temporal |

### Frontend
| Componente | Tecnología | Justificación |
|------------|-----------|---------------|
| Framework | Vue.js 3 (Composition API) | Reactividad, componentes reutilizables, curva de aprendizaje baja |
| CSS | Tailwind CSS | Utility-first, rápido prototipado, responsive por defecto |
| Router | Vue Router | SPA navigation |
| HTTP Client | Axios | Request interceptors, auto JSON serialization |

### Infraestructura
| Componente | Tecnología | Justificación |
|------------|-----------|---------------|
| Containerización | Docker + docker-compose | Reproducibilidad, fácil deployment |
| DB Container | PostgreSQL 16 | Consistencia con producción |
| Cache (future) | Redis | Session cache, rate limiting |

---

## Modelo de Datos (Ver [[Base-Datos-PostgreSQL]])

### Tabla: clients
```sql
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,          -- Nombre único de clienta
    phone VARCHAR(20),                          -- Teléfono con código país
    email VARCHAR(100),                         -- Email opcional
    notes TEXT,                                 -- Notas personalizadas
    custom_timeframe INTEGER,                   -- Client Accommodations - preferencias de tiempo
    appointments_count INTEGER DEFAULT 0,       -- Loyalty tracking - citas completadas
    last_appointment_date DATE,                 -- Última cita (para rebooking eligibility)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Justificación:**
- `name UNIQUE`: Evita duplicados de clientas (tendencia en apps como GlossGenius - clean client list)
- `appointments_count`: Auto-incremented cuando appointment se completa → trigger para punch-card loyalty
- `last_appointment_date`: Calcula days_since_last para rebooking eligibility

### Tabla: services
```sql
CREATE TABLE services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,                 -- Nombre del servicio
    category VARCHAR(50),                       -- manicure, pedicure, nail-art, etc.
    duration INTEGER NOT NULL,                  -- Duración en minutos
    price DECIMAL(10,2) NOT NULL,               -- Precio base
    color VARCHAR(7),                           -- Color asociado (para visualización)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Justificación:**
- `category`: Permite filtrar servicios por tipo → service_filter en loyalty rules
- `color`: Visualización en calendario (tendencia en apps como GlossGenius - premium aesthetic)

### Tabla: appointments
```sql
CREATE TABLE appointments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(id),
    service_id UUID NOT NULL REFERENCES services(id),
    date DATE NOT NULL,                         -- Fecha de la cita
    time TIME NOT NULL,                         -- Hora de inicio
    duration INTEGER NOT NULL,                  -- Duración en minutos (de servicio)
    status VARCHAR(20) DEFAULT 'scheduled',     -- scheduled, completed, cancelled
    notes TEXT,                                 -- Notas de la cita
    discount_applied DECIMAL(5,2),              -- Descuento aplicado (si hay loyalty reward)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Justificación:**
- `status`: Track estado de cita → solo completed appointments cuentan para punch-card
- `discount_applied`: Registra descuento aplicado por loyalty rule → tracking de ROI

### Tabla: loyalty_rules
```sql
CREATE TABLE loyalty_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id),      -- NULL = global rule (applies to all)
    type VARCHAR(20) NOT NULL,                  -- punch-card, rebooking, points, tiered
    trigger_count INTEGER NOT NULL,             -- Número de citas necesarias
    service_filter UUID REFERENCES services(id),-- NULL = todos los servicios
    reward_type VARCHAR(20) NOT NULL,           -- discount, free-service, upgrade
    reward_value DECIMAL(5,2) NOT NULL,         -- Porcentaje o valor de recompensa
    rebooking_days INTEGER,                    -- Para rebooking rules (7 días)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Justificación:**
- `client_id NULL`: Global rules aplican a todas las clientas (tendencia en apps como Vagaro - promotional packages)
- `service_filter`: Punch-card específico para un servicio (ej: 8 gel manicures = free)
- `type`: Extensible para múltiples formatos de loyalty

---

## API Endpoints

### Clients CRUD
| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/api/clients/` | Listar todas las clientas | - | `ClientResponse[]` |
| POST | `/api/clients/` | Crear nueva clienta | `ClientCreate` | `ClientResponse` |
| GET | `/api/clients/{id}` | Obtener clienta por ID | - | `ClientResponse` |
| PUT | `/api/clients/{id}` | Actualizar clienta | `ClientUpdate` | `ClientResponse` |
| DELETE | `/api/clients/{id}` | Eliminar clienta | - | `{message: "Cliente eliminado"}` |

### Services CRUD
| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/api/services/` | Listar todos los servicios | - | `ServiceResponse[]` |
| POST | `/api/services/` | Crear nuevo servicio | `ServiceCreate` | `ServiceResponse` |
| GET | `/api/services/{id}` | Obtener servicio por ID | - | `ServiceResponse` |
| PUT | `/api/services/{id}` | Actualizar servicio | `ServiceUpdate` | `ServiceResponse` |
| DELETE | `/api/services/{id}` | Eliminar servicio | - | `{message: "Servicio eliminado"}` |

### Appointments CRUD
| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/api/appointments/` | Listar citas (con filtros) | `?date=YYYY-MM-DD&client_id=UUID` | `AppointmentResponse[]` |
| POST | `/api/appointments/` | Crear nueva cita | `AppointmentCreate` | `AppointmentResponse` |
| GET | `/api/appointments/{id}` | Obtener cita por ID | - | `AppointmentResponse` |
| PUT | `/api/appointments/{id}` | Actualizar cita | `AppointmentUpdate` | `AppointmentResponse` |
| DELETE | `/api/appointments/{id}` | Cancelar cita | - | `{message: "Cita cancelada"}` |
| PUT | `/api/appointments/{id}/complete` | Completar cita | - | `AppointmentResponse` (auto-increment appointments_count) |

### Loyalty Rules CRUD
| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/api/loyalty/rules/` | Listar todas las reglas | - | `LoyaltyRuleResponse[]` |
| POST | `/api/loyalty/rules/` | Crear nueva regla | `LoyaltyRuleCreate` | `LoyaltyRuleResponse` |
| GET | `/api/loyalty/rules/{id}` | Obtener regla por ID | - | `LoyaltyRuleResponse` |
| PUT | `/api/loyalty/rules/{id}` | Actualizar regla | `LoyaltyRuleUpdate` | `LoyaltyRuleResponse` |
| DELETE | `/api/loyalty/rules/{id}` | Eliminar regla | - | `{message: "Regla eliminada"}` |

### Loyalty Status
| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/api/loyalty/status/{client_id}` | Status de fidelización para clienta | - | `LoyaltyStatusResponse` |

**LoyaltyStatusResponse:**
```json
{
  "client_id": "uuid",
  "appointments_count": 8,
  "last_appointment_date": "2026-06-09",
  "rules_status": [
    {
      "rule_type": "punch-card",
      "current_count": 8,
      "trigger_count": 8,
      "qualified": true,
      "reward_type": "discount",
      "reward_value": 15.0,
      "service_filter_name": "Manicure Clásico"
    },
    {
      "rule_type": "rebooking",
      "days_since_last": 1,
      "eligible": true,
      "reward_type": "discount",
      "reward_value": 10.0,
      "rebooking_days": 7
    }
  ]
}
```

---

## Frontend Components (Ver [[Propuesta-Frontend]])

### DashboardView.vue
- **Stats cards**: Total clientas, citas hoy, ingresos del mes
- **Today's appointments**: Lista de citas de hoy con status
- **Loyalty alerts**: Clientas que califican para recompensa esta semana

### CalendarView.vue
- **Monthly calendar**: Vista mensual con citas color-coded por servicio
- **Day detail panel**: Click en día → lista de citas del día
- **Quick booking**: Crear cita desde el calendario

### ClientsView.vue
- **Client list**: Tabla con búsqueda y filtros
- **Client detail panel**: Historial de citas, notas, loyalty progress bar
- **Loyalty progress**: Visualización de punch-card (8/8 stamps)

### ServicesView.vue
- **Service catalog**: Lista de servicios con precio, duración, color
- **CRUD operations**: Crear/editar/eliminar servicios

### LoyaltyView.vue
- **Rules management**: CRUD de reglas de fidelización
- **Global vs client-specific**: Toggle para rules globales o por clienta
- **Rule preview**: Preview de cómo se aplica la regla

---

## UX/UI Principles (Basados en Tendencias)

1. **Premium aesthetic** - GlossGenius-style clean, Instagram-worthy design
2. **No forced account creation** - Clientas pueden book sin crear cuenta (25% abandonment rate reduction)
3. **Progress bar visual** - Mostrar progreso de punch-card claramente
4. **Color-coded services** - Cada servicio tiene color en calendario
5. **Mobile-first responsive** - Tailwind CSS utility classes para mobile/desktop

---

## Referencias

- [[Tendencias-Apps-Manicurista]] - Tendencias del mercado 2025-2026
- [[Sistemas-Fidelizacion]] - Sistemas de fidelización detallados
- [[Base-Datos-PostgreSQL]] - Schema de base datos PostgreSQL
- [[Backend-FastAPI]] - Documentación del backend FastAPI
- [[Propuesta-Frontend]] - Propuesta de frontend Vue.js + Tailwind CSS