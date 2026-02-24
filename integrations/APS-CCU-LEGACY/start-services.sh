#!/bin/bash
docker-compose -f docker-compose-prod.yml up -d --force-recreate --renew-anon-volumes --remove-orphans
