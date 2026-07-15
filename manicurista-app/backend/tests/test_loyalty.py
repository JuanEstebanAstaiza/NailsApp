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
from models.loyalty_rule import LoyaltyRule
from schemas.loyalty_rule import LoyaltyRuleCreate, LoyaltyRuleUpdate, LoyaltyRuleResponse

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
    test_db.query(LoyaltyRule).delete()
    test_db.query(Appointment).delete()
    test_db.query(Service).delete()
    test_db.query(Client).delete()
    test_db.commit()
    return test_db


loyalty_test_client = TestClient(app)


class TestLoyaltyRulesCRUD:
    """Test CRUD operations for loyalty rules"""

    def test_create_loyalty_rule(self, clean_db):
        """Test creating a new loyalty rule"""
        # Create client and service first
        client_resp = loyalty_test_client.post("/api/clients/", json={
            "name": "Loyalty Client 1"
        })
        client_id = client_resp.json()["id"]

        service_resp = loyalty_test_client.post("/api/services/", json={
            "name": "Manicure Clásico",
            "duration": 30,
            "price": 25.00
        })
        service_id = service_resp.json()["id"]

        response = loyalty_test_client.post("/api/loyalty/rules/", json={
            "client_id": client_id,
            "type": "punch-card",
            "trigger_count": 8,
            "service_filter": service_id,
            "reward_type": "discount",
            "reward_value": 15.0
        })
        
        assert response.status_code == 200
        data = response.json()
        assert str(data["client_id"]) == client_id
        assert data["type"] == "punch-card"
        assert data["trigger_count"] == 8
        assert float(data["reward_value"]) == 15.0

    def test_create_global_loyalty_rule(self, clean_db):
        """Test creating a global loyalty rule (no client_id)"""
        response = loyalty_test_client.post("/api/loyalty/rules/", json={
            "type": "punch-card",
            "trigger_count": 10,
            "reward_type": "discount",
            "reward_value": 20.0
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["client_id"] is None

    def test_list_loyalty_rules(self, clean_db):
        """Test listing all loyalty rules"""
        # Create client first
        client_resp = loyalty_test_client.post("/api/clients/", json={
            "name": "Loyalty Client 2"
        })
        client_id = client_resp.json()["id"]

        loyalty_test_client.post("/api/loyalty/rules/", json={
            "client_id": client_id,
            "type": "punch-card",
            "trigger_count": 8,
            "reward_type": "discount",
            "reward_value": 15.0
        })

        response = loyalty_test_client.get("/api/loyalty/rules/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_get_loyalty_rule(self, clean_db):
        """Test getting a specific loyalty rule by ID"""
        # Create client first
        client_resp = loyalty_test_client.post("/api/clients/", json={
            "name": "Loyalty Client 3"
        })
        client_id = client_resp.json()["id"]

        rule_resp = loyalty_test_client.post("/api/loyalty/rules/", json={
            "client_id": client_id,
            "type": "punch-card",
            "trigger_count": 8,
            "reward_type": "discount",
            "reward_value": 15.0
        })
        
        rule_id = rule_resp.json()["id"]

        response = loyalty_test_client.get(f"/api/loyalty/rules/{rule_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert str(data["client_id"]) == client_id

    def test_get_loyalty_rule_not_found(self, clean_db):
        """Test getting a non-existent loyalty rule"""
        import uuid
        fake_id = str(uuid.uuid4())

        response = loyalty_test_client.get(f"/api/loyalty/rules/{fake_id}")
        
        assert response.status_code == 404

    def test_update_loyalty_rule(self, clean_db):
        """Test updating a loyalty rule"""
        # Create client first
        client_resp = loyalty_test_client.post("/api/clients/", json={
            "name": "Loyalty Client 4"
        })
        client_id = client_resp.json()["id"]

        rule_resp = loyalty_test_client.post("/api/loyalty/rules/", json={
            "client_id": client_id,
            "type": "punch-card",
            "trigger_count": 8,
            "reward_type": "discount",
            "reward_value": 15.0
        })
        
        rule_id = rule_resp.json()["id"]

        response = loyalty_test_client.put(f"/api/loyalty/rules/{rule_id}", json={
            "trigger_count": 12,
            "reward_value": 20.0
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["trigger_count"] == 12
        assert float(data["reward_value"]) == 20.0

    def test_delete_loyalty_rule(self, clean_db):
        """Test deleting a loyalty rule"""
        # Create client first
        client_resp = loyalty_test_client.post("/api/clients/", json={
            "name": "Loyalty Client 5"
        })
        client_id = client_resp.json()["id"]

        rule_resp = loyalty_test_client.post("/api/loyalty/rules/", json={
            "client_id": client_id,
            "type": "punch-card",
            "trigger_count": 8,
            "reward_type": "discount",
            "reward_value": 15.0
        })
        
        rule_id = rule_resp.json()["id"]

        response = loyalty_test_client.delete(f"/api/loyalty/rules/{rule_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Regla eliminada"

    def test_delete_loyalty_rule_not_found(self, clean_db):
        """Test deleting a non-existent loyalty rule"""
        import uuid
        fake_id = str(uuid.uuid4())

        response = loyalty_test_client.delete(f"/api/loyalty/rules/{fake_id}")
        
        assert response.status_code == 404


class TestLoyaltyStatus:
    """Test loyalty status endpoint"""

    def test_loyalty_status_no_rules(self, clean_db):
        """Test loyalty status when no rules exist"""
        # Create client first
        client_resp = loyalty_test_client.post("/api/clients/", json={
            "name": "Loyalty Client 6"
        })
        client_id = client_resp.json()["id"]

        response = loyalty_test_client.get(f"/api/loyalty/status/{client_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert str(data["client_id"]) == client_id
        assert len(data["rules_status"]) == 0

    def test_loyalty_status_punch_card_not_qualified(self, clean_db):
        """Test loyalty status when punch-card rule not yet qualified"""
        # Create client and service first
        client_resp = loyalty_test_client.post("/api/clients/", json={
            "name": "Loyalty Client 7"
        })
        client_id = client_resp.json()["id"]

        service_resp = loyalty_test_client.post("/api/services/", json={
            "name": "Manicure Clásico",
            "duration": 30,
            "price": 25.00
        })
        service_id = service_resp.json()["id"]

        # Create punch-card rule: 8 appointments for 15% discount
        loyalty_test_client.post("/api/loyalty/rules/", json={
            "client_id": client_id,
            "type": "punch-card",
            "trigger_count": 8,
            "reward_type": "discount",
            "reward_value": 15.0
        })

        # Create only 3 completed appointments
        for i in range(3):
            appt_resp = loyalty_test_client.post("/api/appointments/", json={
                "client_id": client_id,
                "service_id": service_id,
                "date": (date.today() - timedelta(days=7-i)).isoformat(),
                "time": "09:00"
            })
            loyalty_test_client.put(f"/api/appointments/{appt_resp.json()['id']}/complete")

        response = loyalty_test_client.get(f"/api/loyalty/status/{client_id}")
        
        assert response.status_code == 200
        data = response.json()
        punch_card_status = [s for s in data["rules_status"] if s["rule_type"] == "punch-card"][0]
        assert punch_card_status["current_count"] == 3
        assert punch_card_status["trigger_count"] == 8
        assert not punch_card_status["qualified"]

    def test_loyalty_status_punch_card_qualified(self, clean_db):
        """Test loyalty status when punch-card rule is qualified"""
        # Create client and service first
        client_resp = loyalty_test_client.post("/api/clients/", json={
            "name": "Loyalty Client 8"
        })
        client_id = client_resp.json()["id"]

        service_resp = loyalty_test_client.post("/api/services/", json={
            "name": "Manicure Clásico",
            "duration": 30,
            "price": 25.00
        })
        service_id = service_resp.json()["id"]

        # Create punch-card rule: 8 appointments for 15% discount
        loyalty_test_client.post("/api/loyalty/rules/", json={
            "client_id": client_id,
            "type": "punch-card",
            "trigger_count": 8,
            "reward_type": "discount",
            "reward_value": 15.0
        })

        # Create 8 completed appointments
        for i in range(8):
            appt_resp = loyalty_test_client.post("/api/appointments/", json={
                "client_id": client_id,
                "service_id": service_id,
                "date": (date.today() - timedelta(days=14-i)).isoformat(),
                "time": "09:00"
            })
            loyalty_test_client.put(f"/api/appointments/{appt_resp.json()['id']}/complete")

        response = loyalty_test_client.get(f"/api/loyalty/status/{client_id}")
        
        assert response.status_code == 200
        data = response.json()
        punch_card_status = [s for s in data["rules_status"] if s["rule_type"] == "punch-card"][0]
        assert punch_card_status["current_count"] == 8
        assert punch_card_status["trigger_count"] == 8
        assert punch_card_status["qualified"]

    def test_loyalty_status_punch_card_service_filter(self, clean_db):
        """Test loyalty status with service-filtered punch-card rule"""
        # Create client and services first
        client_resp = loyalty_test_client.post("/api/clients/", json={
            "name": "Loyalty Client 9"
        })
        client_id = client_resp.json()["id"]

        manicure_resp = loyalty_test_client.post("/api/services/", json={
            "name": "Manicure Clásico",
            "duration": 30,
            "price": 25.00
        })
        manicure_id = manicure_resp.json()["id"]

        pedicure_resp = loyalty_test_client.post("/api/services/", json={
            "name": "Pedicure Básico",
            "duration": 45,
            "price": 30.00
        })
        pedicure_id = pedicure_resp.json()["id"]

        # Create punch-card rule: only for manicure - 8 appointments for 15% discount
        loyalty_test_client.post("/api/loyalty/rules/", json={
            "client_id": client_id,
            "type": "punch-card",
            "trigger_count": 8,
            "service_filter": manicure_id,
            "reward_type": "discount",
            "reward_value": 15.0
        })

        # Create 3 manicure appointments and 2 pedicure appointments
        for i in range(3):
            appt_resp = loyalty_test_client.post("/api/appointments/", json={
                "client_id": client_id,
                "service_id": manicure_id,
                "date": (date.today() - timedelta(days=7-i)).isoformat(),
                "time": "09:00"
            })
            loyalty_test_client.put(f"/api/appointments/{appt_resp.json()['id']}/complete")

        for i in range(2):
            appt_resp = loyalty_test_client.post("/api/appointments/", json={
                "client_id": client_id,
                "service_id": pedicure_id,
                "date": (date.today() - timedelta(days=5-i)).isoformat(),
                "time": "10:00"
            })
            loyalty_test_client.put(f"/api/appointments/{appt_resp.json()['id']}/complete")

        response = loyalty_test_client.get(f"/api/loyalty/status/{client_id}")
        
        assert response.status_code == 200
        data = response.json()
        punch_card_status = [s for s in data["rules_status"] if s["rule_type"] == "punch-card"][0]
        assert punch_card_status["current_count"] == 3  # Only manicure appointments count
        assert punch_card_status["service_filter_name"] == "Manicure Clásico"

    def test_loyalty_status_rebooking_eligible(self, clean_db):
        """Test loyalty status when rebooking rule is eligible"""
        # Create client and service first
        client_resp = loyalty_test_client.post("/api/clients/", json={
            "name": "Loyalty Client 10"
        })
        client_id = client_resp.json()["id"]

        service_resp = loyalty_test_client.post("/api/services/", json={
            "name": "Manicure Clásico",
            "duration": 30,
            "price": 25.00
        })
        service_id = service_resp.json()["id"]

        # Create rebooking rule: within 7 days for 10% discount
        loyalty_test_client.post("/api/loyalty/rules/", json={
            "client_id": client_id,
            "type": "rebooking",
            "trigger_count": 1,
            "reward_type": "discount",
            "reward_value": 10.0,
            "rebooking_days": 7
        })

        # Create appointment yesterday (within rebooking window)
        appt_resp = loyalty_test_client.post("/api/appointments/", json={
            "client_id": client_id,
            "service_id": service_id,
            "date": (date.today() - timedelta(days=1)).isoformat(),
            "time": "09:00"
        })
        loyalty_test_client.put(f"/api/appointments/{appt_resp.json()['id']}/complete")

        response = loyalty_test_client.get(f"/api/loyalty/status/{client_id}")
        
        assert response.status_code == 200
        data = response.json()
        rebooking_status = [s for s in data["rules_status"] if s["rule_type"] == "rebooking"][0]
        assert rebooking_status["days_since_last"] == 1
        assert rebooking_status["eligible"]

    def test_loyalty_status_rebooking_not_eligible(self, clean_db):
        """Test loyalty status when rebooking rule is not eligible"""
        # Create client and service first
        client_resp = loyalty_test_client.post("/api/clients/", json={
            "name": "Loyalty Client 11"
        })
        client_id = client_resp.json()["id"]

        service_resp = loyalty_test_client.post("/api/services/", json={
            "name": "Manicure Clásico",
            "duration": 30,
            "price": 25.00
        })
        service_id = service_resp.json()["id"]

        # Create rebooking rule: within 7 days for 10% discount
        loyalty_test_client.post("/api/loyalty/rules/", json={
            "client_id": client_id,
            "type": "rebooking",
            "trigger_count": 1,
            "reward_type": "discount",
            "reward_value": 10.0,
            "rebooking_days": 7
        })

        # Create appointment 30 days ago (outside rebooking window)
        appt_resp = loyalty_test_client.post("/api/appointments/", json={
            "client_id": client_id,
            "service_id": service_id,
            "date": (date.today() - timedelta(days=30)).isoformat(),
            "time": "09:00"
        })
        loyalty_test_client.put(f"/api/appointments/{appt_resp.json()['id']}/complete")

        response = loyalty_test_client.get(f"/api/loyalty/status/{client_id}")
        
        assert response.status_code == 200
        data = response.json()
        rebooking_status = [s for s in data["rules_status"] if s["rule_type"] == "rebooking"][0]
        assert rebooking_status["days_since_last"] == 30
        assert not rebooking_status["eligible"]

    def test_loyalty_status_multiple_rules(self, clean_db):
        """Test loyalty status with multiple rules"""
        # Create client and service first
        client_resp = loyalty_test_client.post("/api/clients/", json={
            "name": "Loyalty Client 12"
        })
        client_id = client_resp.json()["id"]

        service_resp = loyalty_test_client.post("/api/services/", json={
            "name": "Manicure Clásico",
            "duration": 30,
            "price": 25.00
        })
        service_id = service_resp.json()["id"]

        # Create punch-card rule: 8 appointments for 15% discount
        loyalty_test_client.post("/api/loyalty/rules/", json={
            "client_id": client_id,
            "type": "punch-card",
            "trigger_count": 8,
            "reward_type": "discount",
            "reward_value": 15.0
        })

        # Create rebooking rule: within 7 days for 10% discount
        loyalty_test_client.post("/api/loyalty/rules/", json={
            "client_id": client_id,
            "type": "rebooking",
            "trigger_count": 1,
            "reward_type": "discount",
            "reward_value": 10.0,
            "rebooking_days": 7
        })

        # Create appointment yesterday (within rebooking window)
        appt_resp = loyalty_test_client.post("/api/appointments/", json={
            "client_id": client_id,
            "service_id": service_id,
            "date": (date.today() - timedelta(days=1)).isoformat(),
            "time": "09:00"
        })
        loyalty_test_client.put(f"/api/appointments/{appt_resp.json()['id']}/complete")

        response = loyalty_test_client.get(f"/api/loyalty/status/{client_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["rules_status"]) == 2