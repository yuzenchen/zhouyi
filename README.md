# 蓍草法周易占卜 / Yarrow Stalk I Ching Divination

一個結合傳統中國周易占卜與現代 AI 分析的 Web 應用程式。<br>
A web application combining traditional Chinese I Ching divination with modern AI analysis.

## 特色功能 / Features

### ✨ 多語系支援 / Multilingual Support
- **繁體中文** (Traditional Chinese) - 完整的傳統中文介面
- **English** - Full English interface with hexagram translations
- **語言切換** - Easy language switching via URL or interface

### 🔮 占卜功能 / Divination Features
- **蓍草法占卜** - Authentic yarrow stalk divination method
- **動畫效果** - Animated yarrow stalk simulation
- **六十四卦完整翻譯** - Complete 64 hexagrams in both languages
- **地理位置整合** - Geographic location integration for timing

### 🤖 AI 分析 / AI Analysis
- **智能解析** - AI-powered hexagram interpretation
- **個人化回應** - Personalized responses based on user questions
- **多語言 AI** - AI analysis in user's preferred language

### 📱 響應式設計 / Responsive Design
- **行動裝置優化** - Mobile-optimized interface
- **跨平台支援** - Works on all devices and browsers

## 項目架構 / Project Structure

```
zhouyi/
├── app.py                 # Flask 主應用程式 / Main Flask application
├── requirements.txt       # Python 依賴 / Python dependencies
├── Dockerfile            # Docker 容器配置 / Container configuration
├── deploy.sh             # 部署腳本 / Deployment script
├── templates/
│   └── index.html        # 主頁面模板 / Main page template
├── static/
│   ├── style.css         # 樣式表 / Stylesheet
│   ├── main.js           # JavaScript 邏輯 / Frontend logic
│   └── favicon.ico       # 網站圖示 / Site icon
└── redis/                # Redis 配置 / Redis configuration
```

## 安裝與部署 / Installation & Deployment

### 方法 1：本地運行 / Method 1: Local Development

1. **克隆倉庫 / Clone repository**
```bash
git clone https://github.com/yuzenchen/zhouyi.git
cd zhouyi
```

2. **安裝依賴 / Install dependencies**
```bash
pip install -r requirements.txt
```

3. **啟動應用 / Start application**
```bash
python app.py
```

4. **訪問應用 / Access application**
- 中文版 / Chinese: `http://localhost:888/`
- 英文版 / English: `http://localhost:888/en`

### 方法 2：Docker 部署 / Method 2: Docker Deployment

1. **構建鏡像 / Build image**
```bash
./deploy.sh
```

2. **或手動構建 / Or build manually**
```bash
docker build -t zhouyi-app .
docker run -d -p 1688:888 --name zhouyi-container zhouyi-app
```

3. **訪問應用 / Access application**
- 中文版 / Chinese: `http://localhost:1688/`
- 英文版 / English: `http://localhost:1688/en`

## API 文檔 / API Documentation

### 1. 占卜 API / Divination API

**Endpoint:** `GET /api/divinate`

**參數 / Parameters:**
- `lang` (optional): 語言代碼 / Language code (`zh-TW`, `en`)

**回應範例 / Response Example:**
```json
{
  "time": "2025-10-09 16:30:45",
  "geo": {
    "ip": "192.168.1.1",
    "country": "Taiwan",
    "city": "Taipei"
  },
  "lines": ["Old Yin(6)", "Young Yang(7)", ...],
  "gua_name": "Qian",
  "gua_text": "Heaven moves vigorously...",
  "lang": "en"
}
```

### 2. AI 分析 API / AI Analysis API

**Endpoint:** `POST /api/ai-analysis`

**請求體 / Request Body:**
```json
{
  "question": "User's question",
  "gua_name": "Hexagram name",
  "gua_text": "Hexagram judgment",
  "yao_list": [...],
  "lang": "en"
}
```

## 語言切換 / Language Switching

### URL 路由 / URL Routes
- **中文版 / Chinese:** `/` 或 `/zh-TW`
- **英文版 / English:** `/en`

### 前端切換 / Frontend Switching
點擊頁面右上角的語言切換按鈕即可切換語言。<br>
Click the language switcher in the top-right corner to change languages.

## 技術架構 / Technology Stack

### 後端 / Backend
- **Flask** - Python Web 框架 / Web framework
- **Redis** - 數據快取 / Data caching
- **Requests** - HTTP 請求庫 / HTTP client library

### 前端 / Frontend
- **Vanilla JavaScript** - 原生 JS / Pure JavaScript
- **HTML5 Canvas** - 動畫渲染 / Animation rendering
- **CSS3** - 響應式設計 / Responsive design

### 部署 / Deployment
- **Docker** - 容器化 / Containerization
- **nginx** (可選 / Optional) - 反向代理 / Reverse proxy

## 開發指南 / Development Guide

### 新增語言 / Adding New Languages

1. **更新 `app.py`**
```python
SUPPORTED_LANGUAGES = {
    'zh-TW': '繁體中文',
    'en': 'English',
    'ja': '日本語'  # 新增日文
}
```

2. **添加卦象翻譯**
```python
gua_lookup_ja = {
    (0, 0): ("坤", "地勢坤..."),
    # 添加日文翻譯
}
```

3. **更新前端翻譯**
```javascript
const i18n = {
    'ja': {
        'divination_complete': '占い完了',
        // 添加日文翻譯
    }
};
```

### 自定義樣式 / Custom Styling

修改 `static/style.css` 中的變數來自定義外觀：<br>
Modify variables in `static/style.css` to customize appearance:

```css
:root {
  --primary-color: #ffe873;
  --background-color: #28251f;
  --text-color: #ead987;
}
```

## 貢獻 / Contributing

歡迎提交 Issue 和 Pull Request！<br>
Issues and Pull Requests are welcome!

### 開發流程 / Development Workflow

1. Fork 這個倉庫 / Fork this repository
2. 建立功能分支 / Create a feature branch
3. 提交改變 / Commit your changes
4. 推送分支 / Push to the branch
5. 建立 Pull Request / Create a Pull Request

## 許可證 / License

MIT License - 詳見 [LICENSE](LICENSE) 檔案。<br>
MIT License - See [LICENSE](LICENSE) file for details.

## 連絡方式 / Contact

- **GitHub:** [@yuzenchen](https://github.com/yuzenchen)
- **Email:** b97170098@gmail.com

---

**注意：此應用程式僅供娛樂和學習目的，不應作為重要決策的唯一依據。**<br>
**Note: This application is for entertainment and educational purposes only and should not be used as the sole basis for important decisions.**