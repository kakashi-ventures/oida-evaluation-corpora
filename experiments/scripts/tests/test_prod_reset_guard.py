#!/usr/bin/env python3
"""Stdlib unittest for the PRODUCTION-reset guard in run_regression.py.

Falsification contract for the guard under test
-----------------------------------------------
* What it measures: whether an invocation of `run_regression.main` would fire a
  RESET (wipe + re-ingest) against PRODUCTION oida-core without an explicit
  opt-in. Computed by the pure predicate `_prod_reset_blocked(target,
  skip_reset, allow_prod_reset)`.
* How computed: blocked iff target == "prod" AND not skip_reset AND not
  allow_prod_reset. No I/O, no env, no network.
* Where the behavior changes: `main()` evaluates the predicate AFTER argparse
  and the `--corpora fresh` check, but BEFORE `_load_env` (and therefore before
  any Render API call, preflight, or reset_bench). On block it prints a
  fail-closed refusal to stderr and returns EXIT_PROD_RESET_BLOCKED (7).
* This test proves the three required paths with ZERO network and ZERO real
  RESET:
    1. The predicate truth table (pure).
    2. main() control flow: a prod default aborts before `_load_env` (sentinel
       never raised; preflight/reset_bench never called); `--target staging` and
       prod + `--allow-prod-reset` proceed past the guard (sentinel raised).

The control-flow test monkeypatches `run_regression._load_env` (the first call
AFTER the guard) to raise a sentinel, and `run_regression.preflight` /
`run_regression.reset_bench` to fail if ever reached. Reaching the sentinel
proves "proceeded past the guard"; never reaching it proves "aborted at the
guard before any network call".
"""
from __future__ import annotations

import contextlib
import io
import sys
import unittest
from pathlib import Path

# Make the module dir (experiments/scripts) importable. run_regression's own
# sys.path.insert (its lines ~54-55) wires up adapters.oida / eval_common once
# imported.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import run_regression  # noqa: E402


class _PastGuard(Exception):
    """Sentinel: raised by the patched _load_env to prove the guard was passed."""


class TestProdResetPredicate(unittest.TestCase):
    """Pure truth table — no I/O, no network."""

    def test_prod_no_flag_is_blocked(self):
        self.assertIs(
            run_regression._prod_reset_blocked("prod", False, False), True
        )

    def test_staging_is_allowed(self):
        self.assertIs(
            run_regression._prod_reset_blocked("staging", False, False), False
        )

    def test_prod_with_allow_flag_is_allowed(self):
        self.assertIs(
            run_regression._prod_reset_blocked("prod", False, True), False
        )

    def test_prod_with_skip_reset_is_allowed(self):
        self.assertIs(
            run_regression._prod_reset_blocked("prod", True, False), False
        )


class TestProdResetGuardControlFlow(unittest.TestCase):
    """main() control-flow proof — network-free via monkeypatching.

    _load_env is the first call after the guard; patching it to raise a sentinel
    lets us assert "proceeded past the guard" without any Render API call.
    preflight/reset_bench are patched to explode if ever reached, proving the
    abort happens before any RESET machinery.
    """

    def setUp(self):
        self._orig_load_env = run_regression._load_env
        self._orig_preflight = run_regression.preflight
        self._orig_reset_bench = run_regression.reset_bench

        def _sentinel_load_env(*_args, **_kwargs):
            raise _PastGuard()

        def _must_not_run(*_args, **_kwargs):
            raise AssertionError("must not be reached")

        run_regression._load_env = _sentinel_load_env
        run_regression.preflight = _must_not_run
        run_regression.reset_bench = _must_not_run

    def tearDown(self):
        run_regression._load_env = self._orig_load_env
        run_regression.preflight = self._orig_preflight
        run_regression.reset_bench = self._orig_reset_bench

    def test_prod_default_aborts_before_load_env(self):
        # prod (no --skip-reset, no --allow-prod-reset): blocked. The sentinel
        # _load_env must NEVER raise (abort happens before it), and the return
        # code is EXIT_PROD_RESET_BLOCKED.
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            rc = run_regression.main(["--phase", "guard-test", "--target", "prod"])
        self.assertEqual(rc, run_regression.EXIT_PROD_RESET_BLOCKED)
        self.assertIn("refusing to fire a RESET against PRODUCTION", err.getvalue())

    def test_staging_proceeds_past_guard(self):
        # staging is never blocked: must reach the patched _load_env sentinel.
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            with self.assertRaises(_PastGuard):
                run_regression.main(
                    ["--phase", "guard-test", "--target", "staging"]
                )

    def test_prod_with_allow_flag_proceeds_past_guard(self):
        # prod + explicit opt-in is never blocked: must reach the sentinel.
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            with self.assertRaises(_PastGuard):
                run_regression.main(
                    [
                        "--phase",
                        "guard-test",
                        "--target",
                        "prod",
                        "--allow-prod-reset",
                    ]
                )


if __name__ == "__main__":
    unittest.main()
