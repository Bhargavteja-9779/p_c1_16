#!/usr/bin/env bash
# Snapshot project (excluding checkpoints/backups/data caches) to backups/, keep last 3.
cd "$(dirname "$0")/.." || exit 1
mkdir -p backups
tar --exclude=./checkpoints --exclude=./backups --exclude=./data --exclude=./.git -czf "backups/project_snapshot_$(date +%Y%m%d_%H%M%S).tar.gz" .
ls -1t backups/project_snapshot_*.tar.gz | tail -n +4 | xargs -r rm -f
