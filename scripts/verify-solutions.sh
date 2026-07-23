#!/usr/bin/env bash
# Verify that every exercise solution actually passes its tests.
#
# For each module with exercises/solutions/, the whole module is copied to a
# temp dir INSIDE the repo (so pyproject.toml's pytest config — asyncio mode,
# markers — applies), the solutions are overlaid onto the stubs, and pytest
# runs against the result. CI runs this on every PR: an exercise whose tests
# can't pass is a broken promise to the learner (≈ a kata with a failing
# reference implementation).
set -euo pipefail
cd "$(dirname "$0")/.."

TMP=".solution-check"
trap 'rm -rf "$TMP"' EXIT

failed=0
for sol_dir in */exercises/solutions; do
  module="${sol_dir%%/*}"
  work="$TMP/$module"
  mkdir -p "$work"
  cp -r "$module" "$work/"
  find "$work/$module" -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true
  for sol in "$work/$module/exercises/solutions"/*.py; do
    cp "$sol" "$work/$module/exercises/$(basename "$sol")"
  done
  echo "=== $module ==="
  if ! uv run pytest "$work/$module/exercises" -q -p no:cacheprovider; then
    failed=1
  fi
done

rm -rf "$TMP"
trap - EXIT

if [ "$failed" -eq 0 ]; then
  echo "ALL EXERCISE SOLUTIONS PASS"
else
  echo "SOME EXERCISE SOLUTIONS FAIL — see output above"
  exit 1
fi
