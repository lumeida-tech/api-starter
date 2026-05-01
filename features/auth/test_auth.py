import pytest
from litestar.testing import TestClient

from app import app

# ── Client ────────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    with TestClient(app=app) as c:
        yield c


# ── Register ──────────────────────────────────────────────────────────────────

def test_register_success(client: TestClient):
    response = client.post("/auth/register", json={
        "email":     "test@example.com",
        "password":  "Password123&",
        "full_name": "Test User",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data


def test_register_duplicate_email(client: TestClient):
    payload = {"email": "dup@example.com", "password": "Password123&", "full_name": "Dup"}
    client.post("/auth/register", json=payload)
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 409


# ── Login ─────────────────────────────────────────────────────────────────────

def test_login_success(client: TestClient):
    client.post("/auth/register", json={
        "email": "login@example.com", "password": "Password123&", "full_name": "Login User",
    })
    response = client.post("/auth/login", json={
        "email": "login@example.com", "password": "Password123&",
    })
    assert response.status_code == 201
    assert "access_token" in client.cookies


def test_login_wrong_password(client: TestClient):
    client.post("/auth/register", json={
        "email": "wrong@example.com", "password": "Password123&", "full_name": "Wrong",
    })
    response = client.post("/auth/login", json={
        "email": "wrong@example.com", "password": "BadPassword",
    })
    assert response.status_code == 401


# ── Me ────────────────────────────────────────────────────────────────────────

def test_me_authenticated(client: TestClient):
    client.post("/auth/register", json={
        "email": "me@example.com", "password": "Password123&", "full_name": "Me User",
    })
    client.post("/auth/login", json={"email": "me@example.com", "password": "Password123&"})
    response = client.get("/auth/me")
    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"


def test_me_unauthenticated(client: TestClient):
    response = client.get("/auth/me")
    assert response.status_code == 401


# ── Logout ────────────────────────────────────────────────────────────────────

def test_logout(client: TestClient):
    client.post("/auth/register", json={
        "email": "logout@example.com", "password": "Password123&", "full_name": "Logout",
    })
    client.post("/auth/login", json={"email": "logout@example.com", "password": "Password123&"})
    response = client.delete("/auth/logout")
    assert response.status_code == 200
    assert "access_token" not in client.cookies


# ── Forgot / Reset password ───────────────────────────────────────────────────

def test_forgot_password_unknown_email(client: TestClient):
    # Doit répondre 200 même si l'email n'existe pas (réponse silencieuse)
    response = client.post("/auth/forgot-password", params={
        "email":         "unknown@example.com",
        "redirected_url": "http://localhost:3000/reset-password",
    })
    assert response.status_code == 201


def test_reset_password_invalid_token(client: TestClient):
    response = client.post("/auth/reset-password", params={"token": "invalid-token"}, json={
        "password":        "NewPassword123&",
        "confirmPassword": "NewPassword123&",
    })
    assert response.status_code == 422
