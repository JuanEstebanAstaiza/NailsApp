from .clients import router as clients_router
from .services import router as services_router
from .appointments import router as appointments_router
from .loyalty import router as loyalty_router

__all__ = [
    "clients_router",
    "services_router",
    "appointments_router",
    "loyalty_router",
]