from fastapi import FastAPI
from routers.clients import router as clients_router
from routers.services import router as services_router
from routers.appointments import router as appointments_router
from routers.loyalty import router as loyalty_router
from database import Base, engine

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NailBook API",
    description="API para gestión de citas de manicurista con sistema de fidelización",
    version="1.0.0"
)

# Include routers
app.include_router(clients_router)
app.include_router(services_router)
app.include_router(appointments_router)
app.include_router(loyalty_router)


@app.get("/")
def root():
    return {
        "message": "NailBook API - Gestión de Citas para Manicurista",
        "docs": "/docs"
    }

@app.get("/init")
def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    return {"message": "Database initialized successfully"}
