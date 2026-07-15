# Propuesta de Frontend - App NailBook (Manicurista)

**Tags:** #frontend #nailbook #manicurista #propuesta #benchmarking #seguridad

---

## Estado Actual del Proyecto

- Backend: FastAPI + PostgreSQL ✅ COMPLETADO
- Tests: 47 tests pasados, CERO warnings ✅
- Sistema de fidelización con descuentos ✅
- Documentación en Obsidian: 5 documentos con wikilinks y tags ✅

---

## Benchmarking - Apps de Citas para Manicuristas/Beauty Salons

### Apps Top del Mercado (2025-2026)

| App | Diseño UI | Facilidad Uso | Precio Mensual | Mejor Para |
|---|---|---|---|---|
| **Mangomint** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ~$470/mes | Salones de alto nivel, diseño premium |
| **GlossGenius** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | $39-99/mes | Solopreneurs, diseño moderno y elegante |
| **Booksy Biz** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Gratis (comisión) | Pequeños negocios, marketplace integrado |
| **Fresha** | ⭐⭐⭐ | ⭐⭐⭐⭐ | Gratis (solo transacciones) | Startups con presupuesto limitado |
| **Vagaro** | ⭐⭐⭐ | ⭐⭐⭐ | $25-30/mes | Multi-staff, funcionalidad completa |
| **Boulevard** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ~$470/mes | Salones grandes, operaciones complejas |

### Tendencias de Diseño UI Identificadas 🎨

1. **Mobile-First Design** - Todas las apps top son mobile-first
   - GlossGenius: "mobile-first package"
   - Booksy: "mobile app for managing client bookings"
   - Mangomint: "seamless client experience from booking to checkout"

2. **Diseño Elegante y Minimalista**
   - Mangomint: "sleek, modern interface", "polished brand experience"
   - GlossGenius: "stunning design", "chic and modern", "high-end services"
   - Booksy: "user-friendly and visually appealing design"

3. **Paleta de Colores Rosa/Pastel** - Dominante en apps de manicuristas
   - Rosas, lilas, dorados como colores principales
   - Fondos blancos con acentos pastel
   - Tipografía elegante y limpia

4. **Dashboard Visual con Calendario**
   - Calendarios interactivos con vista semanal/mensual
   - Cards de citas con color por servicio
   - Indicadores visuales de disponibilidad

5. **Sistema de Fidelización Visual**
   - Punch cards visuales (ej: "9 citas = 1 gratis")
   - Badges y logros para clientas frecuentes
   - Progress bars para descuentos

6. **Onboarding Sencillo**
   - Setup en menos de 5 minutos
   - Formularios paso a paso
   - Intake forms digitales para clientas

7. **Automatización de Recordatorios**
   - SMS/Email reminders automáticos
   - Waitlist para citas canceladas
   - Notificaciones push

### UX Patterns Identificados 🧠

- **Booking en 3 clicks**: Seleccionar servicio → Fecha/hora → Confirmar
- **Client Profile con historial completo**: Citas anteriores, servicios favoritos, notas
- **Loyalty Dashboard visual**: Progress bar + badge de nivel
- **Quick Actions**: "Rebook" (reagendar), "Add to waitlist", "Send reminder"

---

## Framework/Librería Frontend Recomendada

### Comparación de Frameworks (2025)

| Framework | Popularidad | Performance | Facilidad Aprendizaje | Ecosistema | Mejor Para |
|---|---|---|---|---|---|
| **React** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Apps grandes, comunidad masiva |
| **Vue.js** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Apps medianas, fácil aprendizaje |
| **Svelte** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Apps pequeñas, performance máxima |
| **Angular** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Enterprise apps, backend developers |

### 🏆 Recomendación: React + Tailwind CSS

#### ¿Por qué React?

1. **Comunidad más grande y ecosistema masivo** - Más componentes UI disponibles
2. **Mejor balance de comunidad vs simplicidad** (según Xuntos.nl)
3. **Component-based architecture** - Perfecto para reutilizar cards, modals, forms
4. **React Native** - Si en el futuro queremos app móvil nativa
5. **Herramientas de seguridad**: DOMPurify, Helmet.js, etc.

#### ¿Por qué Tailwind CSS?

1. **Utility-first CSS** - Desarrollo rápido sin escribir CSS personalizado
2. **Mobile-first responsive** - Built-in con breakpoints
3. **Diseño moderno y limpio** - Perfecto para estética de manicurista
4. **No conflictos de nombres** - No necesita preprocessor (SASS/LESS)
5. **Componentes reutilizables** - Classes consistentes en toda la app

#### Stack Completo Recomendado:

```
Frontend Stack:
├── React 18+ (component-based UI)
├── Tailwind CSS (utility-first styling)
├── React Router DOM (navegación SPA)
├── Axios (HTTP client para API calls)
├── DOMPurify (XSS protection - sanitización HTML)
├── Helmet.js (CSP headers)
└── js-cookie (CSRF token management)
```

#### Alternativa: Vue.js + Tailwind CSS

Si prefieres algo más fácil de aprender y con menos boilerplate:

```
Vue Stack:
├── Vue 3+ (progressive framework, single-file components)
├── Tailwind CSS (utility-first styling)
├── Vue Router (navegación SPA)
├── Axios (HTTP client para API calls)
├── DOMPurify (XSS protection - sanitización HTML)
└── js-cookie (CSRF token management)
```

**Vue es más fácil de aprender que React** según Xuntos.nl: "Vue.js is a mix of Angular and React strengths. The documentation is good and easy to understand."

---

## Seguridad Básica - Frontend + Backend

### Amenazas Principales Identificadas 🔒

1. **XSS (Cross-Site Scripting)** - Inyección de scripts maliciosos
2. **CSRF (Cross-Site Request Forgery)** - Solicitudes falsas en nombre del usuario
3. **CORS** - Acceso no autorizado desde otros dominios
4. **Token leaks** - Exposición de tokens JWT

### Seguridad Frontend 🛡️

#### 1. XSS Prevention

```javascript
// React: JSX automatically escapes values (default protection)
// Safe rendering: userName is escaped if it contains malicious code
<span>{userName}</span>

// DOMPurify for raw HTML content
import DOMPurify from 'dompurify';
const sanitizedHTML = DOMPurify.sanitize(userInput);

// NEVER use dangerouslySetInnerHTML without sanitization
// ❌ Dangerous: <div dangerouslySetInnerHTML={{__html: userInput}} />
// ✅ Safe: <div dangerouslySetInnerHTML={{__html: DOMPurify.sanitize(userInput)}} />
```

#### 2. CSRF Prevention

```javascript
// Include CSRF token in protected requests (POST, PUT, DELETE)
import axios from 'axios';
import Cookies from 'js-cookie';

const csrfToken = Cookies.get('csrf-token');
const apiClient = axios.create({
  headers: {
    'X-CSRF-Token': csrfToken,
  },
});

async function submitProtectedForm(data) {
  try {
    const response = await apiClient.post('/api/protected-action', data);
    return response.data;
  } catch (error) {
    console.error('CSRF protection failed:', error);
    throw error;
  }
}
```

#### 3. Content Security Policy (CSP)

```javascript
// Helmet.js for CSP headers in React
import Helmet from 'react-helmet';

<Helmet>
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' https://trusted-cdn.com; style-src 'self' 'unsafe-inline'" />
</Helmet>
```

#### 4. Token Storage - HttpOnly Cookies

```javascript
// Best practice: use HttpOnly, Secure cookies with SameSite=Strict
// Tokens out of JavaScript = reduced attack surface
// ❌ Dangerous: localStorage.setItem('token', jwtToken)
// ✅ Safe: Server sets cookie with HttpOnly + Secure + SameSite=Strict
```

#### 5. Dependency Management

```bash
# Scan dependencies for known vulnerabilities
npm audit          # Lists known vulnerabilities
npm audit fix      # Attempts to automatically fix issues
npx snyk test      # Scans dependencies with Snyk
```

### Seguridad Backend (FastAPI) 🛡️

#### 1. CORS Configuration - Restrict Origins

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific list only!
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "X-CSRF-Token"],
)
```

#### 2. Token-Based Authentication (JWT)

```python
# Use bearer token in Authorization header instead of cookies
# Token not sent automatically by browser = CSRF protection built-in
headers: {
    'Authorization': 'Bearer <jwt_token>'
}
```

#### 3. Pydantic Validation - Input Sanitization

```python
from pydantic import BaseModel, field_validator

class AppointmentCreate(BaseModel):
    client_id: uuid.UUID
    service_id: uuid.UUID
    date: dt_date
    time: dt_time
    
    @field_validator("notes", mode="before")
    @classmethod
    def sanitize_notes(cls, v):
        if isinstance(v, str):
            # Strip HTML tags to prevent XSS
            import re
            return re.sub(r'<[^>]+>', '', v)
        return v
```

#### 4. Rate Limiting - Prevent Brute Force

```python
# Use slowapi for rate limiting in FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

---

## Estructura de la App Frontend

### Pages/Components:

```
frontend/
├── index.html                    # Entry point
├── css/
│   ├── main.css                  # Tailwind CSS (compiled)
│   └── calendar.css              # Calendar-specific styles
├── js/
│   ├── app.js                    # React app entry point
│   ├── api.js                    # Axios API client with CSRF protection
│   ├── auth.js                   # JWT token management
│   ├── components/
│   │   ├── Dashboard.jsx         # Overview con citas del día
│   │   ├── Calendar.jsx          # Calendario interactivo semanal/mensual
│   │   ├── ClientList.jsx        # Lista de clientas
│   │   ├── ClientForm.jsx        # Formulario crear/editar clienta
│   │   ├── ServiceList.jsx       # Lista de servicios y precios
│   │   ├── AppointmentCard.jsx   # Card de cita con color por servicio
│   │   ├── LoyaltyBadge.jsx      # Badge visual de fidelización
│   │   └── Modal.jsx             # Modal reutilizable
│   └── utils/
│       ├── dateUtils.js          # Formateo de fechas/horas
│       └── securityUtils.js      # XSS sanitization, CSRF token handling
└── assets/
    ├── logo.png                  # Logo de la app
    └── icons/                    # Iconos SVG (nails, calendar, etc.)
```

### Navegación:

```
Dashboard → Calendario → Clientas → Servicios → Fidelización
```

---

## Timeline Estimado para Frontend

| Módulo | Tiempo Estimado | Estado |
|---|---|---|
| Setup React + Tailwind CSS | 1 hora | ⏳ Pendiente |
| Dashboard UI (overview) | 2 horas | ⏳ Pendiente |
| Calendario UI interactivo | 3 horas | ⏳ Pendiente |
| Clientas UI (list + form) | 2.5 horas | ⏳ Pendiente |
| Servicios UI (list + CRUD) | 1.5 horas | ⏳ Pendiente |
| Fidelización UI (badges + progress) | 2 horas | ⏳ Pendiente |
| API integration + CSRF/XSS protection | 3 horas | ⏳ Pendiente |
| Testing y ajustes | 1 hora | ⏳ Pendiente |

**Total estimado: ~16 horas**

---

## Referencias en Vault

- [[Tendencias-Apps-Manicurista]] - Tendencias que inspiran el diseño UI
- [[Sistemas-Fidelizacion]] - Sistema de descuentos y fidelización (UI visual)
- [[Arquitectura-App]] - Estructura general del proyecto
- [[Backend-FastAPI]] - Backend completo (Models, Schemas, Routers)
- [[Base-Datos-PostgreSQL]] - Schema SQL, migrations, queries

---

## Decisiones Pendientes para Aprobación

1. ✅ **Framework**: Vue.js + Tailwind CSS - APROBADO por usuario
2. ✅ **Estilo visual**: Minimalista moderno (Mangomint style) - APROBADO por usuario
3. ✅ **Mobile-first**: Desktop-first primero - APROBADO por usuario
4. ✅ **Autenticación**: JWT con localStorage tokens - APROBADO por usuario

---

## Stack Final Aprobado para Frontend

```
Frontend Stack (Aprobado):
├── Vue.js 3+ (progressive framework, single-file components)
├── Tailwind CSS (utility-first styling)
├── Vue Router (navegación SPA)
├── Axios (HTTP client para API calls)
├── DOMPurify (XSS protection - sanitización HTML)
└── js-cookie (CSRF token management)

Estilo Visual: Minimalista moderno (Mangomint style)
- Fondos blancos con acentos sutiles
- Tipografía limpia y legible
- Interfaz intuitiva sin sobrecarga visual
- Cards con sombras suaves

Prioridad: Desktop-first primero
- Diseño optimizado para desktop/tablet
- Responsive para mobile después

Autenticación: JWT con localStorage tokens
- Token almacenado en localStorage (como aprobó el usuario)
- CORS restriction en backend para proteger API
- Pydantic validation para sanitización de input
