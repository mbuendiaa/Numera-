from fastapi.testclient import TestClient
from sqlalchemy import delete

from numera.infrastructure.database.session import SessionLocal, create_database
from numera.infrastructure.persistence.models import (
    AuditLogORM,
    AuthTokenORM,
    CompanyMembershipORM,
    UserORM,
)
from numera.main import app

client = TestClient(app)


def setup_function():
    create_database()
    with SessionLocal() as db:
        db.execute(delete(AuditLogORM))
        db.execute(delete(AuthTokenORM))
        db.execute(delete(CompanyMembershipORM))
        db.execute(delete(UserORM))
        db.commit()


def register_and_login(email: str):
    response = client.post("/auth/register", json={
        "email": email, "password": "StrongPass123!", "name": email.split("@")[0]
    })
    assert response.status_code == 201
    tokens = client.post("/auth/login", data={
        "username": email, "password": "StrongPass123!"
    }).json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def test_company_memberships_activation_roles_and_audit():
    owner_headers = register_and_login("owner@tenant.test")
    member_headers = register_and_login("member@tenant.test")

    created = client.post("/companies/", headers=owner_headers, json={
        "name": "Tenant One", "country": "ES", "currency": "EUR"
    })
    assert created.status_code == 201
    company_id = created.json()["id"]

    mine = client.get("/companies/my", headers=owner_headers)
    assert mine.status_code == 200
    assert mine.json()[0]["role"] == "owner"
    assert mine.json()[0]["selected"] is True

    added = client.post(f"/companies/{company_id}/members", headers=owner_headers, json={
        "email": "member@tenant.test", "role": "accountant"
    })
    assert added.status_code == 201
    assert added.json()["role"] == "accountant"

    activated = client.post(f"/companies/{company_id}/activate", headers=member_headers)
    assert activated.status_code == 200
    assert activated.json()["role"] == "accountant"

    listed = client.get(f"/companies/{company_id}/members", headers=member_headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 2

    forbidden = client.post(f"/companies/{company_id}/members", headers=member_headers, json={
        "email": "nobody@test.local", "role": "readonly"
    })
    assert forbidden.status_code == 403

    audit = client.get(f"/companies/{company_id}/audit", headers=member_headers)
    assert audit.status_code == 200
    assert {row["action"] for row in audit.json()} >= {"company.created", "member.added", "company.activated"}


def test_tenancy_endpoints_are_in_openapi():
    schema = client.get("/openapi.json").json()
    assert "/companies/my" in schema["paths"]
    assert "/companies/{company_id}/activate" in schema["paths"]
    assert "/companies/{company_id}/members" in schema["paths"]
    assert "/companies/{company_id}/audit" in schema["paths"]
