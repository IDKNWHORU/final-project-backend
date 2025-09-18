#!/bin/bash

# 데이터베이스 마이그레이션을 적용합니다.
python manage.py migrate

# 정적 파일들을 한 곳으로 모읍니다.
python manage.py collectstatic --noinput

# ASGI 애플리케이션을 Uvicorn 워커를 사용하여 Gunicorn으로 실행합니다.
gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker
