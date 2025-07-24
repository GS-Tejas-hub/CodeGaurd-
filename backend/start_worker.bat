@echo off
cd %~dp0
call venv\Scripts\activate
celery -A worker.celery_app worker --loglevel=info -P solo
