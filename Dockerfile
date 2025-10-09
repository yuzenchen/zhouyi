# 使用 python 官方精簡映像
FROM python:3.10-slim

# 工作目錄
WORKDIR /app

# 複製依賴
COPY requirements.txt ./

# 安裝依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製所有程式碼
COPY . .

# 開放 Flask 運作的 port（預設 5000）
EXPOSE 8888

# 啟動服務
CMD ["python", "app.py"]
