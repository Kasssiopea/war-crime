@echo off
REM (develop) Запустити розробницьке середовище
docker compose -f docker-compose-develop.yml --project-name "war-crime-develop-site" up --build
pause
