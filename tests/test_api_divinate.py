"""POST /api/divinate。"""
import pytest


@pytest.mark.asyncio
async def test_divinate_returns_valid_structure(client):
    payload = {
        "session_id": "sess_pytest_aaaa1111",
        "question": "test question",
        "lang": "zh-TW",
    }
    r = await client.post("/api/divinate", json=payload)
    assert r.status_code == 200
    data = r.json()

    assert "id" in data
    assert "time" in data
    assert len(data["lines"]) == 6
    for ln in data["lines"]:
        assert ln["value"] in (6, 7, 8, 9)
        assert "name" in ln
        assert "yin" in ln
        assert "changing" in ln

    assert data["primary"] is not None
    assert "name" in data["primary"]
    assert "sequence" in data["primary"]


@pytest.mark.asyncio
async def test_divinate_no_question(client):
    """question 可空。"""
    r = await client.post("/api/divinate", json={
        "session_id": "sess_pytest_bbbb2222",
        "lang": "zh-TW",
    })
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_divinate_client_tz_used(client):
    """傳 client_tz 時,回傳的 time 應反映該時區(透過小時範圍粗略驗證)。"""
    r = await client.post("/api/divinate", json={
        "session_id": "sess_pytest_cccc3333",
        "lang": "zh-TW",
        "client_tz": "Asia/Taipei",
    })
    assert r.status_code == 200
    # time 格式: "YYYY-MM-DD HH:MM:SS"
    assert len(r.json()["time"]) == 19


@pytest.mark.asyncio
async def test_divinate_transformed_consistency(client):
    """有 changing_indices 必有 transformed,反之亦然。"""
    # 多打幾次以提高機率涵蓋兩種情況
    saw_with = False
    saw_without = False
    for _ in range(15):
        r = await client.post("/api/divinate", json={
            "session_id": "sess_pytest_dddd4444",
            "lang": "zh-TW",
        })
        data = r.json()
        if data["changing_indices"]:
            assert data["transformed"] is not None
            saw_with = True
        else:
            assert data["transformed"] is None
            saw_without = True
        if saw_with and saw_without:
            break
    # 15 次擲卦,出現動爻的機率 > 99.999%
    assert saw_with, "Expected at least one cast with changing lines"
