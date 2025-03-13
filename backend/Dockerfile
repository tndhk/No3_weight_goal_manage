FROM python:3.11-slim

WORKDIR /app

# 必要なパッケージをインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# SQLite用のディレクトリを作成し、確実に権限を設定
RUN mkdir -p /app/instance && chmod 777 /app/instance

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]