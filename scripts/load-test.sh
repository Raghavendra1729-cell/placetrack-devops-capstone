#!/usr/bin/env bash
# Usage: scripts/load-test.sh <base-url> [seconds]   e.g. scripts/load-test.sh http://localhost:8080 60
base="${1:?base url}"; end=$((SECONDS + ${2:-60}))
while [ $SECONDS -lt $end ]; do
  curl -s -o /dev/null -H "Host: ${HOST_HEADER:-placetrack.local}" "$base/api/jobs" &
  curl -s -o /dev/null -H "Host: ${HOST_HEADER:-placetrack.local}" "$base/api/jobs/stats" &
  curl -s -o /dev/null -H "Host: ${HOST_HEADER:-placetrack.local}" "$base/api/jobs/9999" &
  wait; sleep 0.1
done
