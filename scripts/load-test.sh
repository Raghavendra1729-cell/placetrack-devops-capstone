#!/usr/bin/env bash
# Usage: scripts/load-test.sh <base-url> [seconds]   e.g. scripts/load-test.sh http://localhost:8080 60
# Only asks for jobs that exist, so the error panel in Grafana stays at zero.
base="${1:?base url}"; end=$((SECONDS + ${2:-60}))
host="Host: ${HOST_HEADER:-placetrack.local}"
get() { curl -s -o /dev/null -H "$host" "$base$1"; }

# real job ids from the list endpoint
read -r -a ids < <(curl -s -H "$host" "$base/api/jobs" | grep -o '"id":[0-9]*' | cut -d: -f2 | tr '\n' ' ')
[ ${#ids[@]} -gt 0 ] || { echo "no jobs found, add a few in the app first"; exit 1; }
echo "found ${#ids[@]} jobs, sending requests for ${2:-60}s"

while [ $SECONDS -lt $end ]; do
  get /api/jobs &
  get /api/jobs/stats &
  for _ in 1 2 3; do
    id=${ids[RANDOM % ${#ids[@]}]}
    get "/api/jobs/$id" &
  done
  wait; sleep 0.1
done
