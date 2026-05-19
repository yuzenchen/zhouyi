"""Session 隔離與 history endpoints。"""
import pytest


async def _cast(client, session_id: str, question: str | None = None):
    r = await client.post("/api/divinate", json={
        "session_id": session_id,
        "question": question,
        "lang": "zh-TW",
    })
    assert r.status_code == 200
    return r.json()


@pytest.mark.asyncio
async def test_history_empty_initially(client):
    r = await client.get("/api/history?session_id=sess_emptyaaa11111")
    assert r.status_code == 200
    assert r.json() == []


@pytest.mark.asyncio
async def test_history_returns_own_session(client):
    sid = "sess_owner_bbbb2222"
    await _cast(client, sid, "Q1")
    await _cast(client, sid, "Q2")

    r = await client.get(f"/api/history?session_id={sid}")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 2
    # 最新的在前
    assert items[0]["question"] == "Q2"


@pytest.mark.asyncio
async def test_session_isolation(client):
    sid1 = "sess_isoaaaa11111"
    sid2 = "sess_isobbbb22222"

    await _cast(client, sid1, "私密問題")

    r = await client.get(f"/api/history?session_id={sid2}")
    assert r.json() == [], "session2 不應看到 session1 的記錄"

    r = await client.get(f"/api/history?session_id={sid1}")
    assert len(r.json()) == 1


@pytest.mark.asyncio
async def test_get_detail_wrong_session_404(client):
    sid_owner = "sess_ownerrcccc3333"
    sid_attacker = "sess_attackdddd4444"

    cast = await _cast(client, sid_owner)
    record_id = cast["id"]

    r = await client.get(f"/api/history/{record_id}?session_id={sid_attacker}")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_get_detail_own_session_ok(client):
    sid = "sess_detail_eeee5555"
    cast = await _cast(client, sid, "詳情問題")

    r = await client.get(f"/api/history/{cast['id']}?session_id={sid}")
    assert r.status_code == 200
    d = r.json()
    assert d["question"] == "詳情問題"
    assert "primary" in d
    assert d["primary"] is not None


@pytest.mark.asyncio
async def test_delete_wrong_session_404(client):
    sid_owner = "sess_delowner_ffff6666"
    sid_attacker = "sess_delattck_gggg7777"

    cast = await _cast(client, sid_owner)
    r = await client.delete(f"/api/history/{cast['id']}?session_id={sid_attacker}")
    assert r.status_code == 404

    # 確認沒被刪
    r = await client.get(f"/api/history/{cast['id']}?session_id={sid_owner}")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_delete_own_session_ok(client):
    sid = "sess_delete_hhhh8888"
    cast = await _cast(client, sid)

    r = await client.delete(f"/api/history/{cast['id']}?session_id={sid}")
    assert r.status_code == 200
    assert r.json()["deleted"] is True

    # 已不存在
    r = await client.get(f"/api/history/{cast['id']}?session_id={sid}")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_delete_invalid_objectid_400(client):
    r = await client.delete("/api/history/not-an-objectid?session_id=sess_dummmmiiii999")
    assert r.status_code == 400
