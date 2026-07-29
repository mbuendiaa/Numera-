from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import delete

from numera.infrastructure.database.session import SessionLocal, create_database
from numera.infrastructure.persistence.models import AuthTokenORM, UserORM
from numera.main import app

client = TestClient(app)


def setup_function():
    create_database()
    with SessionLocal() as db:
        db.execute(delete(AuthTokenORM))
        db.execute(delete(UserORM))
        db.commit()


def register_user(email="owner@numera.test"):
    return client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "StrongPass123!",
            "name": "Numera Owner",
        },
    )


def login_user(email="owner@numera.test"):
    return client.post(
        "/auth/login",
        json={"email": email, "password": "StrongPass123!"},
    )


def test_register_login_me_refresh_and_logout():
    registered = register_user()
    assert registered.status_code == 201
    assert registered.json()["email"] == "owner@numera.test"
    assert "password_hash" not in registered.json()

    duplicate = register_user()
    assert duplicate.status_code == 409

    logged_in = login_user()
    assert logged_in.status_code == 200
    tokens = logged_in.json()
    assert tokens["token_type"] == "bearer"
    assert tokens["access_token"]
    assert tokens["refresh_token"]

    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    me = client.get("/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["role"] == "readonly"

    updated = client.patch("/users/me", headers=headers, json={"name": "Updated Owner"})
    assert updated.status_code == 200
    assert updated.json()["name"] == "Updated Owner"

    refreshed = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refreshed.status_code == 200
    new_tokens = refreshed.json()

    reused = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert reused.status_code == 401

    logout_headers = {"Authorization": f"Bearer {new_tokens['access_token']}"}
    logged_out = client.post(
        "/auth/logout",
        headers=logout_headers,
        json={"refresh_token": new_tokens["refresh_token"]},
    )
    assert logged_out.status_code == 200

    rejected = client.get("/auth/me", headers=logout_headers)
    assert rejected.status_code == 401


def test_bad_password_is_rejected():
    register_user()
    response = client.post(
        "/auth/login",
        json={"email": "owner@numera.test", "password": "wrong-password"},
    )
    assert response.status_code == 401


def test_authentication_is_exposed_in_openapi():
    schema = client.get("/openapi.json").json()
    for path in [
        "/auth/register",
        "/auth/login",
        "/auth/refresh",
        "/auth/logout",
        "/auth/me",
        "/users/me",
    ]:
        assert path in schema["paths"]
    assert "HTTPBearer" in schema["components"]["securitySchemes"]
    login_schema = schema["components"]["schemas"]["LoginRequest"]
    assert set(login_schema["properties"]) == {"email", "password"}
    register_schema = schema["components"]["schemas"]["UserRegister"]
    assert set(register_schema["properties"]) == {"email", "password", "name"}
