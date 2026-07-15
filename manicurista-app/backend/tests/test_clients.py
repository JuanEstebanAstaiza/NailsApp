import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch

from main import app
from database import get_db
from models.client import Client
from schemas.client import ClientCreate, ClientUpdate, ClientResponse

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
    test_db.query(Client).delete()
    test_db.commit()
    return test_db


client_test_client = TestClient(app)


class TestClientsCRUD:
    """Test CRUD operations for clients"""

    def test_create_client(self, clean_db):
        """Test creating a new client"""
        response = client_test_client.post("/api/clients/", json={
            "name": "Client Test 1",
            "phone": "+57 300 1234567",
            "email": "client1@example.com"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Client Test 1"
        assert data["phone"] == "+57 300 1234567"
        assert data["email"] == "client1@example.com"
        assert data["appointments_count"] == 0

    def test_create_client_without_optional_fields(self, clean_db):
        """Test creating a client with only required fields"""
        response = client_test_client.post("/api/clients/", json={
            "name": "Client Test 2"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Client Test 2"
        assert data["phone"] is None
        assert data["email"] is None

    def test_list_clients(self, clean_db):
        """Test listing all clients"""
        # Create some clients first
        client_test_client.post("/api/clients/", json={"name": "Client Test 3"})
        client_test_client.post("/api/clients/", json={"name": "Client Test 4"})

        response = client_test_client.get("/api/clients/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_client(self, clean_db):
        """Test getting a specific client by ID"""
        # Create a client first
        create_response = client_test_client.post("/api/clients/", json={
            "name": "Client Test 5",
            "phone": "+57 300 1234567"
        })
        
        client_id = create_response.json()["id"]

        response = client_test_client.get(f"/api/clients/{client_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Client Test 5"
        assert str(data["id"]) == client_id

    def test_get_client_not_found(self, clean_db):
        """Test getting a non-existent client"""
        import uuid
        fake_id = str(uuid.uuid4())

        response = client_test_client.get(f"/api/clients/{fake_id}")
        
        assert response.status_code == 404

    def test_update_client(self, clean_db):
        """Test updating a client"""
        # Create a client first
        create_response = client_test_client.post("/api/clients/", json={
            "name": "Client Test 6",
            "phone": "+57 300 1234567"
        })
        
        client_id = create_response.json()["id"]

        response = client_test_client.put(f"/api/clients/{client_id}", json={
            "name": "Client Test 6 Updated",
            "email": "client6@example.com"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Client Test 6 Updated"
        assert data["phone"] == "+57 300 1234567"  # Unchanged
        assert data["email"] == "client6@example.com"

    def test_update_client_partial(self, clean_db):
        """Test updating only some fields of a client"""
        # Create a client first
        create_response = client_test_client.post("/api/clients/", json={
            "name": "Client Test 7",
            "phone": "+57 300 1234567"
        })
        
        client_id = create_response.json()["id"]

        response = client_test_client.put(f"/api/clients/{client_id}", json={
            "name": "Client Test 7 Updated"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Client Test 7 Updated"
        assert data["phone"] == "+57 300 1234567"  # Unchanged

    def test_delete_client(self, clean_db):
        """Test deleting a client"""
        # Create a client first
        create_response = client_test_client.post("/api/clients/", json={
            "name": "Client Test 8",
            "phone": "+57 300 1234567"
        })
        
        client_id = create_response.json()["id"]

        response = client_test_client.delete(f"/api/clients/{client_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Cliente eliminado"

    def test_delete_client_not_found(self, clean_db):
        """Test deleting a non-existent client"""
        import uuid
        fake_id = str(uuid.uuid4())

        response = client_test_client.delete(f"/api/clients/{fake_id}")
        
        assert response.status_code == 404

    def test_list_clients_with_pagination(self, clean_db):
        """Test listing clients with pagination"""
        # Create multiple clients
        for i in range(5):
            client_test_client.post("/api/clients/", json={"name": f"Pagination Client {i}"})

        response = client_test_client.get("/api/clients/?skip=0&limit=3")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_list_clients_skip_limit(self, clean_db):
        """Test listing clients with skip and limit"""
        # Create multiple clients
        for i in range(5):
            client_test_client.post("/api/clients/", json={"name": f"SkipLimit Client {i}"})

        response = client_test_client.get("/api/clients/?skip=2&limit=3")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3