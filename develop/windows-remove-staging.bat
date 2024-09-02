@echo off
REM (staging) Видалити розробницьке середовище (з видаленням volumes - база зникне)
docker compose -f docker-compose-staging.yml --project-name "war-crime-staging-site" down -v
pause
