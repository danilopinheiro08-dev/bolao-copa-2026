"""
Smoke tests: health check and status endpoint.
Full auth/scoring/prediction/group/ranking tests are in dedicated files.
"""


def test_health_check(client):
    """GET /health → 200 com campo 'status'."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ("ok", "degraded")


def test_status_check(client):
    """GET /status → 200 com nome do serviço."""
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert data["service"]  # non-empty string


def test_unknown_route_returns_404(client):
    """Rota desconhecida → 404."""
    response = client.get("/rota-que-nao-existe")
    assert response.status_code == 404
