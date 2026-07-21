from fastapi.testclient import TestClient

from numera.main import app

client = TestClient(app)


def test_cognitive_decision_low_risk():
    response = client.post(
        "/cognitive/decision",
        json={
            "company_id": "company_demo_001",
            "input_type": "invoice",
            "description": "Supplier invoice received",
            "risk_level": "low",
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "recommendation_ready"


def test_cognitive_decision_high_risk():
    response = client.post(
        "/cognitive/decision",
        json={
            "company_id": "company_demo_001",
            "input_type": "payment",
            "description": "Execute supplier payment",
            "risk_level": "high",
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "requires_human_review"
