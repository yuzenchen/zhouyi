FROM python:3.10-slim

WORKDIR /app
COPY app.py import_redis_gua.py gua.json ./

RUN pip install flask redis
RUN pip install flask-cors
RUN pip install opencc-python-reimplemented

# 匯入 json 到 redis
CMD ["sh", "-c", "python import_redis_gua.py && python app.py"]

