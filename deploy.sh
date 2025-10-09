#!/bin/bash

APP_NAME="zhouyi-flask"
PORT=888

echo "開始建置 Docker 映像檔…"
docker build -t $APP_NAME .

if [ $? -ne 0 ]; then
    echo "Docker build 失敗，請檢查錯誤訊息！"
    exit 1
fi

echo "結束建置，準備啟動容器…"
# 停止同名容器（若存在）
if docker ps -a --format '{{.Names}}' | grep -Eq "^${APP_NAME}$"; then
    docker stop $APP_NAME
    docker rm $APP_NAME
fi

docker run -d --name $APP_NAME -p $PORT:888 $APP_NAME

if [ $? -eq 0 ]; then
    echo "啟動容器完成"
    sleep 3
    curl http://localhost:${PORT} -I
else
    echo "Docker run 失敗，請檢查錯誤訊息！"
    exit 1
fi

echo "開始清理舊的 Docker 映像檔…"
# 列出所有同 APP_NAME 標籤的映像檔，保留最新一個
docker images -f "dangling=true" -q | xargs -r docker rmi
OLD_IMAGES=$(docker images $APP_NAME --format "{{.ID}}" | tail -n +2)
if [ ! -z "$OLD_IMAGES" ]; then
    docker rmi $OLD_IMAGES
    echo "已刪除舊的 Docker 映像檔。"
else
    echo "沒有需要刪除的舊映像檔。"
fi

