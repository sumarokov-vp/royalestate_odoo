#!/usr/bin/env fish
podman-compose -f build/compose.yaml build
podman push docker.io/sumarokovvp/simplelogic:royal_estate_arm
podman-compose -f podman/compose.yaml down
podman-compose -f podman/compose.yaml up -d
ssh royal_estate_odoo 'cd /opt/odoo/ && docker compose pull && docker compose down && docker compose up -d'
