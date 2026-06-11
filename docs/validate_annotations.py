#!/usr/bin/env python3
"""Validate the Paper-2 annotation layers against docs/annotation-guide.md.

Usage:
    python3 docs/validate_annotations.py corpora/<id> [corpora/<id> ...]
    python3 docs/validate_annotations.py            # validates every corpus under corpora/

Exit code 0 only if there are zero ERRORs. WARNs never fail the build.
stdlib-only, no dependencies (mirrors the sandbox's stdlib-only discipline).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# ---- controlled vocabularies (annotation-guide.md §1) -----------------------
LIFECYCLE = {
    "provisional", "active", "unknown", "canonical",
    "stale", "contradicted", "superseded", "archived", "retracted",
}
OBSOLETE = {"superseded", "archived", "retracted"}
STANCE = {"supports", "contradicts", "neutral"}
TEMPORAL_INTENT = {
    "current_state", "as_of_time", "supersession_check",
    "change_over_time", "stable_knowledge",
}
REL_POLARITY = {
    "supports": "positive",
    "implements": "positive",
    "based_on": "positive",
    "contradicts": "negative",
    "blocks": "negative",
    "supersedes": "directional",
}

# ---- temporal cutoffs per corpus (annotation-guide.md §2 / paper Tab. 4) -----
CUTOFFS = {
    "org-consulting-clearpath": ["2025-09-30", "2025-11-01", "2025-12-15"],
    "org-iot-fireglass": ["2025-08-31", "2025-09-30", "2025-10-31"],
    "org-vc-vertexminds": ["2025-10-31", "2025-11-10", "2025-11-20"],
}
TEMPORAL_CORPORA = set(CUTOFFS)


class Report:
    def __init__(self, name: str) -> None:
        self.name = name
        self.errors: list[str] = []
        self.warns: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warns.append(msg)

    def dump(self) -> None:
        for w in self.warns:
            print(f"  WARN  [{self.name}] {w}")
        for e in self.errors:
            print(f"  ERROR [{self.name}] {e}")


def _is_iso_date(s: object) -> bool:
    if not isinstance(s, str) or len(s) != 10 or s[4] != "-" or s[7] != "-":
        return False
    try:
        y, m, d = int(s[0:4]), int(s[5:7]), int(s[8:10])
    except ValueError:
        return False
    return 1 <= m <= 12 and 1 <= d <= 31 and y >= 1000


def _load_jsonl(path: Path, rep: Report) -> list[dict]:
    rows: list[dict] = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            rep.error(f"{path.name}:{i} invalid JSON ({exc})")
            continue
        if not isinstance(obj, dict):
            rep.error(f"{path.name}:{i} line is not a JSON object")
            continue
        rows.append(obj)
    return rows


def _load_tsv(path: Path, header: list[str], rep: Report) -> list[list[str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        rep.error(f"{path.name} is empty")
        return []
    if lines[0].split("\t") != header:
        rep.error(f"{path.name} header must be {header!r}, got {lines[0]!r}")
        return []
    out: list[list[str]] = []
    for i, line in enumerate(lines[1:], 2):
        if not line.strip():
            continue
        cells = line.split("\t")
        if len(cells) != len(header):
            rep.error(f"{path.name}:{i} expected {len(header)} tab-separated cols, got {len(cells)}")
            continue
        out.append(cells)
    return out


def validate_corpus(root: Path) -> Report:
    cid = root.name
    rep = Report(cid)

    if not (root / "corpus.jsonl").exists():
        rep.error("missing corpus.jsonl")
        return rep

    corpus_ids: set[str] = set()
    created: dict[str, str] = {}
    for obj in _load_jsonl(root / "corpus.jsonl", rep):
        _id = obj.get("_id")
        if isinstance(_id, str):
            corpus_ids.add(_id)
            meta = obj.get("metadata") or {}
            if isinstance(meta, dict) and _is_iso_date(meta.get("created")):
                created[_id] = meta["created"]

    query_ids: set[str] = set()
    temporal_qtime: dict[str, str] = {}
    for obj in _load_jsonl(root / "queries.jsonl", rep):
        qid = obj.get("_id")
        if not isinstance(qid, str):
            continue
        query_ids.add(qid)
        meta = obj.get("metadata") or {}
        if not isinstance(meta, dict):
            rep.error(f"queries.jsonl: {qid} metadata is not an object")
            continue
        qt, ti = meta.get("query_time"), meta.get("temporal_intent")
        if qt is not None or ti is not None:
            if not _is_iso_date(qt):
                rep.error(f"queries.jsonl: {qid} query_time must be ISO date, got {qt!r}")
            if ti not in TEMPORAL_INTENT:
                rep.error(f"queries.jsonl: {qid} temporal_intent {ti!r} not in {sorted(TEMPORAL_INTENT)}")
            else:
                temporal_qtime[qid] = qt if _is_iso_date(qt) else ""
            if cid not in TEMPORAL_CORPORA:
                rep.warn(f"queries.jsonl: {qid} has temporal fields but {cid} is not a temporal corpus")

    cutoffs = CUTOFFS.get(cid, [])

    # ---- qrels base + time-sliced -----------------------------------------
    qrels_dir = root / "qrels"
    trap_zero: set[tuple[str, str]] = set()

    def check_qrels(path: Path, tag: str | None) -> None:
        for qid, doc, score in _load_tsv(path, ["query-id", "corpus-id", "score"], rep):
            if qid not in query_ids:
                rep.error(f"{path.name}: query-id {qid!r} not in queries.jsonl")
            if doc not in corpus_ids:
                rep.error(f"{path.name}: corpus-id {doc!r} not in corpus.jsonl")
            if score not in {"0", "1", "2", "3"}:
                rep.error(f"{path.name}: score {score!r} for {qid} not in 0..3")
            if tag is None and score == "0":
                trap_zero.add((qid, doc))
            if tag is not None and doc in created and created[doc] > tag:
                rep.error(f"{path.name}: {doc} (created {created[doc]}) appears in slice {tag} before it exists")

    if (qrels_dir / "test.tsv").exists():
        check_qrels(qrels_dir / "test.tsv", None)
    else:
        rep.error("missing qrels/test.tsv")

    slice_files = sorted(qrels_dir.glob("test_t*.tsv")) if qrels_dir.exists() else []
    slice_tags = {p.name[len("test_t"):-len(".tsv")] for p in slice_files}
    for p in slice_files:
        tag = p.name[len("test_t"):-len(".tsv")]
        if cid in TEMPORAL_CORPORA and tag not in cutoffs:
            rep.error(f"{p.name}: tag {tag!r} is not a declared cutoff {cutoffs}")
        check_qrels(p, tag if _is_iso_date(tag) else None)
    if cid in TEMPORAL_CORPORA and slice_files:
        missing = [c for c in cutoffs if c not in slice_tags]
        if missing:
            rep.warn(f"time-sliced qrels present but missing cutoffs {missing}")

    # ---- annotations/ ------------------------------------------------------
    ann = root / "annotations"

    ds_path = ann / "doc_state.jsonl"
    if ds_path.exists():
        if cid not in TEMPORAL_CORPORA:
            rep.error("doc_state.jsonl present but corpus has no temporal cutoffs")
        for obj in _load_jsonl(ds_path, rep):
            _id = obj.get("_id")
            if _id not in corpus_ids:
                rep.error(f"doc_state.jsonl: _id {_id!r} not in corpus.jsonl")
            if not (_is_iso_date(obj.get("valid_from"))):
                rep.error(f"doc_state.jsonl: {_id} valid_from must be ISO date")
            vu = obj.get("valid_until", None)
            if vu is not None and not _is_iso_date(vu):
                rep.error(f"doc_state.jsonl: {_id} valid_until must be ISO date or null")
            if _is_iso_date(obj.get("valid_from")) and _is_iso_date(vu) and not vu > obj["valid_from"]:
                rep.error(f"doc_state.jsonl: {_id} valid_until must be > valid_from")
            lbc = obj.get("lifecycle_by_cutoff")
            if not isinstance(lbc, dict):
                rep.error(f"doc_state.jsonl: {_id} lifecycle_by_cutoff must be an object")
                continue
            if set(lbc) != set(cutoffs):
                rep.error(f"doc_state.jsonl: {_id} cutoff keys {sorted(lbc)} != {cutoffs}")
            seen_obsolete = False
            for c in cutoffs:
                st = lbc.get(c)
                if st is not None and st not in LIFECYCLE:
                    rep.error(f"doc_state.jsonl: {_id} lifecycle {st!r} at {c} not in vocabulary")
                if st in OBSOLETE:
                    seen_obsolete = True
                elif seen_obsolete and st is not None:
                    rep.warn(f"doc_state.jsonl: {_id} resurrects from obsolete to {st!r} at {c}")

    edges_path = ann / "edges.jsonl"
    if edges_path.exists():
        for obj in _load_jsonl(edges_path, rep):
            src, dst, rel, pol = obj.get("src"), obj.get("dst"), obj.get("relation"), obj.get("polarity")
            if src not in corpus_ids:
                rep.error(f"edges.jsonl: src {src!r} not in corpus.jsonl")
            if dst not in corpus_ids:
                rep.error(f"edges.jsonl: dst {dst!r} not in corpus.jsonl")
            if src == dst:
                rep.error(f"edges.jsonl: self-loop on {src!r}")
            if rel not in REL_POLARITY:
                rep.error(f"edges.jsonl: relation {rel!r} not in vocabulary")
            elif pol != REL_POLARITY[rel]:
                rep.error(f"edges.jsonl: relation {rel!r} requires polarity {REL_POLARITY[rel]!r}, got {pol!r}")

    stance_path = ann / "stance.tsv"
    if stance_path.exists():
        for qid, st in _load_tsv(stance_path, ["query-id", "gold_stance"], rep):
            if qid not in query_ids:
                rep.error(f"stance.tsv: query-id {qid!r} not in queries.jsonl")
            if st not in STANCE:
                rep.error(f"stance.tsv: gold_stance {st!r} not in {sorted(STANCE)}")

    traps_path = ann / "traps.tsv"
    if traps_path.exists():
        for qid, doc in _load_tsv(traps_path, ["query-id", "corpus-id"], rep):
            if qid not in query_ids:
                rep.error(f"traps.tsv: query-id {qid!r} not in queries.jsonl")
            if doc not in corpus_ids:
                rep.error(f"traps.tsv: corpus-id {doc!r} not in corpus.jsonl")
            elif (qid, doc) not in trap_zero:
                rep.error(f"traps.tsv: ({qid},{doc}) must be scored 0 in qrels/test.tsv")

    return rep


def main(argv: list[str]) -> int:
    here = Path(__file__).resolve().parent.parent
    if argv:
        roots = [Path(a) for a in argv]
    else:
        roots = sorted((here / "corpora").iterdir())
    roots = [r for r in roots if (r / "corpus.jsonl").exists()]
    if not roots:
        print("no corpora found")
        return 1

    total_err = 0
    for root in roots:
        rep = validate_corpus(root)
        status = "FAIL" if rep.errors else "OK"
        print(f"[{status}] {rep.name}  ({len(rep.errors)} errors, {len(rep.warns)} warns)")
        rep.dump()
        total_err += len(rep.errors)

    print("\n" + ("OK — no errors" if total_err == 0 else f"FAILED — {total_err} error(s)"))
    return 0 if total_err == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
