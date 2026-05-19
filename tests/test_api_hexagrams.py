"""GET /api/hexagrams 與 GET /api/hexagrams/{seq}。"""
import pytest


@pytest.mark.asyncio
async def test_list_returns_64(client):
    r = await client.get("/api/hexagrams?lang=zh-TW")
    assert r.status_code == 200
    docs = r.json()
    assert len(docs) == 64
    # 第 1 卦應為乾(序卦傳序)
    seq1 = next(d for d in docs if d["sequence"] == 1)
    assert seq1["name"] == "乾"


@pytest.mark.asyncio
async def test_list_english(client):
    r = await client.get("/api/hexagrams?lang=en")
    assert r.status_code == 200
    docs = r.json()
    seq1 = next(d for d in docs if d["sequence"] == 1)
    assert seq1["name"] == "Qian"


@pytest.mark.asyncio
async def test_get_single_with_lines(client):
    r = await client.get("/api/hexagrams/1?lang=zh-TW")
    assert r.status_code == 200
    h = r.json()
    assert h["name"] == "乾"
    assert h["sequence"] == 1
    assert len(h["lines"]) == 6
    assert h["lines"][0]["position"] == 1
    assert "潛龍勿用" in h["lines"][0]["text"]


@pytest.mark.asyncio
async def test_get_invalid_sequence(client):
    r = await client.get("/api/hexagrams/0")
    assert r.status_code == 400
    r = await client.get("/api/hexagrams/65")
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_get_non_integer(client):
    """非整數 sequence 應由 FastAPI 自動回 422。"""
    r = await client.get("/api/hexagrams/abc")
    assert r.status_code == 422
