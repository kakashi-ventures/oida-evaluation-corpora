#!/usr/bin/env python3
"""Clean-slate Regression Harness (roadmap §8) — the OIDA benchmark oracle.

ONE command that, against the LIVE oida-core deploy:

  PREFLIGHT  — fail-fast (exit 2) sanity: /health==200, Render API reachable +
               service id resolved, required .env keys present (presence only,
               never printed), per-corpus routing resolves for all 5 corpora.
  RESET      — fire a Render one-off job that wipes the 5 bench projects' KOs
               (RESET_BENCH_KOS=1 npx tsx scripts/seed-bench-projects.ts), poll
               to terminal, fetch logs, capture the "deleted N KOs" line, and
               ENFORCE the exposed-key abort (see below).
  CACHE COLD — delete the judge cache + local oida-core ingest reports so the
               clean ingest + judge start empty (belt-and-suspenders with the
               P0-S7 cache re-key).
  INGEST     — clean-ingest the 5 corpora into oida-core ONLY (baselines NOT
               re-run); assert every doc committed + kos_created>0.
  DRAIN      — bounded settle-wait then re-assert /health (cosmetic for P0;
               cross-document edges arrive in Phase 1).
  RETRIEVE+  — 02 retrieve + 03..07 layer scorers under one RUN_ID; 05 dry-run
  LAYERS       (headline (b) is judge-free).
  MICRO-PROBE— a single live judged corpus (clearpath) to prove CONTRADICTS is
               reachable post P0-S3/S4 + the cache re-key (cost ~cents).
  BUNDLE     — emit the timestamped Evidence Bundle (§9) under
               experiments/output/regression/<phase>-<ts>/.

Burned-corpora bundles are REGRESSION / SANITY signal only — never an OIDA
pass/fail claim (that lives in the Phase-4 fresh corpora). The ±0.005 NDCG@10
sanity check is HARNESS VALIDATION (engine unchanged), not a performance claim.

ABSOLUTE GUARDRAIL: secrets (RENDER_API_KEY, OPENAI_API_KEY, OIDA_CORE_* keys)
are read from .env into locals and NEVER printed/echoed/committed. The committed
bundle contains ZERO secrets.

stdlib only. Usage is via run_regression.sh (which forwards argv here).
"""
from __future__ import annotations

import argparse
import json
import shutil
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib import error as urlerror
from urllib import request as urlrequest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / "experiments" / "scripts"
OUTPUT = REPO_ROOT / "experiments" / "output"
sys.path.insert(0, str(REPO_ROOT / "experiments"))
sys.path.insert(0, str(SCRIPTS))

# Adapter seams (the routing + env loader live in the adapter, single source).
from adapters.oida import (  # noqa: E402
    OIDA_CORE_PROJECT_IDS,
    _load_env,
    resolve_corpus_routing,
)
import eval_common as ec  # noqa: E402

# ---------------------------------------------------------------------------
# constants
# ---------------------------------------------------------------------------

RENDER_API = "https://api.render.com/v1"
# The oida-core Render service. Resolved by name match in PREFLIGHT; the .env may
# override via OIDA_CORE_RENDER_SERVICE_ID. This default is the known service id.
DEFAULT_OIDA_CORE_SERVICE_ID = "srv-d881ojr7uimc73b1berg"
OIDA_CORE_SERVICE_NAME = "oida-core"
# The managed Postgres backing oida-core. Recorded READ-ONLY into the bundle so
# the run documents its infrastructure conditions (the lesson of the 2026-06-03
# outage). The .env may override via OIDA_CORE_RENDER_DB_ID.
DEFAULT_OIDA_CORE_DB_ID = "dpg-d881lq1kh4rs73c92a50-a"

# --target staging — the Option-2 verification substrate (oida-core-staging, KVA,
# built 2026-06-04). Selecting it injects these through the existing
# OIDA_CORE_RENDER_* / OIDA_CORE_BASE_URL override plumbing below; prod is the
# default and is left untouched. .env may override per-target via
# OIDA_CORE_{BASE_URL,RENDER_SERVICE_ID,RENDER_DB_ID}_STAGING.
STAGING_BASE_URL = "https://oida-core-staging.onrender.com"
STAGING_SERVICE_ID = "srv-d8glh4n7f7vs73etcbs0"
STAGING_DB_ID = "dpg-d8glgo8g4nts739pvjl0-a"

# RESET one-off job command (runs inside Render where DATABASE_URL is reachable).
RESET_START_COMMAND = "RESET_BENCH_KOS=1 npx tsx scripts/seed-bench-projects.ts"

# The seed script prints exactly this when NO new plaintext was minted (all bench
# keys already existed) — the only SAFE outcome for a regression run.
SAFE_NO_MINT_MARKER = "# All bench keys already existed; no new plaintext minted."
# If instead a key was missing, the seed prints lines like
# "OIDA_CORE_KEY_CLEARPATH=adb_sk_..." (a RANDOM key, now leaked to job logs).
MINTED_KEY_PREFIX = "OIDA_CORE_KEY_"
RESET_LINE_MARKER = "# RESET_BENCH_KOS:"

REQUIRED_ENV_KEYS = [
    "OPENAI_API_KEY",
    "OIDA_CORE_BASE_URL",
    "OIDA_CORE_ADMIN_KEY",
    "RENDER_API_KEY",
    "OIDA_CORE_KEY_SECRET",
    "OIDA_CORE_KEY_CLEARPATH",
    "OIDA_CORE_KEY_FIREGLASS",
    "OIDA_CORE_KEY_VERTEXMINDS",
    "OIDA_CORE_KEY_REDHOOD",
    "OIDA_CORE_KEY_ASHFORD",
]

SYSTEM = "oida-core"
ALL_CORPORA = list(OIDA_CORE_PROJECT_IDS.keys())  # the canonical 5, ordered
MICRO_PROBE_CORPUS = "org-consulting-clearpath"

NDCG10_TOLERANCE = 0.005

EXIT_PREFLIGHT = 2
EXIT_RESET_FAILED = 3
EXIT_EXPOSED_KEY = 4
EXIT_INGEST = 5
EXIT_LAYER = 6
EXIT_PROD_RESET_BLOCKED = 7


# ---------------------------------------------------------------------------
# tiny HTTP helpers (stdlib) — secrets passed as args, never logged
# ---------------------------------------------------------------------------


def _http(method: str, url: str, headers: dict | None = None,
          body: bytes | None = None, timeout: float = 60.0) -> tuple[int, str]:
    """Return (status_code, raw_text). Never raises on HTTP error status."""
    req = urlrequest.Request(url, data=body, headers=headers or {}, method=method)
    try:
        with urlrequest.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urlerror.HTTPError as e:
        raw = e.read().decode("utf-8", "replace") if e.fp else ""
        return e.code, raw
    except (TimeoutError, urlerror.URLError, ConnectionError, OSError) as e:
        return 0, f"{type(e).__name__}: {str(e)[:200]}"


def _render_headers(render_key: str) -> dict:
    return {
        "Authorization": f"Bearer {render_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def fetch_db_infra(db_id: str, render_key: str) -> dict:
    """READ-ONLY snapshot of the managed Postgres backing oida-core, recorded into
    the bundle so the run documents its infrastructure conditions.

    Falsification contract (DB-infra snapshot):
      MEASURES: the live Render Postgres object's status / plan / diskSizeGB /
        region / version / suspended — the conditions under which THIS run
        executed (the lesson of the 2026-06-03 disk-full outage: a bundle must
        say what infra it ran against).
      HOW: a single GET https://api.render.com/v1/postgres/<db_id> with the
        Bearer RENDER_API_KEY (NEVER printed). Pure read; no Render mutation.
        Tolerates both the bare-object and {"postgres": {...}} response shapes.
      WHERE: serialized into harness_health.md ("## DB infrastructure") and
        run_manifest.json (reset_rep is separate; this is its own block).
      WHAT CHANGES: nothing — informational. It does NOT gate the run (the
        DB-reachability PREFLIGHT probe is the gate); a fetch failure is recorded
        as fetch_ok=false and the harness proceeds (the probe already passed)."""
    out: dict = {"db_id": db_id, "endpoint": f"{RENDER_API}/postgres/{db_id}"}
    st, raw = _http("GET", f"{RENDER_API}/postgres/{db_id}",
                    headers=_render_headers(render_key), timeout=30)
    out["http_status"] = st
    out["fetch_ok"] = st == 200
    if st != 200:
        out["error"] = f"GET /v1/postgres/{db_id} -> {st}"
        return out
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        out["fetch_ok"] = False
        out["error"] = "non-JSON response"
        return out
    # single-GET returns the object directly; be defensive about a wrapper too.
    pg = data.get("postgres", data) if isinstance(data, dict) else {}
    for fld in ("status", "plan", "diskSizeGB", "name", "region", "version",
                "suspended"):
        out[fld] = pg.get(fld)
    return out


# ---------------------------------------------------------------------------
# subprocess runner for the numbered scripts — streams + captures
# ---------------------------------------------------------------------------


def _run_script(script: str, args: list[str], log_lines: list[str],
                check: bool = True) -> tuple[int, str]:
    """Run `python experiments/scripts/<script> <args>`; tee output to stdout +
    return (rc, captured_text). On check + nonzero rc the caller decides to abort."""
    cmd = [sys.executable, str(SCRIPTS / script), *args]
    pretty = "python experiments/scripts/" + script + " " + " ".join(args)
    print(f"\n>>> {pretty}")
    log_lines.append(f"$ {pretty}")
    proc = subprocess.Popen(cmd, cwd=str(REPO_ROOT), stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True, bufsize=1)
    out: list[str] = []
    assert proc.stdout is not None
    for line in proc.stdout:
        sys.stdout.write(line)
        out.append(line.rstrip("\n"))
    rc = proc.wait()
    captured = "\n".join(out)
    log_lines.append(captured)
    log_lines.append(f"# rc={rc}")
    if check and rc != 0:
        print(f"!!! {script} exited rc={rc}")
    return rc, captured


# ---------------------------------------------------------------------------
# PREFLIGHT
# ---------------------------------------------------------------------------


def preflight(env: dict, base_url: str, render_key: str) -> dict:
    """Fail-fast sanity. Returns {service_id, health_ok, render_ok, ...} or exits 2."""
    print("\n===================== PREFLIGHT =====================")
    rep: dict = {"checks": []}

    def _ok(name: str, passed: bool, detail: str = "") -> None:
        rep["checks"].append({"check": name, "passed": passed, "detail": detail})
        print(f"  [{'OK ' if passed else 'FAIL'}] {name}{(' — ' + detail) if detail else ''}")

    # 1) /health == 200
    health_url = base_url.rstrip("/") + "/health"
    st, _ = _http("GET", health_url, timeout=30)
    _ok("oida-core /health == 200", st == 200, f"GET {health_url} -> {st}")

    # 2) Render API reachable + service id resolved (name match, .env override).
    override = env.get("OIDA_CORE_RENDER_SERVICE_ID", "").strip()
    svc_st, svc_raw = _http("GET", f"{RENDER_API}/services?limit=100",
                            headers=_render_headers(render_key), timeout=45)
    render_reachable = svc_st == 200
    _ok("Render API reachable (GET /v1/services == 200)", render_reachable,
        f"-> {svc_st}")
    resolved_id = None
    name_matches: list[str] = []
    if render_reachable:
        try:
            services = json.loads(svc_raw)
            for item in services:
                svc = item.get("service", item) if isinstance(item, dict) else {}
                sid = svc.get("id")
                sname = svc.get("name")
                if sname == OIDA_CORE_SERVICE_NAME and sid:
                    name_matches.append(sid)
        except (json.JSONDecodeError, AttributeError, TypeError):
            name_matches = []
    if override:
        resolved_id = override
        detail = f"using .env OIDA_CORE_RENDER_SERVICE_ID override = {override}"
    elif DEFAULT_OIDA_CORE_SERVICE_ID in name_matches:
        resolved_id = DEFAULT_OIDA_CORE_SERVICE_ID
        detail = f"name match confirms default {DEFAULT_OIDA_CORE_SERVICE_ID}"
    elif name_matches:
        resolved_id = name_matches[0]
        detail = f"name match -> {resolved_id} (expected default {DEFAULT_OIDA_CORE_SERVICE_ID})"
    else:
        # Fall back to the known default but flag that the name match did not
        # confirm it (still proceed — the RESET job will fail loudly if wrong).
        resolved_id = DEFAULT_OIDA_CORE_SERVICE_ID
        detail = f"no name match; falling back to default {DEFAULT_OIDA_CORE_SERVICE_ID}"
    _ok(f"resolve oida-core service id ({OIDA_CORE_SERVICE_NAME})",
        resolved_id is not None, detail)
    rep["service_id"] = resolved_id

    # 3) required env keys present (presence only — values NEVER printed).
    missing = [k for k in REQUIRED_ENV_KEYS if not env.get(k)]
    _ok("required .env keys present (presence-only)", not missing,
        ("all present" if not missing else f"MISSING: {missing}"))

    # 4) per-corpus routing resolves for all 5 (uses the adapter seam).
    routing_ok = True
    routing_detail = []
    for corpus in ALL_CORPORA:
        try:
            project_id, _key = resolve_corpus_routing(SYSTEM, corpus, env)
            routing_detail.append(f"{corpus}->{project_id}")
        except (ValueError, RuntimeError) as e:
            routing_ok = False
            routing_detail.append(f"{corpus}: {e}")
    _ok("per-corpus routing resolves (all 5)", routing_ok,
        "; ".join(routing_detail) if not routing_ok else "5/5 resolved")

    # 5) DB-reachability probe: one AUTHENTICATED retrieve. THE LESSON of the
    #    2026-06-03 outage: the unauthenticated /health (check 1) returns 200 even
    #    when the Postgres backing oida-core is down, so /health ALONE is proven
    #    insufficient. Both the auth middleware (prisma.apiKey.findUnique) and the
    #    retrieve read need the DB, so a single authenticated retrieve exercises
    #    the exact dependency a doomed RESET job would hit. Probe it HERE so we
    #    FAIL FAST (exit 2) BEFORE firing a RESET job that, against a down /
    #    disk-full DB, PANICs at the first write.
    #
    #    Falsification contract (this probe):
    #      MEASURES: is the oida-core Postgres reachable for an authenticated
    #        request right now? (boolean, recorded in the preflight report).
    #      HOW: issue ONE real `OidaClient.retrieve` with a per-corpus bench key,
    #        mirroring 02_retrieve's calling convention exactly (key as admin_key,
    #        projectId in body, short corpus slug). Map the outcome:
    #          - HTTP 200 -> DB reachable (read path + auth lookup both worked).
    #          - notes contains AUTH_BACKEND_UNAVAILABLE -> auth prisma lookup threw
    #            (DB down; the 503 the auth middleware returns on a DB fault). HARD STOP.
    #          - notes contains NETWORK_ERROR / a bare retrieve_error -> the service
    #            or its DB is unreachable. HARD STOP.
    #          - notes contains MISSING_AUTH / INVALID_KEY -> NOT a DB outage but a
    #            key/auth misconfig; still a HARD STOP (never mutate on a bad config),
    #            classified distinctly so the operator fixes the right thing.
    #      WHERE: stored in preflight_rep["checks"] (-> run_manifest.json) and echoed.
    #      WHAT CHANGES: a non-reachable DB sets all_passed False -> sys.exit(2)
    #        before RESET/ingest. No mutation, no bundle. (Read-only probe.)
    db_ok = True
    db_detail = ""
    if routing_ok:
        try:
            from adapters.oida import OidaClient  # noqa: E402
            project_id, key = resolve_corpus_routing(SYSTEM, ALL_CORPORA[0], env)
            probe = OidaClient(admin_key=key, base_url=base_url, timeout_sec=45)
            res = probe.retrieve("regression preflight db probe",
                                 project_id=project_id, top_k=1,
                                 corpus_slug=ALL_CORPORA[0].split("-", 1)[-1])
            note = res.notes or ""
            # A reachable DB returns a normal (possibly empty) v0 result; the
            # adapter only sets a "retrieve_error: ..." note on a non-200 / error
            # response, JSON-dumping the oida-core error code into the note.
            if "AUTH_BACKEND_UNAVAILABLE" in note:
                db_ok = False
                db_detail = ("DB DOWN — auth backend unavailable (503): the auth "
                             f"middleware's prisma lookup threw. {note[:140]}")
            elif "NETWORK_ERROR" in note:
                db_ok = False
                db_detail = ("service/DB UNREACHABLE — network error after retries. "
                             f"{note[:140]}")
            elif "MISSING_AUTH" in note or "INVALID_KEY" in note:
                # Not a DB outage, but a bad config — still never mutate on it.
                db_ok = False
                db_detail = ("AUTH MISCONFIG (not a DB outage) — fix the bench key, "
                             f"not the DB. {note[:140]}")
            elif "retrieve_error" in note:
                db_ok = False
                db_detail = f"retrieve failed (treat as backend unavailable): {note[:140]}"
            else:
                db_detail = f"authenticated retrieve OK (DB reachable): {note[:120]}"
        except Exception as e:  # noqa: BLE001 — any failure here is a hard stop
            db_ok = False
            db_detail = f"{type(e).__name__}: {str(e)[:160]}"
    else:
        db_ok = False
        db_detail = "skipped (routing failed)"
    _ok("oida-core DB reachable (authenticated retrieve probe — /health is NOT enough)",
        db_ok, db_detail)

    rep["all_passed"] = all(c["passed"] for c in rep["checks"])
    if not rep["all_passed"]:
        print("\nPREFLIGHT FAILED — aborting before any live mutation. exit 2")
        sys.exit(EXIT_PREFLIGHT)
    print("\nPREFLIGHT OK")
    return rep


# ---------------------------------------------------------------------------
# RESET (Render one-off job) + exposed-key abort
# ---------------------------------------------------------------------------


def _fetch_job_logs(service_id: str, job_id: str, render_key: str,
                    owner_id: str | None) -> tuple[str, str]:
    """Best-effort job-log fetch from GET /v1/logs (needs ownerId + resource).

    A Render one-off job streams its STDOUT under ``resource=<job_id>`` (NOT the
    parent service id — verified live 2026-06-03; querying the service resource
    returns only the web service's app logs). Logs can lag a few seconds after
    the job goes terminal, so we poll until a marker line appears (or attempts
    exhaust). We also try the service resource as a fallback. Returns
    (log_text, source_endpoint); empty text means logs were not retrievable (the
    caller then fails CLOSED on the safe-mint gate)."""
    attempts: list[str] = []
    hdrs = _render_headers(render_key)
    best_text = ""
    if owner_id:
        # Primary: the JOB's own log stream; fallback: the parent service stream.
        for resource, tag in ((job_id, "job"), (service_id, "service")):
            q = f"{RENDER_API}/logs?ownerId={owner_id}&resource={resource}&limit=500"
            for poll in range(8):
                st, raw = _http("GET", q, headers=hdrs, timeout=45)
                if poll == 0:
                    attempts.append(f"GET /v1/logs?resource={resource} -> {st}")
                if st == 200 and raw.strip():
                    text = _extract_log_text(raw)
                    if len(text) > len(best_text):
                        best_text = text
                    # stop early once we have a decisive marker (safe / reset /
                    # minted-key / a fatal infra error from the seed run).
                    if (SAFE_NO_MINT_MARKER in text
                            or RESET_LINE_MARKER in text
                            or "No space left on device" in text
                            or "prisma:error" in text
                            or any(ln.strip().startswith(MINTED_KEY_PREFIX)
                                   and "=adb_sk_" in ln for ln in text.splitlines())):
                        return text, f"/v1/logs?resource={resource}"
                time.sleep(8)
            if best_text:
                break
        if best_text:
            return best_text, "/v1/logs (no decisive marker in window)"
    return best_text, " | ".join(attempts)


def _extract_log_text(raw: str) -> str:
    """Pull plain log lines out of whatever JSON shape Render returns."""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return raw  # already plain text
    lines: list[str] = []

    def _walk(node):
        if isinstance(node, dict):
            for key in ("message", "text", "log", "line"):
                v = node.get(key)
                if isinstance(v, str):
                    lines.append(v)
            for v in node.values():
                _walk(v)
        elif isinstance(node, list):
            for v in node:
                _walk(v)

    _walk(data)
    return "\n".join(lines) if lines else raw


def _resolve_owner_id(service_id: str, render_key: str) -> str | None:
    st, raw = _http("GET", f"{RENDER_API}/services/{service_id}",
                    headers=_render_headers(render_key), timeout=30)
    if st != 200:
        return None
    try:
        data = json.loads(raw)
        svc = data.get("service", data)
        return svc.get("ownerId") or (svc.get("owner") or {}).get("id")
    except (json.JSONDecodeError, AttributeError, TypeError):
        return None


def reset_bench(service_id: str, render_key: str, bundle: Path,
                skip_reset: bool) -> dict:
    """Fire + poll the RESET one-off job; enforce the exposed-key abort."""
    print("\n===================== RESET (Render one-off job) =====================")
    rep: dict = {"skipped": skip_reset, "service_id": service_id}
    if skip_reset:
        print("  --skip-reset set: NOT firing the RESET job (KOs left as-is).")
        rep["note"] = "skipped via --skip-reset"
        (bundle / "reset_job.md").write_text(_reset_md(rep), encoding="utf-8")
        return rep

    body = json.dumps({"startCommand": RESET_START_COMMAND}).encode("utf-8")
    st, raw = _http("POST", f"{RENDER_API}/services/{service_id}/jobs",
                    headers=_render_headers(render_key), body=body, timeout=60)
    if st not in (200, 201):
        print(f"  RESET job creation failed: HTTP {st}")
        rep["error"] = f"job-create HTTP {st}"
        (bundle / "reset_job.md").write_text(_reset_md(rep), encoding="utf-8")
        sys.exit(EXIT_RESET_FAILED)
    try:
        job = json.loads(raw)
    except json.JSONDecodeError:
        print("  RESET job creation: non-JSON response")
        rep["error"] = "job-create non-JSON"
        (bundle / "reset_job.md").write_text(_reset_md(rep), encoding="utf-8")
        sys.exit(EXIT_RESET_FAILED)
    job_id = job.get("id") or (job.get("job") or {}).get("id")
    rep["job_id"] = job_id
    print(f"  RESET job created: id={job_id}  (startCommand redacted-safe: seed-bench-projects)")

    # Poll to terminal.
    terminal = {"succeeded", "failed"}
    status = job.get("status") or "pending"
    deadline = time.time() + 600
    while status not in terminal and time.time() < deadline:
        time.sleep(8)
        jst, jraw = _http("GET", f"{RENDER_API}/services/{service_id}/jobs/{job_id}",
                          headers=_render_headers(render_key), timeout=30)
        if jst == 200:
            try:
                jj = json.loads(jraw)
                status = (jj.get("job") or jj).get("status") or status
            except json.JSONDecodeError:
                pass
        print(f"  ...job status: {status}")
    rep["status"] = status
    owner_id = _resolve_owner_id(service_id, render_key)
    if status != "succeeded":
        # Pull the job's own log stream to explain WHY (e.g. an infra fault like
        # a disk-full Postgres PANIC), and confirm no key was minted before the
        # failure. Error lines are recorded redacted (never any adb_sk_ value).
        log_text, log_src = _fetch_job_logs(service_id, job_id, render_key, owner_id)
        rep["log_source"] = log_src
        minted_before_fail = [
            ln.strip()[len(MINTED_KEY_PREFIX):].split("=", 1)[0]
            for ln in log_text.splitlines()
            if ln.strip().startswith(MINTED_KEY_PREFIX) and "=adb_sk_" in ln
        ]
        rep["minted_slugs"] = minted_before_fail
        rep["error"] = f"terminal status {status}"
        rep["error_summary"] = _redacted_error_summary(log_text)
        print(f"  RESET job did NOT succeed (status={status}) — ABORT.")
        if rep["error_summary"]:
            print(f"  root cause (redacted): {rep['error_summary']}")
        if minted_before_fail:
            # Defensive: a key minted then the job died still leaks the plaintext.
            _write_rotation_required(bundle, minted_before_fail)
            rep["abort"] = "EXPOSED_KEY_BEFORE_FAILURE"
            print(f"  !!! a key was minted before the failure for slug(s): "
                  f"{sorted(set(minted_before_fail))} — treat as EXPOSED.")
        (bundle / "reset_job.md").write_text(_reset_md(rep), encoding="utf-8")
        sys.exit(EXIT_RESET_FAILED if not minted_before_fail else EXIT_EXPOSED_KEY)

    # Fetch logs (best-effort) and apply the security gate.
    log_text, log_src = _fetch_job_logs(service_id, job_id, render_key, owner_id)
    rep["log_source"] = log_src
    # Capture the RESET line + the safe/exposed determination.
    reset_lines = [ln for ln in log_text.splitlines() if RESET_LINE_MARKER in ln]
    rep["reset_line"] = reset_lines[0] if reset_lines else None
    safe_marker_present = SAFE_NO_MINT_MARKER in log_text
    minted_slugs = []
    for ln in log_text.splitlines():
        s = ln.strip()
        if s.startswith(MINTED_KEY_PREFIX) and "=adb_sk_" in s:
            # capture WHICH slug minted — never the key value.
            slug = s[len(MINTED_KEY_PREFIX):].split("=", 1)[0]
            minted_slugs.append(slug)
    rep["safe_no_mint"] = safe_marker_present
    rep["minted_slugs"] = minted_slugs
    rep["logs_retrieved"] = bool(log_text.strip())

    # ===== EXPOSED-KEY ABORT (mandatory, fail-closed) =====
    if minted_slugs:
        _write_rotation_required(bundle, minted_slugs)
        rep["abort"] = "EXPOSED_KEY"
        (bundle / "reset_job.md").write_text(_reset_md(rep), encoding="utf-8")
        print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!! EXPOSED-KEY ABORT: a bench key was missing and a RANDOM key")
        print(f"!!! was minted + logged for slug(s): {sorted(set(minted_slugs))}")
        print("!!! Treat those keys as EXPOSED. NOT ingesting. NO bundle committed.")
        print(f"!!! Rotation plan written to {bundle / 'ROTATION_REQUIRED.md'}")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        sys.exit(EXIT_EXPOSED_KEY)
    if not safe_marker_present:
        # Fail-closed: cannot positively confirm "no new plaintext minted".
        # The keys are all present in .env so the seed SHOULD hit the reuse
        # branch; if we could not read the confirmation we do not proceed.
        if not log_text.strip():
            print("\n!!! Could not retrieve RESET job logs to confirm the safe-mint")
            print(f"!!! marker. log fetch attempts: {log_src}")
        print("\n!!! SAFE-MINT marker not found in RESET logs — fail-closed ABORT.")
        print(f"!!! Expected line: {SAFE_NO_MINT_MARKER!r}")
        rep["abort"] = "UNCONFIRMED_SAFE_MINT"
        (bundle / "reset_job.md").write_text(_reset_md(rep), encoding="utf-8")
        sys.exit(EXIT_EXPOSED_KEY)

    print(f"  RESET succeeded. reset line: {rep['reset_line']}")
    print(f"  SAFE: {SAFE_NO_MINT_MARKER}")
    (bundle / "reset_job.md").write_text(_reset_md(rep), encoding="utf-8")
    return rep


def _reset_md(rep: dict) -> str:
    out = ["# RESET job (Render one-off)", ""]
    out.append(f"- service_id: `{rep.get('service_id')}`")
    if rep.get("skipped"):
        out.append("- **SKIPPED** via `--skip-reset` (KOs left as-is; NOT a clean slate).")
        return "\n".join(out) + "\n"
    out.append(f"- job_id: `{rep.get('job_id')}`")
    out.append(f"- terminal status: **{rep.get('status')}**")
    out.append(f"- startCommand: `{RESET_START_COMMAND}`")
    out.append(f"- log source: `{rep.get('log_source')}`")
    out.append(f"- logs retrieved: {rep.get('logs_retrieved')}")
    out.append("")
    out.append("## deleted-KOs line (verbatim from job logs)")
    out.append(f"```\n{rep.get('reset_line') or '(not captured)'}\n```")
    out.append("")
    if rep.get("error_summary"):
        out.append("## failure root cause (redacted; no key values)")
        out.append(f"```\n{rep['error_summary']}\n```")
        out.append("")
    out.append("## exposed-key gate")
    out.append(f"- minted slug(s): {rep.get('minted_slugs') or '[] (none — SAFE)'}")
    out.append(f"- safe-no-mint marker present: **{rep.get('safe_no_mint')}**")
    if rep.get("safe_no_mint"):
        out.append(f"- confirmation: `{SAFE_NO_MINT_MARKER}`")
    if rep.get("abort"):
        out.append(f"- ABORT: **{rep['abort']}**")
    return "\n".join(out) + "\n"


def _redacted_error_summary(log_text: str) -> str:
    """Pull the salient error lines from a failed job's logs, with any line that
    contains a minted key value (adb_sk_) REDACTED. Bounded to a few lines."""
    keep: list[str] = []
    for ln in log_text.splitlines():
        s = ln.strip()
        if not s:
            continue
        low = s.lower()
        if any(t in low for t in ("error", "panic", "no space left", "econnrefused",
                                  "authentication", "cannot find", "fatal", "exit code")):
            if "adb_sk_" in s:
                s = "[REDACTED LINE — contained a key value]"
            keep.append(s[:240])
        if len(keep) >= 6:
            break
    return "\n".join(keep)


def _write_rotation_required(bundle: Path, minted_slugs: list[str]) -> None:
    slugs = sorted(set(minted_slugs))
    txt = [
        "# ROTATION REQUIRED — exposed bench key(s)",
        "",
        "The RESET one-off job minted a RANDOM bench key (a per-corpus key was",
        "missing from the live DB) and printed it to the Render job logs. Render",
        "job logs are retained, so that plaintext key is EXPOSED.",
        "",
        f"## Affected slug(s): {slugs}",
        "(key VALUES are deliberately NOT recorded here.)",
        "",
        "## Rotation plan (perform BEFORE any retry)",
        "1. In the live oida-core Postgres, delete the `bench`-labelled apiKey row",
        "   for project `oida-<slug>` for each affected slug.",
        "2. Re-run `seed-bench-projects.ts` WITH `BENCH_KEY_SECRET` set (no",
        "   RESET_BENCH_KOS needed for the key fix), so the key is re-derived",
        "   DETERMINISTICALLY as HMAC-SHA256(secret, slug) and the canonical",
        "   `OIDA_CORE_KEY_<SLUG>` is restored (only sha256(plaintext) is stored).",
        "3. Confirm the corpora-repo `.env` `OIDA_CORE_KEY_<SLUG>` matches the",
        "   deterministic value, then re-run the harness.",
        "",
        "No Evidence Bundle is committed for this aborted run.",
    ]
    (bundle / "ROTATION_REQUIRED.md").write_text("\n".join(txt) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# CACHE COLD
# ---------------------------------------------------------------------------


def cache_cold(log_lines: list[str], skip_reset: bool) -> dict:
    """Cold the judge cache always; clear ingest reports ONLY when a RESET ran.

    The judge cache is ALWAYS deleted: the micro-probe must judge cold so the
    >=1-CONTRADICTS proof is real (belt-and-suspenders with the P0-S7 cache
    re-key). The ingest reports drive 01_ingest's resume-skip: deleting them
    forces a full re-ingest. That is correct ONLY after a RESET wiped the DB.
    On a --skip-reset run the DB still holds the prior KOs, so a full re-ingest
    would DUPLICATE every KO; we therefore KEEP the reports so 01_ingest resumes
    (skips already-committed docs) against the already-populated DB. Net: reports
    are cleared iff the DB was cleared, keeping ingest deterministic + duplicate-free.

    Falsification contract (this step):
      MEASURES: nothing about retrieval — it controls cold-start of the judge
        cache and the ingest resume set.
      HOW: unlink stance_judge_cache.json unconditionally; unlink the per-corpus
        ingest_reports/oida-core/*.jsonl iff not skip_reset.
      WHERE: experiments/output/ (gitignored); recorded in cache_cold rep ->
        run_manifest.json.
      WHAT CHANGES: a fresh (RESET) run re-ingests from empty; a --skip-reset run
        re-uses the populated DB without re-minting KOs. No engine effect."""
    print("\n===================== CACHE COLD =====================")
    rep: dict = {"skip_reset": skip_reset}
    cache_path = OUTPUT / "stance_judge_cache.json"
    if cache_path.exists():
        cache_path.unlink()
        rep["judge_cache_deleted"] = True
        print(f"  deleted {cache_path.relative_to(REPO_ROOT)}")
    else:
        rep["judge_cache_deleted"] = False
        print("  judge cache already absent")
    removed = []
    if not skip_reset:
        # delete local oida-core ingest reports so 01_ingest resume starts empty
        ingest_dir = OUTPUT / "ingest_reports" / SYSTEM
        if ingest_dir.is_dir():
            for p in sorted(ingest_dir.glob("*.jsonl")):
                p.unlink()
                removed.append(p.name)
        print(f"  deleted {len(removed)} oida-core ingest report(s): {removed}")
    else:
        print("  --skip-reset: KEEPING ingest reports so 01_ingest resumes against "
              "the populated DB (no re-mint of KOs).")
    rep["ingest_reports_deleted"] = removed
    log_lines.append(f"# cache cold: judge_cache_deleted={rep['judge_cache_deleted']} "
                     f"ingest_reports_deleted={removed} skip_reset={skip_reset}")
    return rep


# ---------------------------------------------------------------------------
# CLEAN-INGEST (oida-core only, 5 corpora)
# ---------------------------------------------------------------------------


def _read_ingest_report(corpus: str) -> dict:
    """Parse the regenerated ingest_reports/oida-core/<corpus>.jsonl -> health."""
    path = OUTPUT / "ingest_reports" / SYSTEM / f"{corpus}.jsonl"
    docs: list[dict] = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    docs.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    # keep only the LAST record per doc_id (append-only resume semantics)
    latest: dict[str, dict] = {}
    for rec in docs:
        did = rec.get("doc_id")
        if did:
            latest[did] = rec
    recs = list(latest.values())
    kos_created = sum(int(r.get("kos_created") or 0) for r in recs)
    partial_errors = sum(int(r.get("partial_error_count") or 0) for r in recs)
    n_docs = len(recs)
    n_committed = sum(1 for r in recs if r.get("committed"))
    n_zero_ko = sum(1 for r in recs if r.get("committed") and int(r.get("kos_created") or 0) == 0)
    n_partial_outliers = sum(1 for r in recs if int(r.get("partial_error_count") or 0) > 0)
    return {
        "corpus": corpus,
        "n_docs": n_docs,
        "n_committed": n_committed,
        "all_committed": n_docs > 0 and n_committed == n_docs,
        "kos_created": kos_created,
        "kos_created_positive": kos_created > 0,
        "n_docs_zero_ko": n_zero_ko,
        "partial_error_count": partial_errors,
        "n_docs_with_partial_errors": n_partial_outliers,
    }


def clean_ingest(log_lines: list[str]) -> dict:
    print("\n===================== CLEAN-INGEST (oida-core, 5 corpora) =====================")
    rc, _ = _run_script("01_ingest.py", ["--system", SYSTEM], log_lines)
    if rc != 0:
        print("!!! 01_ingest.py failed — ABORT")
        sys.exit(EXIT_INGEST)
    per_corpus = [_read_ingest_report(c) for c in ALL_CORPORA]
    # Ingest-health gate. The HARD gate is the roadmap §8 contract: every doc
    # committed AND per-corpus kos_created>0 (the engine produced epistemic
    # objects). A single committed doc yielding 0 KOs is NOT a failure — it is a
    # legitimate engine outcome for source text with no extractable propositions
    # (e.g. clearpath's 08-agenda/calendar-events: a calendar listing has dates
    # but no claims). Gating on it would make the harness un-runnable on the real
    # corpora despite a healthy ingest, so 0-KO docs are RECORDED (count surfaced
    # here + in harness_health.md) but do NOT abort. The corpus-level kos_created>0
    # gate still catches a genuinely dead ingest (all docs empty).
    #
    # Falsification contract (this gate):
    #   MEASURES: did the clean ingest commit every doc and produce >0 KOs per
    #     corpus? (the precondition for retrieve/score to mean anything).
    #   HOW: parse the resumable ingest_reports/oida-core/<corpus>.jsonl (last
    #     record per doc_id) -> all_committed + kos_created>0; the per-doc 0-KO
    #     tally is informational, not a gate.
    #   WHERE: failures -> stdout + EXIT_INGEST; the full per-corpus table
    #     (incl. 0-KO docs + partial_error_count) -> harness_health.md.
    #   WHAT CHANGES: a real ingest failure aborts before retrieve (no bundle);
    #     a benign 0-KO doc is logged and the run proceeds.
    failures = []
    warnings = []
    for h in per_corpus:
        if not h["all_committed"]:
            failures.append(f"{h['corpus']}: {h['n_committed']}/{h['n_docs']} committed")
        if not h["kos_created_positive"]:
            failures.append(f"{h['corpus']}: kos_created=0 (dead ingest)")
        if h["n_docs_zero_ko"] > 0:
            warnings.append(f"{h['corpus']}: {h['n_docs_zero_ko']} committed doc(s) with 0 KOs "
                            f"(benign — no extractable propositions; recorded, not a failure)")
    rep = {"per_corpus": per_corpus, "failures": failures, "warnings": warnings}
    if warnings:
        print("\n  ingest-health notes (recorded, NOT failures):")
        for w in warnings:
            print(f"   - {w}")
        log_lines.append("# ingest-health 0-KO notes: " + "; ".join(warnings))
    if failures:
        print("\n!!! INGEST HEALTH FAILURES:")
        for f in failures:
            print(f"   - {f}")
        sys.exit(EXIT_INGEST)
    print("\n  ingest health OK: every doc committed, kos_created>0 for all 5.")
    return rep


# ---------------------------------------------------------------------------
# WORKER DRAIN
# ---------------------------------------------------------------------------


def worker_drain(base_url: str, settle_sec: int, log_lines: list[str]) -> dict:
    print(f"\n===================== WORKER DRAIN (settle {settle_sec}s) =====================")
    print("  NOTE: cosmetic for P0 — cross-document edges arrive in Phase 1. This is")
    print("  NOT a claim that draining produced edges; it is a bounded settle-wait so")
    print("  the async ingest workers quiesce before retrieve.")
    t0 = time.time()
    # bounded settle-wait (sleep in small chunks so a Ctrl-C is responsive)
    remaining = settle_sec
    while remaining > 0:
        chunk = min(10, remaining)
        time.sleep(chunk)
        remaining -= chunk
    elapsed = round(time.time() - t0, 1)
    st, _ = _http("GET", base_url.rstrip("/") + "/health", timeout=30)
    health_ok = st == 200
    print(f"  settled {elapsed}s; /health -> {st}")
    rep = {"settle_sec_param": settle_sec, "settle_sec_actual": elapsed,
           "health_after": st, "health_ok": health_ok,
           "label": ("cosmetic for P0 — cross-document edges arrive in Phase 1; "
                     "not a claim that draining produced edges")}
    log_lines.append(f"# worker drain: settle={elapsed}s health={st} (cosmetic for P0)")
    if not health_ok:
        print("!!! /health not 200 after drain — ABORT")
        sys.exit(EXIT_INGEST)
    return rep


# ---------------------------------------------------------------------------
# RETRIEVE + LAYERS
# ---------------------------------------------------------------------------


def retrieve_and_layers(run_id: str, log_lines: list[str]) -> dict:
    print(f"\n===================== RETRIEVE + LAYERS (RUN_ID={run_id}) =====================")
    rep: dict = {"run_id": run_id, "steps": {}}

    rc, _ = _run_script("02_retrieve.py", ["--system", SYSTEM, "--run-id", run_id], log_lines)
    rep["steps"]["02_retrieve"] = rc
    if rc != 0:
        sys.exit(EXIT_LAYER)

    rc, _ = _run_script("03_eval_static_ir.py",
                        ["--run-id", run_id, "--system", SYSTEM], log_lines)
    rep["steps"]["03_static_ir"] = rc
    if rc != 0:
        sys.exit(EXIT_LAYER)

    rc, _ = _run_script("04_eval_adversarial.py", ["--system", SYSTEM], log_lines)
    rep["steps"]["04_adversarial"] = rc

    # 05 dry-run: headline (b) is judge-free, runs in both modes.
    rc, _ = _run_script("05_eval_stance_abstention.py",
                        ["--dry-run", "--system", SYSTEM], log_lines)
    rep["steps"]["05_stance_dry_run"] = rc

    rc, _ = _run_script("06_eval_temporal.py", ["--system", SYSTEM], log_lines)
    rep["steps"]["06_temporal"] = rc

    rc, _ = _run_script("07_collect_telemetry.py", ["--system", SYSTEM], log_lines)
    rep["steps"]["07_telemetry"] = rc
    return rep


# ---------------------------------------------------------------------------
# MICRO-PROBE (live, cold cache)
# ---------------------------------------------------------------------------


def micro_probe(log_lines: list[str]) -> dict:
    print("\n===================== MICRO-PROBE (live judge, clearpath) =====================")
    print("  Judges the 13 clearpath stance-evaluable queries (5 gold-CONTRADICTS:")
    print("  q03/q04/q16/q19/q25). Proves CONTRADICTS is reachable post P0-S3/S4 +")
    print("  the cache re-key. Cost ~cents.")
    rc, captured = _run_script("05_eval_stance_abstention.py",
                              ["--run", "--system", SYSTEM, MICRO_PROBE_CORPUS],
                              log_lines, check=False)
    rep: dict = {"rc": rc, "corpus": MICRO_PROBE_CORPUS}
    # Re-derive the emitted label distribution directly from the run + cache so
    # the bundle records the ground truth (not a parse of stdout). We re-judge
    # from the now-warm cache (no new API cost — every key is cached).
    dist, contradicts, finding = _probe_label_distribution()
    rep["label_distribution"] = dist
    rep["n_contradicts"] = contradicts
    rep["at_least_one_contradicts"] = contradicts >= 1
    rep["finding"] = finding
    print(f"  emitted label distribution (n=13): {dist}")
    print(f"  CONTRADICTS count: {contradicts}  (>=1 required)")
    if contradicts < 1:
        print("  FINDING: 0 CONTRADICTS emitted — recorded honestly, NOT faked.")
    return rep


def _probe_label_distribution() -> tuple[dict, int, str | None]:
    """Recompute the 13-query label distribution for clearpath from the warm
    judge cache (no new cost). Mirrors 05's _answer_for + _judge keying exactly."""
    import hashlib
    sys.path.insert(0, str(SCRIPTS))
    mod = _import_05()
    corpus = MICRO_PROBE_CORPUS
    sg = ec.load_annotation("stance_gold", corpus) or {}
    evaluable = {q: g["gold_stance"] for q, g in sg.items()
                 if g.get("stance_evaluable") and g.get("gold_stance")}
    docs = ec.load_corpus_docs(corpus)
    queries = ec.load_queries(corpus)
    runs = ec.load_runs(corpus, SYSTEM) or {}
    recs = ec.load_retrieve_records(corpus, SYSTEM)
    cache = {}
    cache_path = OUTPUT / "stance_judge_cache.json"
    if cache_path.exists():
        try:
            cache = json.loads(cache_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            cache = {}
    from collections import Counter
    labels = []
    finding = None
    for qid, gold in evaluable.items():
        ans = mod._answer_for(SYSTEM, qid, recs, docs, runs)
        qtext = queries.get(qid, {}).get("text", "")
        if not ans.strip():
            labels.append("INVALID")
            continue
        key = hashlib.sha256(
            f"{mod.CACHE_VERSION}\0{mod.JUDGE_MODEL}\0{mod.JUDGE_MAX_TOKENS}\0{qtext}\0{ans}".encode()
        ).hexdigest()
        labels.append(cache.get(key, "UNCACHED"))
    if "UNCACHED" in labels:
        finding = ("some queries were UNCACHED at recompute time — the micro-probe "
                   "run may not have judged every query; distribution may be partial")
    dist = dict(Counter(labels))
    contradicts = dist.get("CONTRADICTS", 0)
    return dist, contradicts, finding


_MOD05 = None


def _import_05():
    """Import the 05 module (filename starts with a digit, so use importlib)."""
    global _MOD05
    if _MOD05 is not None:
        return _MOD05
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "stance05", str(SCRIPTS / "05_eval_stance_abstention.py"))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _MOD05 = mod
    return mod


# ---------------------------------------------------------------------------
# in-harness signal computation (non-constant distributions)
# ---------------------------------------------------------------------------


def _per_query_ndcg10(corpus: str, run_id: str) -> list[float]:
    """Per-query L1 NDCG@10 from runs.json + qrels (in-harness via eval_common)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "static_ir", str(SCRIPTS / "03_eval_static_ir.py"))
    assert spec and spec.loader
    s3 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(s3)
    qrels = ec.load_qrels(corpus)
    runs = ec.load_runs(corpus, SYSTEM) or {}
    vals = []
    for qid, qrels_q in qrels.items():
        if not qrels_q:
            continue
        retrieved = ec.ranked(runs.get(qid, {}))
        vals.append(s3.ndcg_at_k(retrieved, qrels_q, 10))
    return vals


def _score_component_spread(corpus: str, n_sample: int = 3) -> list[dict]:
    """similarity / regime_adjusted_score spread for ~n sampled queries."""
    recs = ec.load_retrieve_records(corpus, SYSTEM)
    out = []
    for qid in sorted(recs.keys())[:n_sample]:
        sc = recs[qid].get("score_components") or {}
        sims = [c.get("similarity") for c in sc.values() if isinstance(c.get("similarity"), (int, float))]
        ras = [c.get("regime_adjusted_score") for c in sc.values()
               if isinstance(c.get("regime_adjusted_score"), (int, float))]
        out.append({
            "qid": qid,
            "n_docs": len(sc),
            "similarity": _spread(sims),
            "regime_adjusted_score": _spread(ras),
        })
    return out


def _spread(xs: list[float]) -> dict:
    xs = [x for x in xs if isinstance(x, (int, float))]
    if not xs:
        return {"n": 0, "min": None, "median": None, "max": None, "spread": None, "non_constant": False}
    mn, mx = min(xs), max(xs)
    return {
        "n": len(xs),
        "min": round(mn, 6),
        "median": round(statistics.median(xs), 6),
        "max": round(mx, 6),
        "spread": round(mx - mn, 6),
        "non_constant": (mx - mn) > 1e-9,
    }


def _epistemic_signal_presence(corpus: str) -> dict:
    """Count dialectic_resolutions / contradiction_edge_count across queries.
    LABELED ABSENT pre-Phase-1 by design (intra-document graph only)."""
    recs = ec.load_retrieve_records(corpus, SYSTEM)
    dr = [len(r.get("dialectic_resolutions") or []) for r in recs.values()]
    ce = [int(r.get("contradiction_edge_count") or 0) for r in recs.values()]
    return {
        "n_queries": len(recs),
        "dialectic_resolutions_total": sum(dr),
        "contradiction_edge_count_total": sum(ce),
        "max_dialectic_resolutions": max(dr) if dr else 0,
        "max_contradiction_edge_count": max(ce) if ce else 0,
    }


# ---------------------------------------------------------------------------
# BUNDLE assembly
# ---------------------------------------------------------------------------


def _result_path(corpus: str, run_id: str) -> Path:
    return REPO_ROOT / "corpora" / corpus / "results" / f"{SYSTEM}_{run_id}.json"


def assemble_bundle(bundle: Path, phase: str, ts: str, run_id: str,
                    preflight_rep: dict, reset_rep: dict, cache_rep: dict,
                    ingest_rep: dict, drain_rep: dict, layers_rep: dict,
                    probe_rep: dict, log_lines: list[str], corpora_mode: str,
                    db_infra: dict) -> dict:
    print("\n===================== BUNDLE =====================")
    layers_dir = bundle / "layers"
    layers_dir.mkdir(parents=True, exist_ok=True)

    # --- layers/ : copy the 5 scored result JSONs + RESULTS.md ---
    fresh_ndcg10: dict[str, float] = {}
    layer_summaries: list[str] = []
    for corpus in ALL_CORPORA:
        src = _result_path(corpus, run_id)
        if src.exists():
            shutil.copyfile(src, layers_dir / f"{SYSTEM}_{run_id}__{corpus}.json")
            res = json.loads(src.read_text(encoding="utf-8"))
            l1 = res.get("layer_1_static_ir", {})
            ndcg = (l1.get("ndcg") or {})
            n10 = ndcg.get("10")
            if isinstance(n10, (int, float)):
                fresh_ndcg10[corpus] = float(n10)
            l3 = res.get("layer_3_stance_abstention", {})
            ser = l3.get("stance_evidence_recall", {}) or {}
            recall_any10 = None
            if isinstance(ser.get("10"), dict):
                recall_any10 = ser["10"].get("stance_recall_any")
            l2 = res.get("layer_2_adversarial", {})
            l4 = res.get("layer_4_temporal", {})
            l5 = res.get("layer_5_practicality", {})
            layer_summaries.append(
                f"### {corpus}\n"
                f"- L1: NDCG@10={_fmt(ndcg.get('10'))} NDCG@5={_fmt(ndcg.get('5'))} "
                f"Recall@10={_fmt((l1.get('recall') or {}).get('10'))} "
                f"MAP@10={_fmt((l1.get('map') or {}).get('10'))}\n"
                f"- L2: ContraR@10={_fmt(l2.get('contradiction_recall_at_10'))} "
                f"Trap@5={_fmt(l2.get('trap_in_top_5'))} "
                f"SupAbove={_fmt(l2.get('superseded_above_rate'))}\n"
                f"- L3 (b) stance_recall_any@10={_fmt(recall_any10)} [HEADLINE] "
                f"(judge metrics null in dry-run, by design)\n"
                f"- L4: CSA@10={_fmt(l4.get('current_state_accuracy_at_10'))} "
                f"SupLeak@10={_fmt(l4.get('superseded_leakage_at_10'))} "
                f"TmpNDCG@10={_fmt(l4.get('temporal_ndcg_at_10'))} "
                f"F-TEMP-7lift={_fmt(l4.get('temporal_ndcg_lift_b2_minus_b0'))}\n"
                f"- L5: p50={_fmt(l5.get('retrieve_latency_ms_p50'),0)}ms "
                f"p95={_fmt(l5.get('retrieve_latency_ms_p95'),0)}ms "
                f"ingest_s/doc={_fmt(l5.get('ingest_wall_clock_sec_per_doc_median'),2)}\n"
            )
    # copy RESULTS.md if present
    results_md = REPO_ROOT / "RESULTS.md"
    if results_md.exists():
        shutil.copyfile(results_md, layers_dir / "RESULTS.md")
    (layers_dir / "layer_summary.md").write_text(
        "# Layer summary (oida-core, 5 corpora)\n\n"
        f"run_id: `{run_id}`  |  corpora: {corpora_mode} (BURNED — regression/sanity only)\n\n"
        + "\n".join(layer_summaries), encoding="utf-8")

    # --- harness_health.md ---
    _write_harness_health(bundle, probe_rep, ingest_rep, reset_rep, run_id, db_infra)

    # --- signal_presence.md ---
    _write_signal_presence(bundle, run_id)

    # --- diff_vs_baseline.md (delegate to diff_baseline.py for the canonical
    #     archived-vs-fresh comparison; reusable by the verifier) ---
    diff_rep = _write_diff_vs_baseline(bundle, run_id, fresh_ndcg10, log_lines)

    # --- notes.md (verifier comparison contract) ---
    _write_notes(bundle, drain_rep)

    # --- graph_composition.md (stub, Phase-1+) ---
    _write_graph_composition(bundle)

    # --- acceptance.txt (raw harness log) ---
    (bundle / "acceptance.txt").write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    # --- run_manifest.json (machine-readable summary; NO secrets) ---
    manifest = {
        "phase": phase,
        "ts": ts,
        "run_id": run_id,
        "system": SYSTEM,
        "corpora_mode": corpora_mode,
        "corpora": ALL_CORPORA,
        "preflight": preflight_rep,
        "db_infra": db_infra,
        "reset": {k: v for k, v in reset_rep.items()},
        "cache_cold": cache_rep,
        "ingest_health": ingest_rep,
        "worker_drain": drain_rep,
        "layers": layers_rep,
        "micro_probe": probe_rep,
        "diff_vs_baseline": diff_rep,
        "guardrail": ("BURNED dev corpora — regression/sanity ONLY, never an OIDA "
                      "pass/fail claim; pass/fail lives in Phase-4 fresh corpora."),
    }
    (bundle / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    try:
        shown = bundle.relative_to(REPO_ROOT)
    except ValueError:
        shown = bundle
    print(f"  bundle written: {shown}")
    return {"diff": diff_rep, "fresh_ndcg10": fresh_ndcg10}


def _fmt(v, nd: int = 4) -> str:
    return f"{v:.{nd}f}" if isinstance(v, (int, float)) else "—"


def _write_harness_health(bundle: Path, probe_rep: dict, ingest_rep: dict,
                          reset_rep: dict, run_id: str, db_infra: dict) -> None:
    lines = ["# harness_health.md", ""]
    # DB infrastructure first: the conditions THIS run executed under (lesson of
    # the 2026-06-03 disk-full outage). READ-ONLY snapshot from the Render API;
    # NO secret is recorded (only public infra metadata).
    lines.append("## DB infrastructure (Render Postgres, read-only snapshot)")
    lines.append("")
    lines.append("Records the managed Postgres conditions the run executed against")
    lines.append("(pulled READ-ONLY from the Render API; the API key is never recorded).")
    lines.append("")
    lines.append(f"- endpoint: `{db_infra.get('endpoint')}`")
    lines.append(f"- fetch_ok: **{db_infra.get('fetch_ok')}** (HTTP {db_infra.get('http_status')})")
    if db_infra.get("fetch_ok"):
        lines.append(f"- name: `{db_infra.get('name')}`")
        lines.append(f"- **status: `{db_infra.get('status')}`**")
        lines.append(f"- plan: `{db_infra.get('plan')}`")
        lines.append(f"- diskSizeGB: `{db_infra.get('diskSizeGB')}`")
        lines.append(f"- region: `{db_infra.get('region')}`  |  version: `{db_infra.get('version')}`"
                     f"  |  suspended: `{db_infra.get('suspended')}`")
    else:
        lines.append(f"- error: {db_infra.get('error')}")
        lines.append("- NOTE: infra snapshot unavailable, but the run proceeded because the")
        lines.append("  PREFLIGHT DB-reachability probe (an authenticated retrieve) passed —")
        lines.append("  that probe, not this snapshot, is the gate.")
    lines.append("")
    lines.append("## Micro-probe — judge label distribution (clearpath, live, cold cache)")
    lines.append("")
    lines.append("Judges the 13 stance-evaluable clearpath queries (5 gold-CONTRADICTS:")
    lines.append("q03/q04/q16/q19/q25).")
    lines.append("")
    lines.append(f"- emitted label distribution (n=13): `{probe_rep.get('label_distribution')}`")
    lines.append(f"- **CONTRADICTS count: {probe_rep.get('n_contradicts')}** "
                 f"(>=1 invariant: {'HELD' if probe_rep.get('at_least_one_contradicts') else 'FINDING — 0 emitted'})")
    if probe_rep.get("finding"):
        lines.append(f"- finding: {probe_rep['finding']}")
    lines.append("")
    lines.append("### Before/after framing vs the old judge bug")
    lines.append("Pre P0-S3 the judge ran with `max_tokens=4` and (pre P0-S4) was fed a")
    lines.append("GraphRAG-only prose shortcut; on the burned set that produced **0/181**")
    lines.append("CONTRADICTS (every label collapsed to INVALID/NEUTRAL). With")
    lines.append("`max_tokens=16` (P0-S3), top-1 doc-text input for ALL systems (P0-S4),")
    lines.append("and the P0-S7 cache re-key (so those fixes are no longer masked by stale")
    lines.append("cache hits), CONTRADICTS is now reachable. This proves the judge axis is")
    lines.append("live; it is NOT an OIDA stance score (the burned set is sanity-only).")
    lines.append("")
    lines.append("## Per-corpus ingest health")
    lines.append("")
    lines.append("| corpus | docs | committed | all_committed | kos_created | 0-KO docs | partial_errs | partial-err docs |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for h in ingest_rep.get("per_corpus", []):
        lines.append(f"| {h['corpus']} | {h['n_docs']} | {h['n_committed']} | "
                     f"{h['all_committed']} | {h['kos_created']} | {h['n_docs_zero_ko']} | "
                     f"{h['partial_error_count']} | {h['n_docs_with_partial_errors']} |")
    lines.append("")
    lines.append("## P0-S6 adapter-retained epistemic fields")
    lines.append("")
    lines.append("The retrieve adapter retains `dialectic_resolutions`, `contradiction_edges`,")
    lines.append("and `contradiction_edge_count` per query (P0-S6). Pre-Phase-2 these are")
    lines.append("EMPTY by design (the cross-document epistemic graph is built in Phase 1 and")
    lines.append("the contradiction path activates in Phase 2). Presence of the fields (not")
    lines.append("their values) is the P0 check; per-corpus presence:")
    lines.append("")
    for corpus in ALL_CORPORA:
        recs = ec.load_retrieve_records(corpus, SYSTEM)
        n_with_fields = sum(
            1 for r in recs.values()
            if "dialectic_resolutions" in r and "contradiction_edge_count" in r)
        ep = _epistemic_signal_presence(corpus)
        lines.append(f"- {corpus}: fields present on {n_with_fields}/{len(recs)} query records; "
                     f"dialectic_resolutions total={ep['dialectic_resolutions_total']}, "
                     f"contradiction_edge_count total={ep['contradiction_edge_count_total']} "
                     f"(EMPTY pre-Phase-2, LABELED so)")
    lines.append("")
    lines.append("## RESET-job confirmation")
    lines.append("")
    if reset_rep.get("skipped"):
        lines.append("- RESET was **skipped** via `--skip-reset` (not a clean slate).")
    else:
        lines.append(f"- reset line: `{reset_rep.get('reset_line')}`")
        lines.append(f"- **{SAFE_NO_MINT_MARKER}** present: {reset_rep.get('safe_no_mint')}")
        lines.append(f"- minted slugs (must be empty): {reset_rep.get('minted_slugs')}")
    (bundle / "harness_health.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_signal_presence(bundle: Path, run_id: str) -> None:
    lines = ["# signal_presence.md", ""]
    lines.append("Proves the live signals are **non-constant** (roadmap §9 / IC decision #2).")
    lines.append("A constant signal is reported as ABSENT.")
    lines.append("")
    lines.append("## Per-query L1 NDCG@10 distribution (per corpus)")
    lines.append("")
    lines.append("| corpus | n_q | min | median | max | spread | non-constant |")
    lines.append("|---|---|---|---|---|---|---|")
    for corpus in ALL_CORPORA:
        vals = _per_query_ndcg10(corpus, run_id)
        sp = _spread(vals)
        lines.append(f"| {corpus} | {sp['n']} | {_fmt(sp['min'])} | {_fmt(sp['median'])} | "
                     f"{_fmt(sp['max'])} | {_fmt(sp['spread'])} | {sp['non_constant']} |")
    lines.append("")
    lines.append("### Sample per-query NDCG@10 (first corpus, up to 12 queries)")
    sample_vals = _per_query_ndcg10(ALL_CORPORA[0], run_id)[:12]
    lines.append(f"`{ALL_CORPORA[0]}`: " + ", ".join(_fmt(v) for v in sample_vals))
    lines.append("")
    lines.append("## score_components spread (similarity / regime_adjusted_score)")
    lines.append("")
    lines.append("~3 sampled queries per corpus; spread>0 proves non-constant scoring.")
    lines.append("")
    for corpus in ALL_CORPORA:
        lines.append(f"### {corpus}")
        for s in _score_component_spread(corpus, 3):
            lines.append(
                f"- {s['qid']} (n_docs={s['n_docs']}): "
                f"similarity[min={_fmt(s['similarity']['min'])} max={_fmt(s['similarity']['max'])} "
                f"spread={_fmt(s['similarity']['spread'])} nonconst={s['similarity']['non_constant']}] "
                f"regime_adjusted_score[min={_fmt(s['regime_adjusted_score']['min'])} "
                f"max={_fmt(s['regime_adjusted_score']['max'])} "
                f"spread={_fmt(s['regime_adjusted_score']['spread'])} "
                f"nonconst={s['regime_adjusted_score']['non_constant']}]")
        lines.append("")
    lines.append("## Epistemic signals (dialectic_resolutions / contradiction_edge_count)")
    lines.append("")
    lines.append("**ABSENT pre-Phase-1, by design.** The cross-document epistemic graph is")
    lines.append("built in Phase 1; the contradiction path activates in Phase 2. The adapter")
    lines.append("retains these fields (P0-S6) but they are empty/zero on the burned corpora")
    lines.append("today — reported here as ABSENT, not as a regression.")
    lines.append("")
    for corpus in ALL_CORPORA:
        ep = _epistemic_signal_presence(corpus)
        lines.append(f"- {corpus}: dialectic_resolutions total={ep['dialectic_resolutions_total']} "
                     f"(max/q={ep['max_dialectic_resolutions']}), contradiction_edge_count "
                     f"total={ep['contradiction_edge_count_total']} (max/q={ep['max_contradiction_edge_count']}) "
                     f"-> ABSENT")
    (bundle / "signal_presence.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_diff_vs_baseline(bundle: Path, run_id: str, fresh_ndcg10: dict,
                            log_lines: list[str]) -> dict:
    """Delegate to diff_baseline.py (reusable by the verifier). It writes
    diff_vs_baseline.md and returns the structured deltas."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "diff_baseline", str(SCRIPTS / "diff_baseline.py"))
    assert spec and spec.loader
    db = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(db)
    diff_rep = db.diff_and_write(bundle / "diff_vs_baseline.md", fresh_ndcg10)
    log_lines.append("# diff_vs_baseline: " + json.dumps(diff_rep["per_corpus"]))
    return diff_rep


def _write_notes(bundle: Path, drain_rep: dict) -> None:
    lines = [
        "# notes.md — verifier comparison contract + falsification",
        "",
        "## Verifier comparison contract",
        "",
        "When the verifier re-runs this harness, compare its fresh bundle against",
        "THIS Phase-0 baseline under the following rules.",
        "",
        "### MUST-MATCH (deterministic; a mismatch is a real regression)",
        "- per-corpus **L1 NDCG@10 / Recall@10 / MAP@10** (±1e-6) — pure functions of",
        "  runs.json + qrels; the engine is unchanged in Phase 0.",
        "- per-corpus **stance metric (b) `stance_recall_any@k`** — pure retrieval, no",
        "  judge; deterministic from runs.json + annotations + qrels.",
        "- per-corpus **kos_created** (ingest is deterministic + idempotent after a",
        "  clean RESET).",
        "",
        "### TOLERATED (non-deterministic or environmental; NOT a regression)",
        "- timestamps, the `<ts>` bundle dir name, the `run_id`.",
        "- retrieve latency (p50/p95) and imputed cost.",
        "- LLM-nondeterministic artifacts: edge counts, contradiction structures, and",
        "  the micro-probe's EXACT label mix. Only the **>=1 CONTRADICTS** invariant",
        "  must hold (the judge can legitimately shift a borderline label run-to-run).",
        "",
        "## Falsification contract (what this harness measures / how / where / effect)",
        "- MEASURES: regression — does a clean re-ingest + 5-layer score on the burned",
        "  corpora reproduce the archived NDCG@10 within ±0.005 (engine unchanged),",
        "  with all signals present + non-constant and the judge axis live (>=1",
        "  CONTRADICTS)?",
        "- HOW: clean RESET (Render one-off) -> deterministic 01_ingest -> bounded",
        "  worker drain -> 02 retrieve -> 03..07 layer scorers -> in-harness per-query",
        "  NDCG@10 / score-component spreads + a live micro-probe.",
        "- WHERE: serialized into this bundle (layers/, harness_health.md,",
        "  signal_presence.md, diff_vs_baseline.md, run_manifest.json).",
        "- WHAT CHANGES: nothing in the engine — the harness is read-mostly (it only",
        "  mutates the live bench projects' KOs via the documented RESET + ingest). It",
        "  GATES phase completion: a phase is not done until its bundle is produced and",
        "  no unexplained regression on a non-target metric appears.",
        "",
        f"## Worker-drain settle-wait: param={drain_rep.get('settle_sec_param')}s "
        f"actual={drain_rep.get('settle_sec_actual')}s health_after={drain_rep.get('health_after')}",
        f"LABEL: {drain_rep.get('label')}",
        "",
        "## Guardrail",
        "BURNED dev corpora = regression / sanity ONLY, never an OIDA pass/fail claim.",
        "Pass/fail lives exclusively in the Phase-4 fresh corpora.",
    ]
    (bundle / "notes.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_graph_composition(bundle: Path) -> None:
    lines = [
        "# graph_composition.md",
        "",
        "**STUB — Phase-1+.** Edges-by-type and the cross- vs intra-document edge",
        "ratio are produced once Phase 1 builds the cross-document epistemic graph.",
        "",
        "Today (Phase 0) the OIDA graph is intra-document only: cross-document",
        "`contradicts`/`supersedes` edges are NOT yet formed, so the cross-document",
        "edge ratio is ~0 BY DESIGN. The adapter already retains the contradiction-edge",
        "fields (P0-S6) so this section can be populated without re-plumbing once the",
        "edges exist. No edge-composition claim is made for Phase 0.",
    ]
    (bundle / "graph_composition.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def _prod_reset_blocked(target: str, skip_reset: bool, allow_prod_reset: bool) -> bool:
    """True iff this invocation would RESET production and must be blocked.

    Blocked iff the resolved target is prod (the default) AND a RESET would fire
    (not --skip-reset) AND the operator did not explicitly opt in via
    --allow-prod-reset. `--target staging` is never blocked; `--skip-reset` (no
    RESET fires) is never blocked.
    """
    return target == "prod" and not skip_reset and not allow_prod_reset


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--phase", required=True, help="phase id, e.g. P0-baseline")
    p.add_argument("--corpora", choices=["burned", "fresh"], default="burned")
    p.add_argument("--env-file", default=str(REPO_ROOT / ".env"))
    p.add_argument("--skip-reset", action="store_true")
    p.add_argument("--target", choices=["prod", "staging"], default="prod",
                   help="which oida-core deploy to run against (default: prod). "
                        "staging = the Option-2 verification service (oida-core-staging); "
                        "engine steps verify here pre-merge, then merge to main on GREEN.")
    p.add_argument("--allow-prod-reset", action="store_true",
                   help="explicitly permit a RESET against PRODUCTION oida-core. "
                        "Required when --target is prod (the default) and a RESET "
                        "would fire; ignored for --target staging and --skip-reset.")
    p.add_argument("--settle-sec", type=int, default=None,
                   help="override worker-drain settle seconds (default OIDA_CORE_SETTLE_SEC or 90)")
    args = p.parse_args(argv)

    if args.corpora == "fresh":
        print("error: --corpora fresh not implemented (Phase-4 fresh corpora are a "
              "separate, pre-registered run). Use --corpora burned.")
        return 1

    if _prod_reset_blocked(args.target, args.skip_reset, args.allow_prod_reset):
        print(
            "error: refusing to fire a RESET against PRODUCTION oida-core.\n"
            "  --target is 'prod' (the default) and --skip-reset was not passed, so this\n"
            "  run would RESET (wipe the 5 bench projects' KOs) and re-ingest PRODUCTION,\n"
            "  then verify against the production engine — the degenerate-config trap\n"
            "  Phase 0 cleaned up.\n"
            "    - To verify an engine change, run against staging:  --target staging\n"
            "    - To intentionally reset production, pass:           --allow-prod-reset",
            file=sys.stderr,
        )
        return EXIT_PROD_RESET_BLOCKED

    env = _load_env(Path(args.env_file))
    # --target staging: route the whole run at the Option-2 staging deploy by
    # injecting the staging ids/URL through the existing OIDA_CORE_RENDER_*
    # override plumbing (PREFLIGHT service resolution, DB-infra probe, base_url,
    # and the RESET job all read these). prod is the default and is untouched.
    if args.target == "staging":
        env["OIDA_CORE_BASE_URL"] = env.get("OIDA_CORE_BASE_URL_STAGING") or STAGING_BASE_URL
        env["OIDA_CORE_RENDER_SERVICE_ID"] = env.get("OIDA_CORE_RENDER_SERVICE_ID_STAGING") or STAGING_SERVICE_ID
        env["OIDA_CORE_RENDER_DB_ID"] = env.get("OIDA_CORE_RENDER_DB_ID_STAGING") or STAGING_DB_ID
    # secrets pulled into locals; NEVER printed.
    base_url = env.get("OIDA_CORE_BASE_URL", "https://oida-core.onrender.com")
    render_key = env.get("RENDER_API_KEY", "")
    settle_sec = (args.settle_sec if args.settle_sec is not None
                  else int(env.get("OIDA_CORE_SETTLE_SEC", "90")))

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = ts  # one RUN_ID for retrieve + all layers
    bundle = OUTPUT / "regression" / f"{args.phase}-{ts}"
    bundle.mkdir(parents=True, exist_ok=True)

    print(f"\n############ Regression Harness — phase={args.phase} ts={ts} ############")
    print(f"  target:  {args.target.upper()}")
    print(f"  corpora: {args.corpora} (BURNED — regression/sanity only)")
    print(f"  bundle:  {bundle.relative_to(REPO_ROOT)}")
    print(f"  oida-core: {base_url}")

    log_lines: list[str] = [f"# regression harness phase={args.phase} ts={ts} run_id={run_id}",
                            f"# target={args.target} corpora={args.corpora} base_url={base_url}"]

    # 1) PREFLIGHT
    preflight_rep = preflight(env, base_url, render_key)
    service_id = preflight_rep["service_id"]

    # 1b) DB infra snapshot (READ-ONLY) — record the run's infrastructure
    #     conditions in the bundle (lesson of the 2026-06-03 outage). Does NOT
    #     gate (the PREFLIGHT DB-reachability probe is the gate); informational.
    db_id = env.get("OIDA_CORE_RENDER_DB_ID", "").strip() or DEFAULT_OIDA_CORE_DB_ID
    db_infra = fetch_db_infra(db_id, render_key)
    print(f"\n  DB infra (read-only): status={db_infra.get('status')} "
          f"plan={db_infra.get('plan')} diskSizeGB={db_infra.get('diskSizeGB')} "
          f"name={db_infra.get('name')} (fetch_ok={db_infra.get('fetch_ok')})")

    # 2) RESET (+ exposed-key abort)
    reset_rep = reset_bench(service_id, render_key, bundle, args.skip_reset)

    # 3) CACHE COLD (judge cache always; ingest reports only if a RESET ran)
    cache_rep = cache_cold(log_lines, args.skip_reset)

    # 4) CLEAN-INGEST
    ingest_rep = clean_ingest(log_lines)

    # 5) WORKER DRAIN
    drain_rep = worker_drain(base_url, settle_sec, log_lines)

    # 6) RETRIEVE + LAYERS
    layers_rep = retrieve_and_layers(run_id, log_lines)

    # 7) MICRO-PROBE (live judge)
    probe_rep = micro_probe(log_lines)

    # 8) BUNDLE
    bundle_rep = assemble_bundle(
        bundle, args.phase, ts, run_id, preflight_rep, reset_rep, cache_rep,
        ingest_rep, drain_rep, layers_rep, probe_rep, log_lines, args.corpora,
        db_infra)

    # ---- final acceptance gate ----
    diff = bundle_rep["diff"]
    all_within = diff.get("all_within_tolerance", False)
    probe_ok = probe_rep.get("at_least_one_contradicts", False)
    print("\n===================== ACCEPTANCE =====================")
    print(f"  ±{NDCG10_TOLERANCE} NDCG@10 vs archived baseline: "
          f"{'PASS' if all_within else 'FAIL'}")
    print(f"  micro-probe >=1 CONTRADICTS: {'PASS' if probe_ok else 'FAIL (recorded as finding)'}")
    print(f"  bundle: {bundle.relative_to(REPO_ROOT)}")
    if not all_within:
        print("\n!!! ACCEPTANCE FAILED: NDCG@10 moved beyond ±0.005 on a non-target "
              "metric (engine unchanged in Phase 0 — investigate).")
        return 1
    if not probe_ok:
        print("\n!!! ACCEPTANCE FAILED: micro-probe emitted 0 CONTRADICTS. Recorded as a "
              "FINDING in harness_health.md (not faked); the judge axis appears dead.")
        return 1
    print("\nACCEPTANCE PASS — bundle complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
