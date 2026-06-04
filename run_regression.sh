#!/usr/bin/env bash
# Clean-slate Regression Harness (roadmap §8 / P0-S7) — the OIDA benchmark oracle.
#
# ONE command that, against the LIVE oida-core deploy: preflight -> Render RESET
# one-off job (clean slate) -> cold judge cache -> clean-ingest the 5 burned
# corpora -> worker drain -> 02 retrieve + 03..07 layer scorers -> a live
# micro-probe -> a timestamped Evidence Bundle under
# experiments/output/regression/<phase>-<ts>/.
#
# Flags (forwarded verbatim to the Python entrypoint):
#   --phase <id>            REQUIRED, e.g. P0-baseline
#   --corpora burned|fresh  default burned; fresh -> "not implemented" (Phase-4)
#   --env-file <path>       default: repo-root .env
#   --skip-reset            skip the Render RESET job (NOT a clean slate)
#
# This is a LIVE, costly run (real HTTP to oida-core + OpenAI + the Render API).
# Secrets are read from .env by the Python entrypoint and NEVER printed.
#
# Usage:
#   ./run_regression.sh --phase P0-baseline
#   ./run_regression.sh --phase P1-checkpoint --skip-reset
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

# Argument pre-parse: --phase is required; --corpora fresh fails fast here too so
# the wrapper does not even reach a live call when the mode is unsupported.
PHASE=""
CORPORA="burned"
args=("$@")
i=0
while [ $i -lt ${#args[@]} ]; do
  case "${args[$i]}" in
    --phase)
      i=$((i+1)); PHASE="${args[$i]:-}";;
    --phase=*)
      PHASE="${args[$i]#--phase=}";;
    --corpora)
      i=$((i+1)); CORPORA="${args[$i]:-}";;
    --corpora=*)
      CORPORA="${args[$i]#--corpora=}";;
  esac
  i=$((i+1))
done

if [ -z "$PHASE" ]; then
  echo "error: --phase <id> is required (e.g. --phase P0-baseline)" >&2
  exit 2
fi
if [ "$CORPORA" = "fresh" ]; then
  echo "error: --corpora fresh not implemented (Phase-4 fresh corpora are a separate, pre-registered run). Use --corpora burned." >&2
  exit 1
fi

exec python3 "${SCRIPT_DIR}/experiments/scripts/run_regression.py" "$@"
