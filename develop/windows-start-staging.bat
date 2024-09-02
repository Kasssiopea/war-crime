@echo off
REM (staging) Запустити розробницьке середовище
docker compose -f docker-compose-staging.yml --project-name "war-crime-staging-site" up --build
pause