#!/bin/bash
# (staging) Start the staging environment
docker compose -f docker-compose-staging.yml --project-name "war-crime-staging" up --build
