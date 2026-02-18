"""
Tests for RankingService and ranking endpoints.
"""
import pytest
from datetime import datetime, timezone, timedelta
from app.models import Match, Prediction, MatchStage, MatchStatus
from app.services.ranking import RankingService
from app.services.business import ScoringService


# ---------------------------------------------------------------------------
# RankingService unit tests
# ---------------------------------------------------------------------------

def test_global_standings_none_when_empty(db):
    """Sem partidas finalizadas, get_global_standings retorna None."""
    result = RankingService.get_global_standings(db)
    assert result is None


def test_recalculate_global_ranking_no_finished_matches(db):
    """Sem jogos finalizados, recalculate não gera standings."""
    RankingService.recalculate_global_ranking(db)
    result = RankingService.get_global_standings(db)
    assert result is None


def test_recalculate_global_ranking_with_exact_prediction(db, test_user, finished_match):
    """
    Usuário com placar exato deve ter ScoringService.POINTS_EXACT pontos no ranking.
    """
    # Create an exact prediction (2-1 matches finished_match score)
    pred = Prediction(
        user_id=test_user.id,
        match_id=finished_match.id,
        home_pred=2,
        away_pred=1,
    )
    db.add(pred)
    db.commit()

    RankingService.recalculate_global_ranking(db)
    standings = RankingService.get_global_standings(db)

    assert standings is not None
    assert len(standings["standings"]) == 1
    row = standings["standings"][0]
    assert row["user_id"] == test_user.id
    assert row["total_points"] == ScoringService.POINTS_EXACT
    assert row["exact_matches"] == 1
    assert row["rank"] == 1


def test_recalculate_global_ranking_with_wrong_prediction(db, test_user, finished_match):
    """Palpite errado → 0 pontos no ranking."""
    # finished_match is 2-1 (home win); predict away win
    pred = Prediction(
        user_id=test_user.id,
        match_id=finished_match.id,
        home_pred=0,
        away_pred=3,  # away win — wrong result
    )
    db.add(pred)
    db.commit()

    RankingService.recalculate_global_ranking(db)
    standings = RankingService.get_global_standings(db)
    row = standings["standings"][0]
    assert row["total_points"] == 0
    assert row["exact_matches"] == 0


def test_global_ranking_multiple_users_sorted(db, test_user, test_admin_user, finished_match):
    """Ranking ordena usuários por pontos (desc)."""
    # test_user: exact prediction (POINTS_EXACT)
    pred1 = Prediction(
        user_id=test_user.id,
        match_id=finished_match.id,
        home_pred=2,
        away_pred=1,  # exact
    )
    # test_admin_user: result only (POINTS_RESULT_ONLY)
    pred2 = Prediction(
        user_id=test_admin_user.id,
        match_id=finished_match.id,
        home_pred=3,
        away_pred=1,  # home win but wrong balance
    )
    db.add_all([pred1, pred2])
    db.commit()

    RankingService.recalculate_global_ranking(db)
    standings = RankingService.get_global_standings(db)

    rows = standings["standings"]
    assert len(rows) == 2
    # First place: test_user with exact prediction
    assert rows[0]["user_id"] == test_user.id
    assert rows[0]["total_points"] == ScoringService.POINTS_EXACT
    assert rows[0]["rank"] == 1
    # Second place: admin with result only
    assert rows[1]["user_id"] == test_admin_user.id
    assert rows[1]["total_points"] == ScoringService.POINTS_RESULT_ONLY
    assert rows[1]["rank"] == 2


def test_group_standings_empty(db, test_group):
    """Sem predictions no grupo, get_group_standings retorna None."""
    result = RankingService.get_group_standings(db, test_group.id)
    assert result is None


def test_group_standings_after_match(db, test_user, test_group, finished_match):
    """Ranking do grupo inclui pontos de predições com group_id."""
    pred = Prediction(
        user_id=test_user.id,
        match_id=finished_match.id,
        group_id=test_group.id,
        home_pred=2,
        away_pred=1,  # exact
    )
    db.add(pred)
    db.commit()

    RankingService.recalculate_group_ranking(db, test_group.id)
    standings = RankingService.get_group_standings(db, test_group.id)

    assert standings is not None
    assert len(standings["standings"]) == 1
    row = standings["standings"][0]
    assert row["user_id"] == test_user.id
    assert row["total_points"] == ScoringService.POINTS_EXACT


def test_match_count_in_global_standings(db, test_user, finished_match):
    """standings contém match_count correto."""
    pred = Prediction(
        user_id=test_user.id,
        match_id=finished_match.id,
        home_pred=1,
        away_pred=0,
    )
    db.add(pred)
    db.commit()

    RankingService.recalculate_global_ranking(db)
    standings = RankingService.get_global_standings(db)

    assert standings["match_count"] == 1


# ---------------------------------------------------------------------------
# Rankings API endpoints
# ---------------------------------------------------------------------------

def test_global_rankings_endpoint_empty(client):
    """GET /api/users/rankings/global → lista vazia quando sem dados."""
    response = client.get("/api/users/rankings/global")
    assert response.status_code == 200
    data = response.json()
    assert data["standings"] == []
    assert data["scope"] == "GLOBAL"


def test_group_standings_endpoint(client, test_group):
    """GET /api/groups/{id}/standings → retorna estrutura correta."""
    response = client.get(f"/api/groups/{test_group.id}/standings")
    assert response.status_code == 200
    data = response.json()
    assert "standings" in data
    assert "scope" in data
    assert f"GROUP:{test_group.id}" in data["scope"]
