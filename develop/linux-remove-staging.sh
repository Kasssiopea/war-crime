#!/bin/bash
# (staging) Remove the staging environment (with volumes removal - database will be gone)
docker compose -f docker-compose-staging.yml --project-name "war-crime-staging" down -v
