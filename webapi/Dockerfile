# ベースとなる公式のPythonイメージを指定 (slimバージョンは軽量でおすすめ)
FROM python:3.11-slim

# アプリケーションのコードを配置する作業ディレクトリを設定
WORKDIR /app

# 1. 依存関係ファイルを先にコピー
COPY requirements.txt .

# 2. 依存関係をインストール (キャッシュを活用してビルドを高速化)
RUN pip install --no-cache-dir -r requirements.txt

# 3. アプリケーションのソースコードをコピー
COPY . .

# アプリケーションがリッスンするポートをコンテナに公開
EXPOSE 8000

# コンテナ起動時にGunicornサーバーを実行するコマンド
# 0.0.0.0:8000 でリクエストを待ち受け、app.py内の'app'インスタンスを起動
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]