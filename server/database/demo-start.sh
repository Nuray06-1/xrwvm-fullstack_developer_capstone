#!/bin/sh
set -eu
# Single-instance educational demo. Data is ephemeral across container replacement.
mongod --bind_ip 127.0.0.1 --port 27017 --dbpath /data/db --logpath /tmp/mongod.log &
mongo_pid=$!
trap 'kill "$mongo_pid" 2>/dev/null || true' EXIT INT TERM
attempt=0
until mongosh --quiet --eval 'db.adminCommand({ping:1}).ok' >/dev/null 2>&1; do
  attempt=$((attempt + 1))
  if [ "$attempt" -ge 30 ]; then cat /tmp/mongod.log; exit 1; fi
  sleep 1
done
node app.js &
api_pid=$!
trap 'kill "$api_pid" "$mongo_pid" 2>/dev/null || true' EXIT INT TERM
wait "$api_pid"
