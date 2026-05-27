# 蓍草法周易占卜 v2 / Yarrow Stalk I Ching

從原本 Flask + Redis + Vanilla JS 的單體應用,重構為 **FastAPI + MongoDB + Alpine.js** 的前後端分離架構,並徹底重做 UI/UX。

- **前端**:GitHub Pages https://yuzenchen.github.io/zhouyi/
- **後端**:Render https://zhouyi-api-8mvi.onrender.com/health
- **資料庫**:MongoDB Atlas (M0 Free)

---

## 重構亮點

### 後端
- **FastAPI 0.115** + Motor 3.6(async MongoDB driver)取代 Flask + Redis
- **修正 64 卦對照表 bug**:原版有重複映射(`(1,0)` 與 `(5,1)` 都對應「復」),依序卦傳重建並有測試強制驗證 64 個 (inner, outer) 唯一
- **修正占卜種子 bug**:原版 `seed = YYYYMMDDHHMMSS` 同秒撞卦,改用 `secrets.SystemRandom`(OS-level 熵源)
- **完整動爻 / 變卦邏輯**:偵測老陰 6 / 老陽 9,本卦 + 變卦同時呈現
- **64 卦完整資料**:卦辭、象辭、384 條爻辭(中英雙語,通行本周易)
- **匿名 session 隔離**:localStorage UUID + server-side 嚴格比對(他人 URL 拿不到資料)
- **AI proxy 模式**:n8n webhook URL 不外露,後端代理 + 防禦性 JSON 解析

### 前端
- **設計方向**:現代古籍編排 — 象牙紙 (`#f5f1e8`) + 墨黑 (`#1a1612`) + 朱砂 (`#a3331c`) 單一 accent
- **字體**:Noto Serif TC + Cormorant Garamond + JetBrains Mono
- **Alpine.js 3.14**(15 KB)反應式 UI,**無 build step**
- **狀態機**:idle → casting → waiting → result(cold start 期間 inline 提示「凝思中」+ 已等待秒數)
- 三個畫面:占卜 / 歷史 / 64 卦目錄
- 詳情 modal(歷史 + 目錄共用)— 動爻整行朱砂強調
- **PNG 分享卡**:html2canvas 一鍵下載

### DevOps
- **GitHub Pages + Render + Atlas** 三層免費部署
- **GitHub Actions**:push 自動跑 30 個測試(ubuntu + mongo:7 service);Pages 自動部署
- **啟動時 auto-seed**:Render Free 無 Shell 可手動 seed,改在 lifespan 偵測空 collection 時自動寫入
- **瀏覽器時區優先**:`Intl.DateTimeFormat` 取代 IP geo(VPN / 私有 IP 都正確)

---

## 專案結構

```
zhouyi-v2/
├── app/                              FastAPI backend
│   ├── main.py                       入口 + StaticFiles mount(/static legacy + / SPA)
│   ├── config.py                     Pydantic settings(MONGODB_URI, CORS_ORIGINS, ...)
│   ├── database.py                   Motor lifespan + ensure_hexagrams_seeded()
│   ├── models/{hexagram,divination}.py
│   ├── services/
│   │   ├── divination.py             蓍草法 + 動爻變卦
│   │   ├── hexagram_service.py       DB 查詢
│   │   └── geo.py                    IP 地理(失敗不阻塞)
│   ├── routers/
│   │   ├── divinate.py               POST /api/divinate
│   │   ├── hexagrams.py              GET /api/hexagrams[/{seq}]
│   │   ├── history.py                GET/DELETE /api/history[/{id}](session 隔離)
│   │   └── ai.py                     POST /api/ai-analysis(n8n proxy)
│   └── utils/trigrams.py             序卦傳序 64 卦對照表
├── data/hexagrams_seed.py            SEED_DATA(卦辭/象辭) + LINES_DATA(384 爻辭)
├── scripts/seed_hexagrams.py         手動 seed(也可靠 lifespan 自動)
├── static/                           前端(Pages 部署 root)
│   ├── index.html                    <meta name="api-base"> 指向 Render
│   ├── css/main.css                  設計 tokens + 動畫
│   ├── js/main.js                    Alpine app + API client + i18n
│   └── assets/favicon.svg
├── tests/                            30 個測試
│   ├── conftest.py                   AsyncClient fixture + 獨立 zhouyi_test DB
│   ├── test_divination.py            蓍草法核心(9)
│   ├── test_api_divinate.py          POST /api/divinate(4)
│   ├── test_api_hexagrams.py         GET 列表/單卦/錯誤(5)
│   ├── test_api_history.py           session 隔離 + CRUD(8)
│   └── test_i18n.py                  to_localized 雙語切換(4)
├── .github/workflows/
│   ├── test.yml                      push/PR 跑 pytest + mongo:7 service
│   └── pages.yml                     push 時 deploy static/ 到 Pages
├── pytest.ini                        asyncio_mode = auto
├── requirements.txt                  production
├── requirements-dev.txt              + pytest, pytest-asyncio
├── render.yaml                       Render Blueprint
├── Dockerfile                        備用
└── .env.example
```

---

## 本地開發

需 Docker (推薦) 或 Python 3.12 + 本機 MongoDB。

### 用 Docker(推薦)

```powershell
# 1. 起獨立 mongo 容器(避免影響其他專案)
docker run -d --name zhouyi-mongo -p 27018:27017 mongo:7

# 2. 設 .env
cp .env.example .env
# 編輯 MONGODB_URI=mongodb://host.docker.internal:27018

# 3. build & run
docker build -t zhouyi-v2 .
docker run -d --name zhouyi-app -p 8000:8000 --env-file .env --add-host=host.docker.internal:host-gateway zhouyi-v2

# 啟動時會自動 seed 64 卦
```

### 直接跑 Python

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env
# 編輯 .env 填 MONGODB_URI

python -m scripts.seed_hexagrams --reset   # 或直接讓 lifespan auto-seed
uvicorn app.main:app --reload --port 8000
```

開啟:
- 應用:http://localhost:8000
- API docs:http://localhost:8000/docs
- Health:http://localhost:8000/health

### 跑測試

```bash
python -m pytest tests/ -v
```

---

## 部署(前後端分離)

### 1. MongoDB Atlas (Free M0)
1. https://www.mongodb.com/atlas → 建免費 M0 cluster(AWS / Singapore)
2. Database Access 建 user;Network Access 加 `0.0.0.0/0`(Render 出口 IP 不固定)
3. Connect → Drivers → 複製 `mongodb+srv://...` 連線字串

> **為何不用 Railway:** Railway free MongoDB volume 太小,首次建 index 就會 `OutOfDiskSpace`。Atlas M0 實測穩定。

### 2. Render(Backend)
1. https://dashboard.render.com → **New +** → **Blueprint**
2. Connect repo `yuzenchen/zhouyi`,Render 讀取 `render.yaml` 自動建立 `zhouyi-api` service
3. Apply 前填兩個 secret env vars(`render.yaml` 中 `sync: false`):
   - `MONGODB_URI`:Atlas 連線字串
   - `N8N_AI_WEBHOOK`:你的 n8n webhook
4. 部署完後改 `CORS_ORIGINS` 為 `https://yuzenchen.github.io`(避免 wildcard + credentials)
5. 首次啟動 lifespan 會自動 seed 64 卦,不用手動跑

### 3. GitHub Pages(Frontend)
1. Repo Settings → Pages → **Source: GitHub Actions**
2. push 到 main 時 `.github/workflows/pages.yml` 自動部署 `static/`
3. 若 Render service name 變動,要更新 `static/index.html` 的 `<meta name="api-base">`

---

## API

完整文件:`/docs`(Swagger UI 自動產生)

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/divinate` | 擲一卦,寫入歷史(`client_tz` 帶瀏覽器時區) |
| `GET`  | `/api/hexagrams` | 列出 64 卦 |
| `GET`  | `/api/hexagrams/{seq}` | 取單卦 (1~64),含爻辭 |
| `GET`  | `/api/history?session_id=X` | session 歷史(隔離) |
| `GET`  | `/api/history/{id}?session_id=X` | 單筆詳情(session 比對) |
| `DELETE` | `/api/history/{id}?session_id=X` | 刪除(僅同 session) |
| `POST` | `/api/ai-analysis` | 代理到 n8n,選擇性寫回 record |
| `GET`  | `/health` | 健康檢查 |

---

## 硬性規則(給未來改動者)

1. **64 卦對照表是 source of truth** — 任何 `app/utils/trigrams.py` 改動必須過 `test_64_hexagrams_unique` 與 `test_trigram_keys_complete`
2. **設計鐵則** — 禁止引入第二個 accent color,所有強調用 `--vermilion`
3. **session 隔離不可繞** — 任何寫/讀 history 都必須 server-side 比對 `session_id`,測試於 `test_api_history.py` 強制保護
4. **走 router / service / model 分層** — 不要把 endpoint 直接寫進 `main.py`,DB 查詢不繞 service 層
5. **i18n 強制雙語** — user-facing 字串都要 zh-TW + en,前端 `translations` 與後端 `to_localized()`
6. **古文準確性** — 64 卦卦辭/象辭/爻辭採通行本(王弼/朱熹),不可隨意改寫

---

## License

MIT(沿用原專案)
