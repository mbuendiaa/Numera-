from fastapi.testclient import TestClient

from numera.api.routes.purchases import get_purchase_container
from numera.main import app


client = TestClient(app)


def setup_function():
    get_purchase_container().purchase_repository.clear()


def test_purchase_lifecycle_is_available_through_api():
    created = client.post(
        "/purchases/",
        json={
            "purchase_id": "purchase_api_1",
            "supplier_id": "supplier_1",
            "invoice_id": "invoice_1",
            "total_amount": "100.00",
            "currency": "EUR",
        },
    )
    assert created.status_code == 201
    assert created.json()["status"] == "RECEIVED"
    assert created.json()["outstanding_amount"] == "100.00"

    approved = client.post("/purchases/purchase_api_1/approve")
    assert approved.status_code == 200
    assert approved.json()["status"] == "APPROVED"

    partially_paid = client.post(
        "/purchases/purchase_api_1/payments",
        json={"amount": "40.00", "currency": "EUR"},
    )
    assert partially_paid.status_code == 200
    assert partially_paid.json()["status"] == "PARTIALLY_PAID"
    assert partially_paid.json()["outstanding_amount"] == "60.00"

    paid = client.post(
        "/purchases/purchase_api_1/payments",
        json={"amount": "60.00", "currency": "EUR"},
    )
    assert paid.status_code == 200
    assert paid.json()["status"] == "PAID"
    assert paid.json()["outstanding_amount"] == "0.00"

    fetched = client.get("/purchases/purchase_api_1")
    assert fetched.status_code == 200
    assert fetched.json()["status"] == "PAID"

    listed = client.get("/purchases/")
    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_duplicate_purchase_returns_conflict():
    payload = {
        "purchase_id": "duplicate",
        "supplier_id": "supplier_1",
        "invoice_id": "invoice_1",
        "total_amount": "10.00",
        "currency": "EUR",
    }
    assert client.post("/purchases/", json=payload).status_code == 201
    response = client.post("/purchases/", json=payload)
    assert response.status_code == 409


def test_missing_purchase_returns_not_found():
    assert client.get("/purchases/unknown").status_code == 404
    assert client.post("/purchases/unknown/approve").status_code == 404


def test_invalid_transition_returns_conflict():
    client.post(
        "/purchases/",
        json={
            "purchase_id": "not_approved",
            "supplier_id": "supplier_1",
            "invoice_id": "invoice_1",
            "total_amount": "10.00",
            "currency": "EUR",
        },
    )
    response = client.post(
        "/purchases/not_approved/payments",
        json={"amount": "5.00", "currency": "EUR"},
    )
    assert response.status_code == 409


def test_purchases_are_exposed_in_openapi():
    schema = client.get("/openapi.json").json()
    assert "/purchases/" in schema["paths"]
    assert "/purchases/{purchase_id}/approve" in schema["paths"]
    assert "/purchases/{purchase_id}/payments" in schema["paths"]
