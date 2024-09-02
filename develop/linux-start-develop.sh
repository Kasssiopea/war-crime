#!/bin/bash
# (develop) Start the development environment
docker compose -f docker-compose-develop.yml --project-name "war-crime-develop" up --build
