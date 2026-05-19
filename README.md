# 蓍草法周易占卜 v2 / Yarrow Stalk I Ching — Refactored

從原本 Flask + Redis + Vanilla JS 的單體應用,重構為 **FastAPI + MongoDB(Railway)** 的現代化架構,並徹底重做 UI/UX。

---

## 重構亮點

### 後端
- **FastAPI** 取代 Flask:async I/O、自動 API docs (`/docs`)、Pydantic 型別驗證
- **MongoDB (Motor async driver)** 取代 Redis:儲存 64 卦資料 + 占卜歷史
- **修正 64 卦對照表的 bug**:原版有重複映射(`(1,0)` 與 `(5,1)` 都對應「復」),全部按伏羲先天八卦序重做
- **修正占卜種子 bug**:原版 `seed=YYYYMMDDHHMMSS` 同秒撞卦,改用 `secrets.SystemRandom`
- **新增動爻 / 變卦邏輯**:原版只算本卦,現可同時呈現變卦
- **占卜歷史**:以 session_id (匿名 UUID) 為單位持久化

### 前端
- **設計方向**:現代古籍編排 — 象牙白 + 墨黑 + 朱砂紅,Noto Serif TC + Cormorant Garamond
- **Alpine.js (15kb)** 提供反應式 UI,無 build step
- 三個畫面:占卜 / 歷史 / 64 卦目錄
- 蓍草分堆動畫保留但用 SVG/CSS 重寫(效能更好)
- 響應式設計,行動裝置優先

### DevOps
- **Render** 一鍵部署 (`render.yaml`)
- **Railway MongoDB** 透過環境變數連線
- Health check endpoint
- 環境變數管理(`.env`)取代寫死的設定

---

## 專案結構

```
zhouyi-v2/
├── app/
│   ├── main.py                  FastAPI 入口、CORS、靜態檔
│   ├── config.py                Pydantic settings
│   ├── database.py              MongoDB async 連線 + lifespan
│   ├── models/
│   │   ├── hexagram.py
│   │   └── divination.py
│   ├── services/
│   │   ├── divination.py        蓍草法核心邏輯
│   │   ├── hexagram_service.py  DB 查詢
│   │   └── geo.py               IP 地理位置
│   ├── routers/
│   │   ├── divinate.py          POST /api/divinate
│   │   ├── hexagrams.py         GET /api/hexagrams
│   │   ├── history.py           GET/DELETE /api/history
│   │   └── ai.py                POST /api/ai-analysis
│   └── utils/
│       └── trigrams.py          修正後的 64 卦對照表
├── data/
│   └── hexagrams_seed.py        64 卦卦辭+象辭資料
├── scripts/
│   └── seed_hexagrams.py        DB seed 腳本
├── static/                       前端
│   ├── index.html
│   ├── css/main.css
│   ├── js/main.js
│   └── assets/favicon.svg
├── requirements.txt
├── render.yaml                   Render 部署設定
├── Dockerfile
└── .env.example
```

---

## 本地開發

```bash
# 1. 安裝依賴
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. 設定環境變數
cp .env.example .env
# 編輯 .env 填入 Railway MongoDB URI

# 3. 種入 64 卦資料
python -m scripts.seed_hexagrams --reset

# 4. 啟動
uvicorn app.main:app --reload --port 8000
```

開啟:
- 應用:http://localhost:8000
- API docs:http://localhost:8000/docs
- Health:http://localhost:8000/health

---

## 部署

### Railway (MongoDB)
1. 到 [Railway](https://railway.app) 建立專案 → New → Database → MongoDB
2. 在 Variables tab 取得 `MONGO_URL`(注意是 internal/external URL 都可,Render 用 external)
3. 在 Railway 的 MongoDB shell 或本地連線後,執行 seed 腳本

### Render (Backend)
1. 推 code 上 GitHub
2. 到 [Render](https://render.com) → New → Blueprint → 選 repo
3. Render 會自動讀 `render.yaml`,只需在 dashboard 補上兩個敏感環境變數:
   - `MONGODB_URI`:Railway 的 MongoDB URL
   - `N8N_AI_WEBHOOK`:你原本的 n8n webhook URL
4. 首次部署完成後,在 Render shell 執行一次 seed:
   ```bash
   python -m scripts.seed_hexagrams
   ```

---

## API 摘要

完整文件:`/docs`(FastAPI 自動產生 Swagger UI)

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/divinate` | 擲一卦,寫入歷史 |
| `GET`  | `/api/hexagrams` | 列出 64 卦 |
| `GET`  | `/api/hexagrams/{seq}` | 取單卦 (1~64) |
| `GET`  | `/api/history` | 取得 session 歷史 |
| `DELETE` | `/api/history/{id}` | 刪除一筆 |
| `POST` | `/api/ai-analysis` | 代理到 n8n,選擇性寫回 record |
| `GET`  | `/health` | Render health check |

---

## 待擴充

- [ ] 64 卦的爻辭(目前 `lines: []`,可後續補上)
- [ ] AI 解卦結果的 streaming
- [ ] 占卜結果分享卡(PNG 匯出)
- [ ] PWA 離線支援
- [ ] 卦象 modal 詳細頁(目前 catalog 點擊只 alert)

---

## License

MIT(沿用原專案)
