FROM python:3.11-slim

# Pythonの標準出力バッファを無効化（ログをリアルタイム表示するため）
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 依存ライブラリのインストール
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY . /app/

# 起動用エントリーポイントスクリプトの準備
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

# 本番用WSGI/ASGIサーバー（GunicornまたはDaphne）で起動
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]