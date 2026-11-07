#!/bin/sh

# エラーが発生したら即停止
set -e

# DBのマイグレーション実行（未適用分があれば適用、なければスキップ）
echo "Running database migrations..."
python manage.py migrate --noinput

# 静的ファイルの集約（Nginxから配信するための準備）
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Dockerfileの CMD で指定したコマンド（Gunicorn起動）を実行
exec "$@"