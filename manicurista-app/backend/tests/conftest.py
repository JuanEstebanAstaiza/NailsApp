import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import MagicMock, patch
import tempfile
import os

from database import Base, get_db
from models.client import Client
from models.service import Service
from models.appointment import Appointment
from models.loyalty_rule import LoyaltyRule
from schemas.client import ClientCreate, ClientUpdate, ClientResponse
from schemas.service import ServiceCreate, ServiceUpdate, ServiceResponse
from schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentResponse
from schemas.loyalty_rule import LoyaltyRuleCreate, LoyaltyRuleUpdate, LoyaltyRuleResponse

# SQLite file-based for testing (use temp files to avoid conflicts)
_temp_db_files = []


def _get_test_db_url():
    """Get a unique temporary database URL for each test"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    _temp_db_files.append(path)
    return f"sqlite:///{path}"

SQLALCHEMY_DATABASE_URL = _get_test_db_url()

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def test_db():
    """Create and teardown test database for each function"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True, scope="session")
def cleanup_temp_db():
    """Clean up temporary database files after all tests"""
    yield
    import gc
    # Force garbage collection to close any lingering connections
    gc.collect()
    for path in _temp_db_files:
        if os.path.exists(path):
            try:
                os.remove(path)
            except PermissionError:
                pass  # File might still be locked, skip it


@pytest.fixture
def sample_client_data():
    """Sample client data for testing"""
    return ClientCreate(
        name="Client Test Sample",
        phone="+57 300 1234567",
        email="client@example.com"
    )


@pytest.fixture
def sample_service_data():
    """Sample service data for testing"""
    return ServiceCreate(
        name="Manicure Clásico",
        category="manicure",
        duration=30,
        price=25.00,
        color="#FF69B4"
    )


@pytest.fixture
def sample_appointment_data():
    """Sample appointment data for testing"""
    from datetime import date, time
    return AppointmentCreate(
        client_id=None,  # Will be set in test
        service_id=None,  # Will be set in test
        date=date.today(),
        time=time(10, 0),
        notes="Primera cita"
    )


@pytest.fixture
def sample_loyalty_rule_data():
    """Sample loyalty rule data for testing"""
    return LoyaltyRuleCreate(
        client_id=None,  # Will be set in test
        type="punch-card",
        trigger_count=8,
        service_filter=None,
        reward_type="discount",
        reward_value=15.0,
        rebooking_days=None
    )


@pytest.fixture
def sample_loyalty_rule_rebooking_data():
    """Sample loyalty rule data for rebooking type"""
    return LoyaltyRuleCreate(
        client_id=None,  # Will be set in test
        type="rebooking",
        trigger_count=1,
        service_filter=None,
        reward_type="discount",
        reward_value=10.0,
        rebooking_days=7
    )


@pytest.fixture
def mock_db_session():
    """Mock database session for unit tests"""
    db = MagicMock()
    return db