"""API liveness, readiness, CORS, and error contract tests."""

import asyncio
from collections.abc import Generator
from typing import Any

from httpx import ASGITransport, AsyncClient, Response
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.main import app


def api_request(method: str, path: str, **kwargs: Any) -> Response:
    async def send_request() -> Response:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.request(method, path, **kwargs)

    return asyncio.run(send_request())


def test_health_reports_process_liveness() -> None:
    response = api_request("GET", "/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_checks_database(db_session: Session) -> None:
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        response = api_request("GET", "/api/v1/ready")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"status": "ready", "checks": {"database": "ok"}}


def test_readiness_returns_503_when_database_query_fails() -> None:
    class UnavailableSession:
        def execute(self, statement: object) -> None:
            raise OperationalError(str(statement), {}, RuntimeError("offline"))

    def unavailable_session() -> Generator[UnavailableSession, None, None]:
        yield UnavailableSession()

    app.dependency_overrides[get_db] = unavailable_session
    try:
        response = api_request("GET", "/api/v1/ready")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json() == {
        "error": {"code": "database_unavailable", "message": "Database is not ready."}
    }


def test_cors_allows_only_configured_origins() -> None:
    allowed = api_request(
        "OPTIONS",
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    denied = api_request(
        "OPTIONS",
        "/api/v1/health",
        headers={
            "Origin": "https://untrusted.example",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert allowed.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert "access-control-allow-origin" not in denied.headers


def test_http_errors_use_consistent_safe_shape() -> None:
    response = api_request("GET", "/missing-route")

    assert response.status_code == 404
    assert response.json() == {
        "error": {"code": "not_found", "message": "Not Found"}
    }


def test_readiness_executes_database_probe(db_session: Session) -> None:
    assert db_session.execute(text("SELECT 1")).scalar_one() == 1
