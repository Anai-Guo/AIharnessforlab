"""Tests for Web API endpoints."""

import pytest

# Need httpx for async testing
pytest.importorskip("httpx")
pytest.importorskip("fastapi")

from httpx import ASGITransport, AsyncClient

from lab_harness.web.app import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "templates_available" in data


@pytest.mark.asyncio
async def test_list_templates(client):
    resp = await client.get("/api/templates")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] >= 46
    assert "iv" in data["templates"]


@pytest.mark.asyncio
async def test_get_template(client):
    resp = await client.get("/api/templates/iv")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "IV Measurement"


@pytest.mark.asyncio
async def test_get_template_not_found(client):
    resp = await client.get("/api/templates/nonexistent")
    assert resp.status_code == 200
    data = resp.json()
    assert "error" in data


@pytest.mark.asyncio
async def test_dashboard_page(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "LabAgent" in resp.text or "labharness" in resp.text.lower()


@pytest.mark.asyncio
async def test_monitor_page(client):
    resp = await client.get("/monitor")
    assert resp.status_code == 200
    assert "Monitor" in resp.text or "monitor" in resp.text.lower()
