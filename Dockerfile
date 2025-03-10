FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cloud Runは環境変数PORTを使用
ENV PORT=8080

# Cloud Run用のエントリーポイント
# app.main:appを指定して正しいモジュールを実行
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}