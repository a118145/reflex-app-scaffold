#!/usr/bin/env bash
# Gate. Green = exit 0. Output stays short on purpose: it ends up in an agent's
# context, so only failures print detail (last 30 lines each).
#
#   scripts/check.sh          ruff check, ruff format --check, mypy, pytest
#   scripts/check.sh --full   + reflex compile with zero deprecation warnings
#
# --full needs the compiled frontend (.web/). In a fresh checkout or worktree
# the first compile reinstalls the frontend packages, so workers run the fast
# gate and the integration step runs --full in the main checkout.
set -uo pipefail
cd "$(dirname "$0")/.."
export REFLEX_TELEMETRY_ENABLED=false REFLEX_CHECK_LATEST_VERSION=false

full=0
[ "${1:-}" = "--full" ] && full=1
fail=0

step() {
  local name=$1 out
  shift
  if out=$("$@" 2>&1); then
    echo "ok   $name"
  else
    echo "FAIL $name"
    printf '%s\n' "$out" | tail -n 30
    fail=1
  fi
}

step "ruff check"  uv run --quiet ruff check --quiet .
step "ruff format" uv run --quiet ruff format --check --quiet .
step "mypy"        uv run --quiet mypy .
step "pytest"      uv run --quiet pytest -q --tb=short

if [ "$full" = 1 ]; then
  if ! out=$(uv run --quiet reflex compile --no-rich 2>&1); then
    echo "FAIL reflex compile"
    printf '%s\n' "$out" | tail -n 30
    fail=1
  elif grep -qi deprecat <<<"$out"; then
    echo "FAIL reflex compile: deprecation warnings (see docs/reflex-facts.md)"
    grep -i -A3 deprecat <<<"$out" | head -n 30
    fail=1
  else
    echo "ok   reflex compile"
  fi
fi

exit "$fail"
