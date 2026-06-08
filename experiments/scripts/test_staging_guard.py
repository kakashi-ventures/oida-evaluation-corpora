#!/usr/bin/env python3
"""test_staging_guard — fail-closed prod guard + os.environ routing precedence.

Verification hook for the STEP-1 harness routing fix (D5 MUST #1 prerequisite;
root cause in ../../oida-core/doc/findings/edge-freeze-step1-live-demo.md §3/§5).
Proves, with NO live calls:
  (1) `_load_env` PREFERS os.environ over the .env file — the override path that
      lets `--target staging` route the spawned subprocesses.
  (2) `staging_write_blocked()` flags a staging run whose write resolves off-staging.
  (3) `_assert_staging_write_target()` ABORTS (exit EXIT_STAGING_MISROUTE) BEFORE
      any write when `--target staging` would resolve to prod, and PASSES when it
      correctly resolves to staging — i.e. a `--target staging` run can NEVER
      write to prod, even under a future routing regression.

Stdlib only. Run: `python experiments/scripts/test_staging_guard.py` (exit 0 = all pass).
"""
import os
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "experiments"))
sys.path.insert(0, str(REPO_ROOT / "experiments" / "scripts"))

from adapters.oida import _load_env  # noqa: E402
import run_regression as rr  # noqa: E402

PROD = "https://oida-core.onrender.com"
STAGE = "https://oida-core-staging.onrender.com"
failures: list[str] = []


def check(name: str, cond: bool) -> None:
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        failures.append(name)


def _write_env(base_url: str) -> str:
    f = tempfile.NamedTemporaryFile("w", suffix=".env", delete=False)
    f.write(f"OIDA_CORE_BASE_URL={base_url}\n")
    f.write("OIDA_CORE_ADMIN_KEY=test-admin-key\n")
    f.write(f"OIDA_CORE_BASE_URL_STAGING={STAGE}\n")
    f.close()
    return f.name


def _clear() -> None:
    for k in ("OIDA_CORE_BASE_URL", "OIDA_CORE_ADMIN_KEY"):
        os.environ.pop(k, None)


def main() -> int:
    envf = _write_env(PROD)

    print("== 1. _load_env prefers os.environ over the .env file ==")
    _clear()
    check("file value used when env unset", _load_env(Path(envf)).get("OIDA_CORE_BASE_URL") == PROD)
    os.environ["OIDA_CORE_BASE_URL"] = STAGE
    check("os.environ overrides the file", _load_env(Path(envf)).get("OIDA_CORE_BASE_URL") == STAGE)
    _clear()

    print("== 2. staging_write_blocked() predicate ==")
    check("staging + resolved=prod  -> blocked", rr.staging_write_blocked("staging", STAGE, PROD) is True)
    check("staging + resolved=stage -> ok", rr.staging_write_blocked("staging", STAGE, STAGE + "/") is False)
    check("prod target -> not blocked (guarded by _prod_reset_blocked)",
          rr.staging_write_blocked("prod", STAGE, PROD) is False)

    print("== 3. _assert_staging_write_target() fail-closed ==")
    # (a) MISROUTE: env points at prod, no os.environ override -> resolves prod -> ABORT.
    _clear()
    aborted = False
    try:
        rr._assert_staging_write_target("staging", envf, "INGEST(test-misroute)")
    except SystemExit as e:
        aborted = (e.code == rr.EXIT_STAGING_MISROUTE)
    check("misrouted staging write ABORTS before write (exit EXIT_STAGING_MISROUTE)", aborted)

    # (b) CORRECT route: os.environ override -> resolves staging -> PASS (no exit).
    os.environ["OIDA_CORE_BASE_URL"] = STAGE
    passed = True
    try:
        rr._assert_staging_write_target("staging", envf, "INGEST(test-ok)")
    except SystemExit:
        passed = False
    check("correctly-routed staging write PASSES", passed)
    _clear()

    # (c) prod target is never staging-guarded here.
    not_guarded = True
    try:
        rr._assert_staging_write_target("prod", envf, "INGEST(prod)")
    except SystemExit:
        not_guarded = False
    check("prod target not staging-guarded here", not_guarded)

    os.unlink(envf)
    print(f"\n{'ALL PASS' if not failures else 'FAILURES: ' + ', '.join(failures)}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
