from app.db import get_db
from app.main import app

JOB = {"company": "Acme", "role": "SDE Intern", "status": "applied", "applied_on": "2026-09-01", "notes": "referral"}


def make(client, **overrides):
    return client.post("/api/jobs", json={**JOB, **overrides})


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_ready(client):
    assert client.get("/ready").status_code == 200


def test_ready_returns_503_when_db_down(client):
    class Broken:
        def execute(self, *_):
            raise RuntimeError("db down")

    app.dependency_overrides[get_db] = lambda: Broken()
    assert client.get("/ready").status_code == 503


def test_create_job(client):
    r = make(client)
    assert r.status_code == 201
    assert r.json()["id"] == 1 and r.json()["company"] == "Acme"


def test_create_rejects_invalid_status(client):
    assert make(client, status="ghosted").status_code == 422


def test_create_rejects_blank_company(client):
    assert make(client, company="   ").status_code == 422


def test_list_and_filter(client):
    make(client)
    make(client, company="Beta", status="offer")
    assert len(client.get("/api/jobs").json()) == 2
    offers = client.get("/api/jobs", params={"status": "offer"}).json()
    assert [j["company"] for j in offers] == ["Beta"]


def test_get_job(client):
    make(client)
    assert client.get("/api/jobs/1").json()["role"] == "SDE Intern"


def test_get_missing_returns_404(client):
    assert client.get("/api/jobs/99").status_code == 404


def test_update_job(client):
    make(client)
    r = client.put("/api/jobs/1", json={**JOB, "status": "interview"})
    assert r.status_code == 200 and r.json()["status"] == "interview"


def test_update_missing_returns_404(client):
    assert client.put("/api/jobs/99", json=JOB).status_code == 404


def test_delete_job(client):
    make(client)
    assert client.delete("/api/jobs/1").status_code == 204
    assert client.get("/api/jobs/1").status_code == 404


def test_delete_missing_returns_404(client):
    assert client.delete("/api/jobs/99").status_code == 404


def test_stats_empty(client):
    assert client.get("/api/jobs/stats").json() == {
        "total": 0, "applied": 0, "interview": 0, "offer": 0, "rejected": 0,
    }


def test_stats_counts(client):
    make(client)
    make(client, status="offer")
    s = client.get("/api/jobs/stats").json()
    assert s["total"] == 2 and s["applied"] == 1 and s["offer"] == 1


def test_metrics_exposed(client):
    client.get("/health")
    body = client.get("/metrics").text
    assert "http_requests_total" in body
