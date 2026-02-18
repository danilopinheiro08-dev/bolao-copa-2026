"""
Tests for group management endpoints.
"""
import pytest
from app.models import User
from app.security.crypto import hash_password, create_access_token
from datetime import timedelta


def _make_user(db, email: str, name: str = "Outro") -> tuple:
    """Helper: cria usuário e retorna (user, auth_headers)."""
    user = User(
        name=name,
        email=email,
        password_hash=hash_password("Senha1234!"),
        provider="email",
        email_verified=True,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    from app.security.crypto import create_access_token
    token = create_access_token({"sub": str(user.id), "email": user.email}, timedelta(hours=1))
    return user, {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Create group
# ---------------------------------------------------------------------------

def test_create_group(client, auth_headers):
    """POST /api/groups → 200, grupo criado com join_code."""
    response = client.post(
        "/api/groups",
        headers=auth_headers,
        json={"name": "Meu Bolão", "description": "Grupo de teste", "is_public": False},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Meu Bolão"
    assert "join_code" in data
    assert data["join_code"] is not None  # private group has join code


def test_create_group_public_no_code(client, auth_headers):
    """Grupo público não precisa de join_code."""
    response = client.post(
        "/api/groups",
        headers=auth_headers,
        json={"name": "Bolão Público", "is_public": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_public"] is True
    assert data["join_code"] is None


def test_create_group_unauthenticated(client):
    """POST /api/groups sem token → 401."""
    response = client.post(
        "/api/groups",
        json={"name": "Bolão Sem Auth"},
    )
    assert response.status_code == 401


def test_create_group_short_name(client, auth_headers):
    """Nome com menos de 2 caracteres → 422."""
    response = client.post(
        "/api/groups",
        headers=auth_headers,
        json={"name": "A"},
    )
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# List groups
# ---------------------------------------------------------------------------

def test_list_my_groups_empty(client, auth_headers):
    """GET /api/groups → lista vazia quando não membro de nenhum grupo."""
    response = client.get("/api/groups", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_list_my_groups_after_create(client, auth_headers):
    """Dono do grupo aparece na lista."""
    client.post(
        "/api/groups",
        headers=auth_headers,
        json={"name": "Meu Grupo"},
    )
    response = client.get("/api/groups", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


# ---------------------------------------------------------------------------
# Get group detail
# ---------------------------------------------------------------------------

def test_get_group_detail(client, test_group, test_user, auth_headers):
    """GET /api/groups/{id} retorna grupo com membros."""
    response = client.get(f"/api/groups/{test_group.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_group.id
    assert data["name"] == test_group.name
    assert "members" in data
    assert data["member_count"] == 1
    assert data["members"][0]["user_id"] == test_user.id
    assert data["members"][0]["role"] == "owner"


def test_get_group_not_found(client):
    """GET /api/groups/9999 → 404."""
    response = client.get("/api/groups/9999")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Join group
# ---------------------------------------------------------------------------

def test_join_group_with_valid_code(client, db, test_group):
    """Outro usuário entra no grupo privado com código correto."""
    other_user, other_headers = _make_user(db, "outro@example.com")

    response = client.post(
        f"/api/groups/{test_group.id}/join",
        headers=other_headers,
        params={"join_code": test_group.join_code},
    )
    assert response.status_code == 200
    assert "joined" in response.json()["message"].lower()


def test_join_group_wrong_code(client, db, test_group):
    """Código errado → 403."""
    other_user, other_headers = _make_user(db, "wrong@example.com")

    response = client.post(
        f"/api/groups/{test_group.id}/join",
        headers=other_headers,
        params={"join_code": "CODIGOERRADO"},
    )
    assert response.status_code == 403


def test_join_group_already_member(client, db, test_group, test_user, auth_headers):
    """Tentar entrar num grupo onde já é membro → 400."""
    response = client.post(
        f"/api/groups/{test_group.id}/join",
        headers=auth_headers,
        params={"join_code": test_group.join_code},
    )
    assert response.status_code == 400
    assert "already" in response.json()["detail"].lower()


def test_join_public_group_no_code(client, db, auth_headers):
    """Entrar em grupo público sem código."""
    # Create public group with a different user
    other_user, other_headers = _make_user(db, "creator@example.com")
    create_resp = client.post(
        "/api/groups",
        headers=other_headers,
        json={"name": "Grupo Público", "is_public": True},
    )
    group_id = create_resp.json()["id"]

    response = client.post(
        f"/api/groups/{group_id}/join",
        headers=auth_headers,
    )
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Leave group
# ---------------------------------------------------------------------------

def test_leave_group(client, db, test_group):
    """Membro sai do grupo."""
    member_user, member_headers = _make_user(db, "member@example.com")

    # Join first
    client.post(
        f"/api/groups/{test_group.id}/join",
        headers=member_headers,
        params={"join_code": test_group.join_code},
    )

    # Leave
    response = client.post(
        f"/api/groups/{test_group.id}/leave",
        headers=member_headers,
    )
    assert response.status_code == 200
    assert "left" in response.json()["message"].lower()


def test_owner_cannot_leave(client, test_group, auth_headers):
    """Dono não pode sair do grupo → 400."""
    response = client.post(
        f"/api/groups/{test_group.id}/leave",
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "owner" in response.json()["detail"].lower()


def test_leave_group_not_member(client, db, test_group):
    """Usuário que não é membro tenta sair → 404."""
    other_user, other_headers = _make_user(db, "notmember@example.com")

    response = client.post(
        f"/api/groups/{test_group.id}/leave",
        headers=other_headers,
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Group standings
# ---------------------------------------------------------------------------

def test_group_standings_empty(client, test_group):
    """GET /api/groups/{id}/standings sem ranking calculado → vazio."""
    response = client.get(f"/api/groups/{test_group.id}/standings")
    assert response.status_code == 200
    data = response.json()
    assert data["standings"] == []
    assert "scope" in data
