"""
Tests for ScoringService — pontuação de palpites.
These tests are pure unit tests (no DB needed).
"""
import pytest
from app.models import Match, Prediction, MatchStatus, MatchStage
from app.services.business import ScoringService
from datetime import datetime, timezone


def make_match(home_score: int, away_score: int, finished: bool = True) -> Match:
    """Helper: create a Match object in memory (no DB)."""
    match = Match()
    match.id = 1
    match.home_team = "Team A"
    match.away_team = "Team B"
    match.stage = MatchStage.GROUP
    match.group_name = "A"
    match.match_order = 1
    match.kickoff_at_utc = datetime.now(timezone.utc)
    match.home_score = home_score
    match.away_score = away_score
    match.status = MatchStatus.FINISHED if finished else MatchStatus.SCHEDULED
    return match


def make_prediction(home_pred: int, away_pred: int) -> Prediction:
    """Helper: create a Prediction object in memory (no DB)."""
    pred = Prediction()
    pred.user_id = 1
    pred.match_id = 1
    pred.home_pred = home_pred
    pred.away_pred = away_pred
    return pred


# ---------------------------------------------------------------------------
# Exact score tests (5 points)
# ---------------------------------------------------------------------------

def test_exact_score_home_win():
    """Placar exato numa vitória do time da casa: 5 pontos."""
    pred = make_prediction(2, 1)
    match = make_match(2, 1)
    points, details = ScoringService.calculate_points(pred, match)
    assert points == ScoringService.POINTS_EXACT
    assert details["exact"] is True
    assert details["result"] is False  # exact implies early return


def test_exact_score_away_win():
    """Placar exato numa vitória do visitante: 5 pontos."""
    pred = make_prediction(0, 3)
    match = make_match(0, 3)
    points, details = ScoringService.calculate_points(pred, match)
    assert points == ScoringService.POINTS_EXACT
    assert details["exact"] is True


def test_exact_score_draw():
    """Placar exato num empate: 5 pontos."""
    pred = make_prediction(1, 1)
    match = make_match(1, 1)
    points, details = ScoringService.calculate_points(pred, match)
    assert points == ScoringService.POINTS_EXACT
    assert details["exact"] is True


def test_exact_zero_zero():
    """Placar exato 0-0: 5 pontos."""
    pred = make_prediction(0, 0)
    match = make_match(0, 0)
    points, details = ScoringService.calculate_points(pred, match)
    assert points == ScoringService.POINTS_EXACT


# ---------------------------------------------------------------------------
# Result + balance tests (3 points)
# ---------------------------------------------------------------------------

def test_result_and_balance_home_win():
    """
    Resultado correto + mesmo saldo de gols: 3 pontos.
    Pred: 3-1 (home +2)  |  Real: 2-0 (home +2)
    """
    pred = make_prediction(3, 1)
    match = make_match(2, 0)
    points, details = ScoringService.calculate_points(pred, match)
    assert points == ScoringService.POINTS_RESULT_BALANCE
    assert details["result"] is True
    assert details["balance"] is True
    assert details["exact"] is False


def test_result_and_balance_away_win():
    """
    Visitante vence com mesmo saldo: 3 pontos.
    Pred: 0-2 (away +2)  |  Real: 1-3 (away +2)
    """
    pred = make_prediction(0, 2)
    match = make_match(1, 3)
    points, details = ScoringService.calculate_points(pred, match)
    assert points == ScoringService.POINTS_RESULT_BALANCE
    assert details["result"] is True
    assert details["balance"] is True


def test_result_and_balance_draw():
    """
    Empate com mesmo placar diferencial (0): 3 pontos.
    Pred: 2-2  |  Real: 1-1
    """
    pred = make_prediction(2, 2)
    match = make_match(1, 1)
    points, details = ScoringService.calculate_points(pred, match)
    assert points == ScoringService.POINTS_RESULT_BALANCE
    assert details["result"] is True
    assert details["balance"] is True


# ---------------------------------------------------------------------------
# Result only tests (2 points)
# ---------------------------------------------------------------------------

def test_result_only_home_win():
    """
    Resultado correto mas saldo diferente: 2 pontos.
    Pred: 3-1 (home +2)  |  Real: 2-1 (home +1)
    """
    pred = make_prediction(3, 1)
    match = make_match(2, 1)
    points, details = ScoringService.calculate_points(pred, match)
    assert points == ScoringService.POINTS_RESULT_ONLY
    assert details["result"] is True
    assert details["balance"] is False
    assert details["exact"] is False


def test_result_only_away_win():
    """
    Visitante vence mas saldo diferente: 2 pontos.
    Pred: 0-1 (away +1)  |  Real: 0-3 (away +3)
    """
    pred = make_prediction(0, 1)
    match = make_match(0, 3)
    points, details = ScoringService.calculate_points(pred, match)
    assert points == ScoringService.POINTS_RESULT_ONLY
    assert details["result"] is True
    assert details["balance"] is False


# ---------------------------------------------------------------------------
# No points tests (0 points)
# ---------------------------------------------------------------------------

def test_no_points_wrong_result():
    """Resultado errado: 0 pontos."""
    pred = make_prediction(2, 0)  # home win
    match = make_match(1, 2)      # away win
    points, details = ScoringService.calculate_points(pred, match)
    assert points == 0
    assert details["result"] is False
    assert details["exact"] is False


def test_no_points_draw_predicted_win():
    """Previu vitória, acabou empate: 0 pontos."""
    pred = make_prediction(2, 1)  # home win
    match = make_match(1, 1)      # draw
    points, details = ScoringService.calculate_points(pred, match)
    assert points == 0


def test_no_points_win_predicted_draw():
    """Previu empate, um time ganhou: 0 pontos."""
    pred = make_prediction(1, 1)  # draw
    match = make_match(2, 0)      # home win
    points, details = ScoringService.calculate_points(pred, match)
    assert points == 0


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_match_not_finished_returns_zero():
    """Jogo não terminado: sem pontos."""
    pred = make_prediction(1, 1)
    match = make_match(1, 1, finished=False)
    points, details = ScoringService.calculate_points(pred, match)
    assert points == 0
    assert details == {}


def test_match_score_is_none():
    """Placar nulo (match sem resultado): sem pontos."""
    pred = make_prediction(1, 0)
    match = make_match(0, 0)
    match.home_score = None
    match.away_score = None
    points, details = ScoringService.calculate_points(pred, match)
    assert points == 0


def test_scoring_constants_are_ordered():
    """Sanidade: EXACT > RESULT_BALANCE > RESULT_ONLY > 0."""
    assert ScoringService.POINTS_EXACT > ScoringService.POINTS_RESULT_BALANCE
    assert ScoringService.POINTS_RESULT_BALANCE > ScoringService.POINTS_RESULT_ONLY
    assert ScoringService.POINTS_RESULT_ONLY > 0
