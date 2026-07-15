import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch

from main import app
from database import get_db
from models.service import Service
from schemas.service import ServiceCreate, ServiceUpdate, ServiceResponse

# Override the dependency for testing
def override_get_db():
    from tests.conftest import TestingSessionLocal
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def clean_db(test_db):
    """Clean database before each test"""
    # Delete all data in correct order (respecting foreign keys)
    test_db.query(Service).delete()
    test_db.commit()
    return test_db


service_test_client = TestClient(app)


class TestServicesCRUD:
    """Test CRUD operations for services"""

    def test_create_service(self, clean_db):
        """Test creating a new service"""
        response = service_test_client.post("/api/services/", json={
            "name": "Manicure Clásico",
            "category": "manicure",
            "duration": 30,
            "price": 25.00,
            "color": "#FF69B4"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Manicure Clásico"
        assert data["category"] == "manicure"
        assert data["duration"] == 30
        assert float(data["price"]) == 25.00

    def test_create_service_without_optional_fields(self, clean_db):
        """Test creating a service with only required fields"""
        response = service_test_client.post("/api/services/", json={
            "name": "Pedicure Básico",
            "duration": 45,
            "price": 30.00
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Pedicure Básico"
        assert data["category"] is None
        assert data["color"] == "#FF69B4"  # Default color

    def test_list_services(self, clean_db):
        """Test listing all services"""
        service_test_client.post("/api/services/", json={
            "name": "Manicure Clásico",
            "duration": 30,
            "price": 25.00
        })
        service_test_client.post("/api/services/", json={
            "name": "Pedicure Básico",
            "duration": 45,
            "price": 30.00
        })

        response = service_test_client.get("/api/services/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_service(self, clean_db):
        """Test getting a specific service by ID"""
        create_response = service_test_client.post("/api/services/", json={
            "name": "Manicure Clásico",
            "duration": 30,
            "price": 25.00
        })
        
        service_id = create_response.json()["id"]

        response = service_test_client.get(f"/api/services/{service_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Manicure Clásico"
        assert str(data["id"]) == service_id

    def test_get_service_not_found(self, clean_db):
        """Test getting a non-existent service"""
        import uuid
        fake_id = str(uuid.uuid4())

        response = service_test_client.get(f"/api/services/{fake_id}")
        
        assert response.status_code == 404

    def test_update_service(self, clean_db):
        """Test updating a service"""
        create_response = service_test_client.post("/api/services/", json={
            "name": "Manicure Clásico",
            "duration": 30,
            "price": 25.00
        })
        
        service_id = create_response.json()["id"]

        response = service_test_client.put(f"/api/services/{service_id}", json={
            "name": "Manicure Premium",
            "price": 35.00
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Manicure Premium"
        assert float(data["price"]) == 35.00
        assert data["duration"] == 30  # Unchanged

    def test_delete_service(self, clean_db):
        """Test deleting a service"""
        create_response = service_test_client.post("/api/services/", json={
            "name": "Manicure Clásico",
            "duration": 30,
            "price": 25.00
        })
        
        service_id = create_response.json()["id"]

        response = service_test_client.delete(f"/api/services/{service_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Servicio eliminado"

    def test_delete_service_not_found(self, clean_db):
        """Test deleting a non-existent service"""
        import uuid
        fake_id = str(uuid.uuid4())

        response = service_test_client.delete(f"/api/services/{fake_id}")
        
        assert response.status_code == 404

    def test_list_services_with_pagination(self, clean_db):
        """Test listing services with pagination"""
        for i in range(5):
            service_test_client.post("/api/services/", json={
                "name": f"Service {i}",
                "duration": 30,
                "price": 25.00
            })

        response = service_test_client.get("/api/services/?skip=0&limit=3")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3