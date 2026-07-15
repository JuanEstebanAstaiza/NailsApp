import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch
from datetime import date, timedelta

from main import app
from database import get_db
from models.client import Client
from models.service import Service
from models.appointment import Appointment
from schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentResponse

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
    test_db.query(Appointment).delete()
    test_db.query(Service).delete()
    test_db.query(Client).delete()
    test_db.commit()
    return test_db


appointment_test_client = TestClient(app)


class TestAppointmentsCRUD:
    """Test CRUD operations for appointments"""

    def test_create_appointment(self, clean_db):
        """Test creating a new appointment"""
        # Create client and service first
        client_resp = appointment_test_client.post("/api/clients/", json={
            "name": "María García",
            "phone": "+57 300 1234567"
        })
        client_id = client_resp.json()["id"]

        service_resp = appointment_test_client.post("/api/services/", json={
            "name": "Manicure Clásico",
            "duration": 30,
            "price": 25.00
        })
        service_id = service_resp.json()["id"]

        response = appointment_test_client.post("/api/appointments/", json={
            "client_id": client_id,
            "service_id": service_id,
            "date": date.today().isoformat(),
            "time": "10:00"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert str(data["client_id"]) == client_id
        assert str(data["service_id"]) == service_id
        assert float(data["price"]) == 25.00
        assert float(data["discount_applied"]) == 0
        assert float(data["final_price"]) == 25.00

    def test_create_appointment_with_loyalty_discount(self, clean_db):
        """Test creating appointment with loyalty discount applied"""
        # Create client and service first
        client_resp = appointment_test_client.post("/api/clients/", json={
            "name": "María García",
            "phone": "+57 300 1234567"
        })
        client_id = client_resp.json()["id"]

        service_resp = appointment_test_client.post("/api/services/", json={
            "name": "Manicure Clásico",
            "duration": 30,
            "price": 25.00
        })
        service_id = service_resp.json()["id"]

        # Create loyalty rule: punch-card with 8 appointments for 15% discount
        appointment_test_client.post("/api/loyalty/rules/", json={
            "client_id": client_id,
            "type": "punch-card",
            "trigger_count": 8,
            "reward_type": "discount",
            "reward_value": 15.0
        })

        # Create 8 completed appointments to reach threshold
        for i in range(8):
            appt_resp = appointment_test_client.post("/api/appointments/", json={
                "client_id": client_id,
                "service_id": service_id,
                "date": (date.today() - timedelta(days=14-i)).isoformat(),
                "time": "09:00"
            })
            appointment_test_client.put(f"/api/appointments/{appt_resp.json()['id']}/complete")

        # Create 9th appointment - should get discount since 8 are completed
        response = appointment_test_client.post("/api/appointments/", json={
            "client_id": client_id,
            "service_id": service_id,
            "date": date.today().isoformat(),
            "time": "10:00"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert float(data["discount_applied"]) == 15.0
        expected_final_price = 25.00 * (1 - 0.15)
        assert abs(float(data["final_price"]) - expected_final_price) < 0.01

    def test_create_appointment_time_conflict(self, clean_db):
        """Test creating appointment with time conflict"""
        # Create client and service first
        client_resp = appointment_test_client.post("/api/clients/", json={
            "name": "María García"
        })
        client_id = client_resp.json()["id"]

        service_resp = appointment_test_client.post("/api/services/", json={
            "name": "Manicure Clásico",
            "duration": 30,
            "price": 25.00
        })
        service_id = service_resp.json()["id"]

        # Create first appointment
        appointment_test_client.post("/api/appointments/", json={
            "client_id": client_id,
            "service_id": service_id,
            "date": date.today().isoformat(),
            "time": "10:00"
        })

        # Try to create conflicting appointment
        response = appointment_test_client.post("/api/appointments/", json={
            "client_id": client_id,
            "service_id": service_id,
            "date": date.today().isoformat(),
            "time": "10:00"
        })
        
        assert response.status_code == 409

    def test_list_appointments(self, clean_db):
        """Test listing all appointments"""
        # Create client and service first
        client_resp = appointment_test_client.post("/api/clients/", json={
            "name": "María García"
        })
        client_id = client_resp.json()["id"]

        service_resp = appointment_test_client.post("/api/services/", json={
            "name": "Manicure Clásico",
            "duration": 30,
            "price": 25.00
        })
        service_id = service_resp.json()["id"]

        # Create appointments
        for i in range(3):
            appointment_test_client.post("/api/appointments/", json={
                "client_id": client_id,
                "service_id": service_id,
                "date": date.today().isoformat(),
                "time": f"{10+i}:00"
            })

        response = appointment_test_client.get("/api/appointments/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_list_appointments_with_date_filter(self, clean_db):
        """Test listing appointments with date filter"""
        # Create client and service first
        client_resp = appointment_test_client.post("/api/clients/", json={
            "name": "María García"
        })
        client_id = client_resp.json()["id"]

        service_resp = appointment_test_client.post("/api/services/", json={
            "name": "Manicure Clásico",
            "duration": 30,
            "price": 25.00
        })
        service_id = service_resp.json()["id"]

        # Create appointments on different dates
        appointment_test_client.post("/api/appointments/", json={
            "client_id": client_id,
            "service_id": service_id,
            "date": date.today().isoformat(),
            "time": "10:00"
        })
        tomorrow = date.today() + timedelta(days=1)
        appointment_test_client.post("/api/appointments/", json={
            "client_id": client_id,
            "service_id": service_id,
            "date": tomorrow.isoformat(),
            "time": "10:00"
        })

        response = appointment_test_client.get(f"/api/appointments/?date_filter={date.today().isoformat()}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_get_appointment(self, clean_db):
        """Test getting a specific appointment by ID"""
        # Create client and service first
        client_resp = appointment_test_client.post("/api/clients/", json={
            "name": "María García"
        })
        client_id = client_resp.json()["id"]

        service_resp = appointment_test_client.post("/api/services/", json={
            "name": "Manicure Clásico",
            "duration": 30,
            "price": 25.00
        })
        service_id = service_resp.json()["id"]

        appt_resp = appointment_test_client.post("/api/appointments/", json={
            "client_id": client_id,
            "service_id": service_id,
            "date": date.today().isoformat(),
            "time": "10:00"
        })
        
        appt_id = appt_resp.json()["id"]

        response = appointment_test_client.get(f"/api/appointments/{appt_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert str(data["client_id"]) == client_id

    def test_get_appointment_not_found(self, clean_db):
        """Test getting a non-existent appointment"""
        import uuid
        fake_id = str(uuid.uuid4())

        response = appointment_test_client.get(f"/api/appointments/{fake_id}")
        
        assert response.status_code == 404

    def test_update_appointment(self, clean_db):
        """Test updating an appointment"""
        # Create client and service first
        client_resp = appointment_test_client.post("/api/clients/", json={
            "name": "María García"
        })
        client_id = client_resp.json()["id"]

        service_resp = appointment_test_client.post("/api/services/", json={
            "name": "Manicure Clásico",
            "duration": 30,
            "price": 25.00
        })
        service_id = service_resp.json()["id"]

        appt_resp = appointment_test_client.post("/api/appointments/", json={
            "client_id": client_id,
            "service_id": service_id,
            "date": date.today().isoformat(),
            "time": "10:00"
        })
        
        appt_id = appt_resp.json()["id"]

        tomorrow = date.today() + timedelta(days=1)
        response = appointment_test_client.put(f"/api/appointments/{appt_id}", json={
            "date": tomorrow.isoformat(),
            "time": "14:00"
        })
        
        # Debug: print error details if 422
        if response.status_code == 422:
            import pprint
            pprint.pprint(response.json())
        
        assert response.status_code == 200, f"Update failed with status {response.status_code}: {response.json()}"
        data = response.json()
        assert str(data["client_id"]) == client_id

    def test_complete_appointment(self, clean_db):
        """Test completing an appointment and incrementing loyalty count"""
        # Create client and service first
        client_resp = appointment_test_client.post("/api/clients/", json={
            "name": "María García"
        })
        client_id = client_resp.json()["id"]

        service_resp = appointment_test_client.post("/api/services/", json={
            "name": "Manicure Clásico",
            "duration": 30,
            "price": 25.00
        })
        service_id = service_resp.json()["id"]

        appt_resp = appointment_test_client.post("/api/appointments/", json={
            "client_id": client_id,
            "service_id": service_id,
            "date": date.today().isoformat(),
            "time": "10:00"
        })
        
        appt_id = appt_resp.json()["id"]

        # Complete the appointment
        response = appointment_test_client.put(f"/api/appointments/{appt_id}/complete")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"

    def test_cancel_appointment(self, clean_db):
        """Test cancelling an appointment"""
        # Create client and service first
        client_resp = appointment_test_client.post("/api/clients/", json={
            "name": "María García"
        })
        client_id = client_resp.json()["id"]

        service_resp = appointment_test_client.post("/api/services/", json={
            "name": "Manicure Clásico",
            "duration": 30,
            "price": 25.00
        })
        service_id = service_resp.json()["id"]

        appt_resp = appointment_test_client.post("/api/appointments/", json={
            "client_id": client_id,
            "service_id": service_id,
            "date": date.today().isoformat(),
            "time": "10:00"
        })
        
        appt_id = appt_resp.json()["id"]

        response = appointment_test_client.delete(f"/api/appointments/{appt_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Cita cancelada"

    def test_list_appointments_with_status_filter(self, clean_db):
        """Test listing appointments with status filter"""
        # Create client and service first
        client_resp = appointment_test_client.post("/api/clients/", json={
            "name": "María García"
        })
        client_id = client_resp.json()["id"]

        service_resp = appointment_test_client.post("/api/services/", json={
            "name": "Manicure Clásico",
            "duration": 30,
            "price": 25.00
        })
        service_id = service_resp.json()["id"]

        # Create appointments with different statuses
        appt1 = appointment_test_client.post("/api/appointments/", json={
            "client_id": client_id,
            "service_id": service_id,
            "date": date.today().isoformat(),
            "time": "10:00"
        })
        appt2 = appointment_test_client.post("/api/appointments/", json={
            "client_id": client_id,
            "service_id": service_id,
            "date": date.today().isoformat(),
            "time": "11:00"
        })

        # Cancel one appointment
        appointment_test_client.delete(f"/api/appointments/{appt2.json()['id']}")

        response = appointment_test_client.get("/api/appointments/?status=scheduled")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_list_appointments_with_client_filter(self, clean_db):
        """Test listing appointments with client filter"""
        # Create two clients and services first
        client1_resp = appointment_test_client.post("/api/clients/", json={
            "name": "María García"
        })
        client1_id = client1_resp.json()["id"]

        client2_resp = appointment_test_client.post("/api/clients/", json={
            "name": "Ana López"
        })
        client2_id = client2_resp.json()["id"]

        service_resp = appointment_test_client.post("/api/services/", json={
            "name": "Manicure Clásico",
            "duration": 30,
            "price": 25.00
        })
        service_id = service_resp.json()["id"]

        # Create appointments for both clients
        appointment_test_client.post("/api/appointments/", json={
            "client_id": client1_id,
            "service_id": service_id,
            "date": date.today().isoformat(),
            "time": "10:00"
        })
        appointment_test_client.post("/api/appointments/", json={
            "client_id": client2_id,
            "service_id": service_id,
            "date": date.today().isoformat(),
            "time": "11:00"
        })

        response = appointment_test_client.get(f"/api/appointments/?client_id={client1_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1