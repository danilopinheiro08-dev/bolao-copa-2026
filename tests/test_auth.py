"""
Tests for authentication endpoints: register, login, health, status.
"""
import pytest


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def test_register_new_user(client):
    """POST /api/auth/register → 200, retorna email do usuário."""
    response = client.post(
        "/api/auth/register",
        json={"name": "Maria Silva", "email": "maria@example.com", "password": "Senha1234!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "maria@example.com"
    assert data["name"] == "Maria Silva"
    assert "id" in data
    assert "password_hash" not in data  # nunca expor hash


def test_register_short_name(client):
    """Nome com menos de 2 caracteres deve retornar 422."""
    response = client.post(
        "/api/auth/register",
        json={"name": "A", "email": "a@example.com", "password": "Senha1234!"},
    )
    assert response.status_code == 422


def test_register_short_password(client):
    """Senha com menos de 8 caracteres deve retornar 422."""
    response = client.post(
        "/api/auth/register",
        json={"name": "Ana", "email": "ana@example.com", "password": "123"},
    )
    assert response.status_code == 422


def test_register_invalid_email(client):
    """Email inválido deve retornar 422."""
    response = client.post(
        "/api/auth/register",
        json={"name": "João", "email": "not-an-email", "password": "Senha1234!"},
    )
    assert response.status_code == 422


def test_register_duplicate_email(client):
    """Email já cadastrado deve retornar 400."""
    payload = {"name": "Carlos", "email": "carlos@example.com", "password": "Senha1234!"}
    client.post("/api/auth/register", json=payload)

    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

def test_login_success(client):
    """Login com credenciais corretas → 200 + access_token."""
    client.post(
        "/api/auth/register",
        json={"name": "Pedro", "email": "pedro@example.com", "password": "Senha1234!"},
    )
    response = client.post(
        "/api/auth/login",
        json={"email": "pedro@example.com", "password": "Senha1234!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "user" in data
    assert data["user"]["email"] == "pedro@example.com"


def test_login_wrong_password(client):
    """Senha errada → 401."""
    client.post(
        "/api/auth/register",
        json={"name": "Ana", "email": "ana2@example.com", "password": "Senha1234!"},
    )
    response = client.post(
        "/api/auth/login",
        json={"email": "ana2@example.com", "password": "SenhaErrada!"},
    )
    assert response.status_code == 401


def test_login_unknown_email(client):
    """Email não cadastrado → 401."""
    response = client.post(
        "/api/auth/login",
        json={"email": "naoexiste@example.com", "password": "Qualquer123!"},
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Authenticated routes
# ---------------------------------------------------------------------------

def test_get_current_user_profile(client, test_user, auth_headers):
    """GET /api/users/me → 200, retorna perfil do usuário autenticado."""
    response = client.get("/api/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["name"] == test_user.name


def test_get_profile_without_token(client):
    """GET /api/users/me sem token → 401."""
    response = client.get("/api/users/me")
    assert response.status_code == 401


def test_update_profile(client, test_user, auth_headers):
    """PUT /api/users/me → atualiza nome."""
    response = client.put(
        "/api/users/me",
        headers=auth_headers,
        json={"name": "Nome Atualizado"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Nome Atualizado"


# ---------------------------------------------------------------------------
# System endpoints
# ---------------------------------------------------------------------------

def test_health_check(client):
    """GET /health → 200 com campo 'status'."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data


def test_status_check(client):
    """GET /status → 200 com campo 'service'."""
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "version" in data
    assert "environment" in data
