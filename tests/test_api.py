import pytest
from httpx import AsyncClient, ASGITransport
from server.app import app

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_reset_easy():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.post("/reset", json={"task": "easy", "seed": 42})
    assert r.status_code == 200 and r.json()["observation"]["status"] == "open"

@pytest.mark.asyncio
async def test_reset_without_body_defaults_to_easy():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.post("/reset")
    assert r.status_code == 200 and r.json()["observation"]["status"] == "open"
