#!/bin/bash
# (develop) Remove the development environment (with volumes removal - database will be gone)
docker compose -f docker-compose-develop.yml --project-name "war-crime-develop" down -v
