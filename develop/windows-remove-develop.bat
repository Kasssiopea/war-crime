@echo off
REM (develop) Видалити розробницьке середовище (з видаленням volumes - база зникне)
docker compose -f docker-compose-develop.yml --project-name "war-crime-develop-site" down -v
pause
