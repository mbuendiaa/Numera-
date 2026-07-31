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
    tokens = client.post("/auth/login", json={
        "email": email, "password": "StrongPass123!"
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


def test_register_then_create_company_completes_onboarding():
    headers = register_and_login("new-owner@tenant.test")

    before = client.get("/auth/me", headers=headers)
    assert before.status_code == 200
    assert before.json()["company_id"] is None
    assert before.json()["role"] == "readonly"

    created = client.post("/companies/", headers=headers, json={
        "name": "First Company", "tax_id": "B12345678", "country": "ES", "currency": "EUR"
    })
    assert created.status_code == 201

    after = client.get("/auth/me", headers=headers)
    assert after.status_code == 200
    assert after.json()["company_id"] == created.json()["id"]
    assert after.json()["role"] == "owner"

    mine = client.get("/companies/my", headers=headers)
    assert mine.status_code == 200
    assert mine.json() == [{
        "id": created.json()["id"],
        "name": "First Company",
        "country": "ES",
        "currency": "EUR",
        "role": "owner",
        "is_active": True,
        "selected": True,
    }]


def test_login_restores_company_for_legacy_membership():
    headers = register_and_login("legacy@tenant.test")
    created = client.post("/companies/", headers=headers, json={
        "name": "Legacy Company", "country": "ES", "currency": "EUR"
    })
    assert created.status_code == 201
    company_id = created.json()["id"]

    # Simulate an account created by an older frontend: membership exists but
    # the selected company was not persisted on the user.
    with SessionLocal() as db:
        user = db.query(UserORM).filter(UserORM.email == "legacy@tenant.test").one()
        user.company_id = None
        user.role = "readonly"
        db.commit()

    relogin = client.post("/auth/login", json={
        "email": "legacy@tenant.test", "password": "StrongPass123!"
    })
    assert relogin.status_code == 200
    restored_headers = {"Authorization": f"Bearer {relogin.json()['access_token']}"}
    me = client.get("/auth/me", headers=restored_headers)
    assert me.status_code == 200
    assert me.json()["company_id"] == company_id
    assert me.json()["role"] == "owner"
