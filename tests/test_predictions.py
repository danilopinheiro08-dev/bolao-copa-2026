"""
Tests for match and prediction endpoints.
"""
import pytest
from datetime import datetime, timezone, timedelta
from app.models import Match, MatchStage, MatchStatus


# ---------------------------------------------------------------------------
# Matches
# ---------------------------------------------------------------------------

def test_list_matches_empty(client):
    """GET /api/matches sem jogos → lista vazia."""
    response = client.get("/api/matches")
    assert response.status_code == 200
    assert response.json() == []


def test_list_matches_with_data(client, test_match):
    """GET /api/matches retorna o jogo criado."""
    response = client.get("/api/matches")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["home_team"] == test_match.home_team
    assert data[0]["away_team"] == test_match.away_team


def test_get_match_by_id(client, test_match):
    """GET /api/matches/{id} retorna o jogo correto."""
    response = client.get(f"/api/matches/{test_match.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_match.id
    assert data["status"] == "SCHEDULED"


def test_get_match_not_found(client):
    """GET /api/matches/9999 → 404."""
    response = client.get("/api/matches/9999")
    assert response.status_code == 404


def test_filter_matches_by_stage(client, test_match):
    """Filtro por stage retorna apenas jogos da fase."""
    response = client.get("/api/matches?stage=GROUP")
    assert response.status_code == 200
    assert len(response.json()) == 1

    response_empty = client.get("/api/matches?stage=FINAL")
    assert response_empty.json() == []


# ---------------------------------------------------------------------------
# Predictions — unauthenticated
# ---------------------------------------------------------------------------

def test_create_prediction_unauthenticated(client, test_match):
    """POST /api/predictions sem token → 401."""
    response = client.post(
        "/api/predictions",
        json={"match_id": test_match.id, "home_pred": 1, "away_pred": 0},
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Predictions — authenticated
# ---------------------------------------------------------------------------

def test_create_prediction(client, test_user, test_match, auth_headers):
    """Cria palpite para jogo futuro: 200."""
    response = client.post(
        "/api/predictions",
        headers=auth_headers,
        json={"match_id": test_match.id, "home_pred": 2, "away_pred": 1},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["home_pred"] == 2
    assert data["away_pred"] == 1
    assert data["match_id"] == test_match.id
    assert data["user_id"] == test_user.id
    assert data["is_locked"] is False


def test_create_prediction_updates_existing(client, test_match, auth_headers):
    """Criar palpite para mesmo jogo novamente → atualiza o existente."""
    client.post(
        "/api/predictions",
        headers=auth_headers,
        json={"match_id": test_match.id, "home_pred": 1, "away_pred": 0},
    )
    response = client.post(
        "/api/predictions",
        headers=auth_headers,
        json={"match_id": test_match.id, "home_pred": 3, "away_pred": 2},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["home_pred"] == 3
    assert data["away_pred"] == 2


def test_create_prediction_locked_match(client, db, test_user, auth_headers):
    """Palpite para jogo que vai começar em menos de 10 minutos → 400."""
    locked_match = Match(
        fifa_match_code="LOCK001",
        stage=MatchStage.GROUP,
        group_name="B",
        match_order=10,
        home_team="Espanha",
        away_team="Portugal",
        kickoff_at_utc=datetime.now(timezone.utc) + timedelta(minutes=5),
        status=MatchStatus.SCHEDULED,
    )
    db.add(locked_match)
    db.commit()
    db.refresh(locked_match)

    response = client.post(
        "/api/predictions",
        headers=auth_headers,
        json={"match_id": locked_match.id, "home_pred": 1, "away_pred": 1},
    )
    assert response.status_code == 400


def test_create_prediction_invalid_score(client, test_match, auth_headers):
    """Placar negativo → 422."""
    response = client.post(
        "/api/predictions",
        headers=auth_headers,
        json={"match_id": test_match.id, "home_pred": -1, "away_pred": 0},
    )
    assert response.status_code == 422


def test_update_prediction(client, test_match, auth_headers):
    """PUT /api/predictions/{id} → atualiza placar."""
    # Create first
    create_resp = client.post(
        "/api/predictions",
        headers=auth_headers,
        json={"match_id": test_match.id, "home_pred": 1, "away_pred": 0},
    )
    pred_id = create_resp.json()["id"]

    # Update
    response = client.put(
        f"/api/predictions/{pred_id}",
        headers=auth_headers,
        json={"home_pred": 3, "away_pred": 1},
    )
    assert response.status_code == 200
    assert response.json()["home_pred"] == 3
    assert response.json()["away_pred"] == 1


def test_update_prediction_not_owner(client, db, test_match, auth_headers):
    """Tentar atualizar palpite de outro usuário → 403."""
    from app.models import User, Prediction
    from app.security.crypto import hash_password, create_access_token

    # Create another user and prediction
    other = User(
        name="Outro",
        email="outro@example.com",
        password_hash=hash_password("Senha1234!"),
        provider="email",
        email_verified=True,
        is_active=True,
    )
    db.add(other)
    db.commit()
    db.refresh(other)

    pred = Prediction(
        user_id=other.id,
        match_id=test_match.id,
        home_pred=2,
        away_pred=0,
    )
    db.add(pred)
    db.commit()
    db.refresh(pred)

    # Try to update as test_user
    response = client.put(
        f"/api/predictions/{pred.id}",
        headers=auth_headers,
        json={"home_pred": 1, "away_pred": 1},
    )
    assert response.status_code == 403


def test_get_my_predictions_empty(client, auth_headers):
    """GET /api/my/predictions sem palpites → lista vazia."""
    response = client.get("/api/my/predictions", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_get_my_predictions(client, test_match, auth_headers):
    """GET /api/my/predictions retorna palpites do usuário."""
    client.post(
        "/api/predictions",
        headers=auth_headers,
        json={"match_id": test_match.id, "home_pred": 2, "away_pred": 1},
    )
    response = client.get("/api/my/predictions", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["prediction"]["home_pred"] == 2


def test_get_match_predictions(client, test_match, auth_headers):
    """GET /api/matches/{id}/predictions retorna lista de palpites do jogo."""
    client.post(
        "/api/predictions",
        headers=auth_headers,
        json={"match_id": test_match.id, "home_pred": 1, "away_pred": 0},
    )
    response = client.get(f"/api/matches/{test_match.id}/predictions")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert "home_pred" in data[0]


def test_get_upcoming_matches(client, test_match, auth_headers):
    """GET /api/my/upcoming retorna jogos futuros sem palpite."""
    response = client.get("/api/my/upcoming", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == test_match.id
