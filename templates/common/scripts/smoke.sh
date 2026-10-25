#!/usr/bin/env bash
# Runtime smoke test: start the app, expect HTTP 200 on every static route in
# navigation/routes.py and on the backend's /ping, scan the log for
# tracebacks, stop the app. Green = exit 0.
#
# Binds the ports below. Run it in one place only (the main checkout at
# integration), never in parallel worktrees.
#
#   SMOKE_FRONTEND_PORT (3000)  SMOKE_BACKEND_PORT (8000)  SMOKE_TIMEOUT (240 s)
#
# A 200 proves the app compiles, both servers start and the routes are served.
# It does not prove a page renders correctly in a browser — look at it.
set -euo pipefail
cd "$(dirname "$0")/.."
export REFLEX_TELEMETRY_ENABLED=false REFLEX_CHECK_LATEST_VERSION=false

fport=${SMOKE_FRONTEND_PORT:-3000}
bport=${SMOKE_BACKEND_PORT:-8000}
timeout=${SMOKE_TIMEOUT:-240}

for p in "$fport" "$bport"; do
  if (exec 3<>"/dev/tcp/127.0.0.1/$p") 2>/dev/null; then
    echo "FAIL port $p is in use — stop the running app first"
    exit 2
  fi
done

if [ -d alembic ]; then
  # Quiet on success (alembic and SQLAlchemy warnings go to stderr), detail on
  # failure.
  if ! out=$(uv run --quiet reflex db migrate 2>&1); then
    echo "FAIL reflex db migrate"
    printf '%s\n' "$out" | tail -n 30
    exit 1
  fi
fi

routes=$(uv run --quiet python - <<'EOF'
import importlib

from reflex.config import get_config

mod = importlib.import_module(f"{get_config().app_name}.navigation.routes")
static = {
    v for k, v in vars(mod).items()
    if k.isupper() and isinstance(v, str) and v.startswith("/") and "[" not in v
}
print("\n".join(sorted(static)))
EOF
)

log=$(mktemp)
# Own process group (job control on for this one job), so cleanup reaches the
# frontend dev server and the backend workers, not just the reflex parent.
set -m
uv run --quiet reflex run --frontend-port "$fport" --backend-port "$bport" \
  --loglevel warning >"$log" 2>&1 &
pgid=$!
set +m
cleanup() {
  kill -TERM -- "-$pgid" 2>/dev/null || true
  sleep 2
  kill -KILL -- "-$pgid" 2>/dev/null || true
  rm -f "$log"
}
trap cleanup EXIT

code() { curl -s -o /dev/null -m 10 -w '%{http_code}' "$1" || true; }

deadline=$((SECONDS + timeout))
until [ "$(code "http://127.0.0.1:$bport/ping")" = 200 ] \
   && [ "$(code "http://127.0.0.1:$fport/")" = 200 ]; do
  if ! kill -0 "$pgid" 2>/dev/null; then
    echo "FAIL app exited during startup"
    tail -n 30 "$log"
    exit 1
  fi
  if [ "$SECONDS" -ge "$deadline" ]; then
    echo "FAIL app not up after ${timeout}s"
    tail -n 30 "$log"
    exit 1
  fi
  sleep 2
done

fail=0
while read -r route; do
  [ -n "$route" ] || continue
  c=$(code "http://127.0.0.1:$fport$route")
  if [ "$c" = 200 ]; then echo "ok   $route"; else echo "FAIL $route ($c)"; fail=1; fi
done <<<"$routes"

if grep -q "Traceback" "$log"; then
  echo "FAIL traceback in app log"
  grep -A 15 "Traceback" "$log" | head -n 30
  fail=1
fi
exit "$fail"
