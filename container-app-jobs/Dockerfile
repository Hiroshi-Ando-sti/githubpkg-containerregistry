# ベースとなる公式のPythonイメージを指定 (slimバージョンは軽量でおすすめ)
FROM python:3.12-slim

# アプリケーションのコードを配置する作業ディレクトリを設定
WORKDIR /app

# 1. 依存関係ファイルを先にコピー
COPY requirements.txt .

# 2. 依存関係をインストール (キャッシュを活用してビルドを高速化)
RUN pip install --no-cache-dir -r requirements.txt

# 3. アプリケーションのソースコードをコピー
COPY . .

# アプリケーションを実行するユーザーを作成（セキュリティ向上のため）
RUN useradd --create-home --shell /bin/bash app

# アプリケーションファイルの所有者を変更
RUN chown -R app:app /app

# 非rootユーザーに切り替え
USER app

# アプリケーションを実行
CMD ["python", "app.py"]
