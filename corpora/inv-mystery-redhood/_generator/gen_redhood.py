#!/usr/bin/env python3
"""
gen_redhood.py — deterministic scale-up generator for the inv-mystery-redhood corpus.

Extends the hand-authored 30-document "toy" corpus into larger tiers
(medium / big / very big / huge / very huge) by adding two kinds of synthetic
documents around the *unchanged* canonical 30:

  - DISTRACTORS ("dist"): high-similarity / epistemically-disqualified traps.
      Same vocabulary as the gold queries (Marta, Old Mill, dark shape, canid,
      parcel, honey, tincture, debt, rough voice, forced latch, red scarf...)
      but wrong entity / wrong time / wrong place / unverified — so a pure
      similarity retriever pulls them while an epistemically-grounded system
      (OIDA) rejects them. They never contradict the gold; they are simply not
      part of the causal chain of the 13 Oct 1842 attack on Marta Bellandi.

  - NOISE ("noise"): pure off-topic, era-coherent village paperwork
      (markets, weather, school, recipes, taxes, harvest, livestock...).

A small band of CONTEXT ("ctx") documents provides mundane, non-probative
world-building (often mentioning real case entities in ordinary ways).

Invariants enforced by construction
------------------------------------
  * The canonical 30 (source_001..source_030) are copied VERBATIM — their _id
    must stay stable because qrels/test.tsv references them.
  * Time only moves forward and is internally consistent:
      - retrospective documents (witness/medical/incident/report/receipt/ledger)
        carry TIMESTAMP >= the event time they report; any explicit clock time
        in the body is < the document TIMESTAMP.
      - prospective documents (notices/forecasts/schedules) are issued BEFORE
        the scheduled event they announce (as in the toy weather/market notices).
  * All dates are valid calendar dates (1842 is not a leap year -> Feb = 28).

Usage:
    python3 gen_redhood.py <tier>
    where <tier> in {medium, big, "very big", "very_big", huge, "very huge", "very_huge"}

Output:
    ../raw_<tier>_sized/source_*.md   (canonical + generated)
    ./manifests/manifest_<tier>.json  (composition + time-range audit)
"""

import sys, os, json, random, shutil, zlib
from datetime import datetime, timedelta

SEED = 20261015
HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS_DIR = os.path.dirname(HERE)
TOY_DIR = os.path.join(CORPUS_DIR, "raw_toy_sized")
MANIFEST_DIR = os.path.join(HERE, "manifests")

# tier -> (folder_name, total_docs, noise_frac, distractor_frac)
TIERS = {
    "medium":     ("raw_medium_sized",      300,        0.25, 0.35),
    "big":        ("raw_big_sized",        3_000,       0.35, 0.40),
    "very_big":   ("raw_very big_sized",   30_000,      0.45, 0.42),
    "huge":       ("raw_huge_sized",       300_000,     0.52, 0.43),
    "very_huge":  ("raw_very huge_sized",  3_000_000,   0.57, 0.42),
}
TIER_ALIASES = {"very big": "very_big", "verybig": "very_big",
                "very huge": "very_huge", "veryhuge": "very_huge"}

# Output mode per tier:
#   md_flat       -> individual .md files in the tier folder (toy-identical)
#   md_sharded    -> individual .md files in navigable subfolders part-NNNN/
#   jsonl_sharded -> packed shards part-NNNN.jsonl, one JSON record per line,
#                    SAME fields as the .md (kept for the 3M tier to avoid the
#                    ~11 GB block-size overhead of millions of tiny files).
OUTPUT_MODE = {
    "medium": "md_flat", "big": "md_flat", "very_big": "md_flat",
    "huge": "md_sharded", "very_huge": "jsonl_sharded",
}
SHARD_SIZE = 10_000


def parse_md(content):
    """Parse a rendered .md document back into a structured record."""
    head, _, text = content.partition("\nTEXT:\n")
    f = {}
    for line in head.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            f[k.strip()] = v.strip()
    return {
        "source_id": f["SOURCE_ID"], "source_type": f["SOURCE_TYPE"],
        "author": f["AUTHOR"], "recipient": f["RECIPIENT"],
        "timestamp": f["TIMESTAMP"], "location": f["LOCATION"],
        "reliability_prior": float(f["RELIABILITY_PRIOR"]),
        "text": text.rstrip("\n"),
    }

# ----------------------------------------------------------------------------
# Calendar helpers (1842, non-leap)
# ----------------------------------------------------------------------------
DAYS_IN_MONTH = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}

def valid_date(year, month, day):
    dim = DAYS_IN_MONTH[month] if year == 1842 else (
        29 if (month == 2 and year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else DAYS_IN_MONTH[month])
    day = min(day, dim)
    return year, month, day

def iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S")

# ----------------------------------------------------------------------------
# Slot pools
# ----------------------------------------------------------------------------
# Canonical case entities (used by context + same-entity distractors)
CASE_PEOPLE = ["Marta Bellandi", "Clara Vieri", "Ada Vieri", "Pietro Lanza",
               "Enrico Sarti", "Dr. Tommaso Grevi", "Nino Falchi", "Sofia Rinaldi",
               "Carlo Fenzi", "Rinaldo Marchi", "Lucia Berti", "Livia Ferri"]

# Unrelated villagers (noise + look-alike distractors). Includes deliberate
# near-name collisions (a different Marta / Clara / Bruno) as entity-linking traps.
OTHER_PEOPLE = [
    "Bruno Tessari", "Marta Conti", "Clara Fabbri", "Giulio Beneventi",
    "Anselmo Riva", "Teresa Galli", "Matteo Donati", "Renata Sciarra",
    "Osvaldo Pini", "Camilla Roveri", "Fausto Lamberti", "Ilaria Negri",
    "Gualtiero Massi", "Pia Venturi", "Severino Cau", "Brigida Moretti",
    "Ettore Salvi", "Noemi Bracci", "Corrado Tinti", "Vanda Lippi",
    "Aldo Persichetti", "Marisa Quaranta", "Bruno Marchi", "Clara Vieri the elder",
    "Tobia Greve", "Marta the weaver", "Doctor Greco", "Ranger Bisi",
]

CASE_PLACES = ["Old Mill", "Old Mill Road", "Birch Crossing", "Northwood",
               "Bellandi Cottage", "Chapel Road", "Village Square", "Lanza Bakery",
               "Council House", "Southern Bridge", "Village Center", "Village Edge"]

OTHER_PLACES = [
    "Castelrosso", "Valmorra", "Pietraforte", "Borgosecco", "Cedar Hollow",
    "East Ford", "Stone Bridge", "the Lower Marsh", "Vetrano", "Colle Sereno",
    "the Hazel Wood", "Tannery Lane", "the West Quarry", "Fontechiara",
    "the Drovers' Road", "Sant'Eligio", "the Salt Track", "Roccaverde",
]

CANID_WORDS = ["large canid", "gray wolf", "stray mastiff", "wild dog",
               "great hound", "lean wolf-dog", "shaggy beast"]
SHAPE_WORDS = ["a dark shape", "a low silhouette", "a hunched figure",
               "a crouching form", "a tall shadow", "something pale and quick"]
GOODS = ["honey jar", "loaf of rye", "brown cloth wrap", "sealed vial of tincture",
         "bundle of thyme", "coil of rope", "lantern", "wool blanket", "jar of lard"]
NOISE_GOODS = ["chestnuts", "flour", "dried apples", "wool", "salt fish",
               "tallow candles", "linen", "barley", "cured ham", "beeswax"]

# (source_type, reliability_lo, reliability_hi)
def rel(lo, hi, rng):
    return round(rng.uniform(lo, hi), 2)

BELLS = ["first bell", "second bell", "third bell", "second afternoon bell",
         "evening bell", "the noon bell"]

# ----------------------------------------------------------------------------
# Document rendering
# ----------------------------------------------------------------------------
def render(source_id, source_type, author, recipient, ts, location, reliability, body):
    return (
        f"SOURCE_ID: {source_id}\n"
        f"SOURCE_TYPE: {source_type}\n"
        f"AUTHOR: {author}\n"
        f"RECIPIENT: {recipient}\n"
        f"TIMESTAMP: {iso(ts)}\n"
        f"LOCATION: {location}\n"
        f"RELIABILITY_PRIOR: {reliability}\n\n"
        f"TEXT:\n{body}\n"
    )

# ----------------------------------------------------------------------------
# Date pickers (coherent distributions)
# ----------------------------------------------------------------------------
def pick_event_dt(rng, profile):
    """Return a plausible *event* datetime for a generated doc.
    profile drives where in time the event sits relative to the case."""
    if profile == "distractor":
        r = rng.random()
        if r < 0.55:            # autumn 1842, around the case month
            month = rng.choice([9, 10, 10, 11])
            day = rng.randint(1, 28)
            year = 1842
        elif r < 0.85:          # elsewhere in 1842
            month = rng.randint(1, 12); day = rng.randint(1, 28); year = 1842
        else:                   # "old stories" — prior years
            year = rng.choice([1839, 1840, 1841]); month = rng.randint(1, 12); day = rng.randint(1, 28)
    elif profile == "context":
        # mostly the case fortnight (Oct 1842) and surrounding weeks
        r = rng.random()
        if r < 0.7:
            month = 10; day = rng.randint(1, 28); year = 1842
        else:
            month = rng.choice([9, 11]); day = rng.randint(1, 28); year = 1842
    else:  # noise — spread across all 1842
        month = rng.randint(1, 12); day = rng.randint(1, 28); year = 1842
    year, month, day = valid_date(year, month, day)
    hour = rng.randint(6, 21)
    minute = rng.randint(0, 59)
    return datetime(year, month, day, hour, minute, rng.randint(0, 59))

# ----------------------------------------------------------------------------
# Template families. Each returns (source_type, author, recipient, location,
# reliability, body, tense) where tense in {past, notice, neutral}.
#   past   -> retrospective; TIMESTAMP placed AFTER event (event clock < ts)
#   notice -> prospective;   TIMESTAMP is issuance, BEFORE the announced event
#   neutral-> authored at TIMESTAMP (letters/notes about plans or mundane facts)
# ----------------------------------------------------------------------------

def t_distractor(rng):
    person = rng.choice(CASE_PEOPLE + OTHER_PEOPLE)
    other = rng.choice(OTHER_PEOPLE)
    place = rng.choice(OTHER_PLACES)
    case_place = rng.choice(CASE_PLACES)
    canid = rng.choice(CANID_WORDS)
    shape = rng.choice(SHAPE_WORDS)
    good = rng.choice(GOODS)
    bell = rng.choice(BELLS)
    kind = rng.randint(0, 11)

    if kind == 0:  # other canid sighting, wrong place/time
        return ("ranger_log", rng.choice(["Enrico Sarti", "Ranger Bisi", "Forest Warden"]),
                "Municipal Archive", place, rel(0.62, 0.80, rng),
                f"Tracks of a {canid} near {place}, well away from the Old Mill road. "
                f"Direction toward the open fields. Noted earlier today; logged after returning to the station. "
                f"No livestock harmed. Unrelated to the birch crossing reports.", "past")
    if kind == 1:  # other dark-shape witness, wrong locus
        return ("witness_statement", rng.choice(OTHER_PEOPLE), "Municipal Guard", place,
                rel(0.50, 0.70, rng),
                f"I saw {shape} near {place} before the {bell}. I thought it a man in a cloak. "
                f"It moved off toward the hills. I cannot say it had anything to do with the Bellandi matter.", "past")
    if kind == 2:  # other debt quarrel (motive red herring, other people)
        return ("rumor_account", rng.choice(["Lucia Berti", "Valdombra Gazette", rng.choice(OTHER_PEOPLE)]),
                "Public", rng.choice(OTHER_PLACES + ["Lucia's Inn"]),
                rel(0.40, 0.55, rng),
                f"They say {other} and {rng.choice(OTHER_PEOPLE)} came to blows over an old debt at {place}. "
                f"Money makes men foolish. Some at the inn tie every quarrel back to the Old Mill, but this one is its own affair.", "neutral")
    if kind == 3:  # other forced-latch / cottage disturbance elsewhere
        return ("official_report", "Municipal Guard", "Village Council", place,
                rel(0.74, 0.86, rng),
                f"A cottage at {place} reported its rear latch lifted overnight. Suspected foxes or wind; no entry, nothing taken. "
                f"No connection established to the {case_place} case.", "past")
    if kind == 4:  # other parcel with honey/tincture (object collision)
        return ("receipt", rng.choice(["Pietro Lanza", rng.choice(OTHER_PEOPLE)]),
                rng.choice(OTHER_PEOPLE), rng.choice(["Lanza Bakery"] + OTHER_PLACES),
                rel(0.74, 0.86, rng),
                f"Receipt: one {good}, two small loaves, one brown cloth wrap, one sealed vial. "
                f"Collected by {other}. A common order this season.", "neutral")
    if kind == 5:  # entity-collision: a different Marta/Clara/Bruno
        twin = rng.choice(["Marta Conti", "Clara Fabbri", "Bruno Tessari", "Bruno Marchi", "Clara Vieri the elder"])
        return ("administrative_record", "Village Clerk", "Municipal Archive", place,
                rel(0.78, 0.88, rng),
                f"{twin} of {place} registered for the autumn grain allotment. "
                f"Not to be confused with the Bellandi household; different parish, different person.", "neutral")
    if kind == 6:  # rough-voice / impersonation anecdote elsewhere
        return ("witness_statement", rng.choice(OTHER_PEOPLE), "Municipal Guard", place,
                rel(0.52, 0.70, rng),
                f"At {place} I heard a rough voice from a shuttered room and thought someone ill. "
                f"It was only old {rng.choice(OTHER_PEOPLE)} with a winter cough. Nothing strange after all.", "past")
    if kind == 7:  # alibi/toll for someone else
        return ("administrative_record", "Bridge Toll Keeper", "Municipal Archive",
                rng.choice(["Stone Bridge", "East Ford", "Southern Bridge"]),
                rel(0.70, 0.80, rng),
                f"{other} crossed with two cloth bundles. Toll paid in copper. Entry time approximate; "
                f"line smudged. Routine traffic.", "past")
    if kind == 8:  # old beast-legend (historical distractor)
        return ("local_news", "Valdombra Gazette", "Public", "Valdombra",
                rel(0.45, 0.58, rng),
                f"Elders again recall the Northwood beast of years past, when a {canid} was blamed for losses near {place}. "
                f"Old tales, no proof, and nothing tying them to present events.", "neutral")
    if kind == 9:  # red scarf / clothing collision
        return ("witness_statement", rng.choice(OTHER_PEOPLE), "Municipal Guard", place,
                rel(0.45, 0.65, rng),
                f"A girl in a dark red scarf passed through {place}. Many girls wear such scarves this autumn. "
                f"I paid it no mind.", "past")
    if kind == 10:  # birch-crossing mention, mundane
        return ("private_note", rng.choice(CASE_PEOPLE + OTHER_PEOPLE), rng.choice(OTHER_PEOPLE),
                "Birch Crossing", rel(0.55, 0.72, rng),
                f"Mended the fence by the birch crossing and cleared the ditch. The fog there is bad after midday. "
                f"Left a marker so the carts keep to the firm side.", "neutral")
    # kind == 11: same-entity but non-probative (Marta in an ordinary earlier moment)
    return ("private_note", rng.choice(["Ada Vieri", "Marta Bellandi", "Clara Vieri"]),
            rng.choice(CASE_PEOPLE), rng.choice(CASE_PLACES), rel(0.60, 0.78, rng),
            f"Marta asked for thyme and honey again; her cough lingers. Clara will carry the small things over when she can. "
            f"An ordinary errand, nothing more.", "neutral")


def t_context(rng):
    person = rng.choice(CASE_PEOPLE)
    place = rng.choice(CASE_PLACES)
    kind = rng.randint(0, 6)
    if kind == 0:
        return ("ranger_log", "Enrico Sarti", "Municipal Archive", "Northwood", rel(0.74, 0.82, rng),
                f"Quiet patrol along {place}. No fresh tracks of note. Repaired a marker post and noted the path is firm.", "past")
    if kind == 1:
        return ("administrative_record", "Village Clerk", "Municipal Archive", "Council House", rel(0.78, 0.88, rng),
                f"Routine ledger entry: lamp oil and rope issued for the week. Signed and filed in order.", "past")
    if kind == 2:
        return ("private_letter", rng.choice(CASE_PEOPLE), rng.choice(CASE_PEOPLE), place, rel(0.70, 0.82, rng),
                f"All is well enough here. The market was busy and the chapel repairs drag on. "
                f"Write when you can; the evenings grow cold.", "neutral")
    if kind == 3:
        return ("parish_notice", "Parish Office", "Public Notice Board", "Chapel Road", rel(0.84, 0.90, rng),
                f"Service times stand as usual this week, conditions permitting. The bell repair continues; "
                f"do not rely on it for the hour.", "notice")
    if kind == 4:
        return ("weather_bulletin", "Weather Clerk", "Public Notice Board", "Council House", rel(0.84, 0.90, rng),
                f"Patchy fog likely in the low parts of Northwood after midday. Main road expected clear.", "notice")
    if kind == 5:
        return ("witness_statement", rng.choice(CASE_PEOPLE), "Municipal Guard", place, rel(0.58, 0.74, rng),
                f"I passed through {place} earlier and saw nothing unusual at the time. People went about the market as always.", "past")
    return ("private_note", person, "Personal Papers", place, rel(0.62, 0.78, rng),
            f"A plain note of the day's errands near {place}: bread, oil, a word with the baker. Nothing to remark.", "neutral")


def t_noise(rng):
    place = rng.choice(CASE_PLACES + OTHER_PLACES)
    good = rng.choice(NOISE_GOODS)
    person = rng.choice(OTHER_PEOPLE)
    kind = rng.randint(0, 9)
    if kind == 0:
        return ("market_notice", "Market Office", "Public", "Village Square", rel(0.86, 0.92, rng),
                f"The weekly market will offer {good} and {rng.choice(NOISE_GOODS)}. Vendors should arrive before the second bell. "
                f"Cart traffic may be heavier than usual.", "notice")
    if kind == 1:
        return ("weather_bulletin", "Weather Clerk", "Public Notice Board", "Council House", rel(0.84, 0.90, rng),
                f"Clear skies expected, with a cold wind from the north toward evening. No rain anticipated.", "notice")
    if kind == 2:
        return ("school_notice", "Agnese Conti", "Parents of Valdombra", "Schoolhouse", rel(0.82, 0.88, rng),
                f"Lessons will run as usual. Please return the rehearsal costumes by week's end and keep children clear of the cart lane.", "notice")
    if kind == 3:
        return ("personal_recipe_card", person, "Personal Papers", place, rel(0.68, 0.76, rng),
                f"Remedy: honey, thyme, hot water, two drops of bitter root. Do not boil after adding the tincture. Keeps a week.", "neutral")
    if kind == 4:
        return ("administrative_record", "Village Clerk", "Municipal Archive", "Council House", rel(0.80, 0.90, rng),
                f"Tax roll: {person} settled the autumn levy in copper. Entry filed and witnessed. Accounts in order.", "past")
    if kind == 5:
        return ("administrative_record", "Census Officer", "Municipal Archive", place, rel(0.80, 0.90, rng),
                f"Livestock count at {place}: goats, two; fowl, eleven; one mule. No change from last quarter.", "past")
    if kind == 6:
        return ("market_notice", "Harvest Committee", "Public", "Village Square", rel(0.82, 0.90, rng),
                f"Harvest preparations continue. Carts of {good} will gather at dawn. Hands are needed for the threshing floor.", "notice")
    if kind == 7:
        return ("receipt", person, rng.choice(OTHER_PEOPLE), place, rel(0.74, 0.84, rng),
                f"Receipt: {rng.randint(1,6)} measures of {good}, paid in full. Goods collected the same day.", "neutral")
    if kind == 8:
        return ("parish_notice", "Parish Office", "Public Notice Board", "Chapel Road", rel(0.84, 0.90, rng),
                f"A blessing of the harvest will be held after services. The fountain repairs near the square are nearly complete.", "notice")
    return ("local_news", "Valdombra Gazette", "Public", "Valdombra", rel(0.50, 0.62, rng),
            f"In brief: the bridge toll rises a copper next month; the chestnut crop is good; a new well is dug at {place}.", "neutral")


# ----------------------------------------------------------------------------
# Timestamp assignment honoring tense
# ----------------------------------------------------------------------------
def assign_timestamp(rng, event_dt, tense):
    """Return (timestamp_dt, body_suffix) enforcing forward-time coherence."""
    if tense == "past":
        # event already happened; document written minutes..hours later (same/next day)
        delta = timedelta(minutes=rng.choice([15, 25, 40, 70, 120, 180, 300]))
        ts = event_dt + delta
        # explicit clock reference < ts, demonstrating the invariant
        suffix = f" (event observed about {event_dt.strftime('%H:%M')}; recorded at {ts.strftime('%H:%M')}.)"
        return ts, suffix
    if tense == "notice":
        # issuance precedes the announced event by hours
        lead = timedelta(hours=rng.choice([2, 3, 5, 8]))
        ts = event_dt - lead
        return ts, ""
    # neutral: authored at the event datetime
    return event_dt, ""

# ----------------------------------------------------------------------------
# Main build
# ----------------------------------------------------------------------------
def read_canonical():
    """Return list of (filename, content) for the canonical 30, sorted."""
    out = []
    for fn in sorted(os.listdir(TOY_DIR)):
        if fn.endswith(".md"):
            with open(os.path.join(TOY_DIR, fn)) as fh:
                out.append((fn, fh.read()))
    return out

def build(tier_key):
    folder, total, noise_frac, dist_frac = TIERS[tier_key]
    dest = os.path.join(CORPUS_DIR, folder)
    os.makedirs(dest, exist_ok=True)
    os.makedirs(MANIFEST_DIR, exist_ok=True)
    mode = OUTPUT_MODE[tier_key]
    sharded = mode in ("md_sharded", "jsonl_sharded")
    jsonl = mode == "jsonl_sharded"

    # clear any prior content (stale .md/.jsonl at root and old shard dirs)
    for entry in os.listdir(dest):
        p = os.path.join(dest, entry)
        if (entry.endswith(".md") or entry.endswith(".jsonl")) and os.path.isfile(p):
            os.remove(p)
        elif entry.startswith("part-") and os.path.isdir(p):
            shutil.rmtree(p)

    # stable per-tier seed (zlib.crc32 is not salted, unlike str hash()),
    # so re-running reproduces byte-identical corpora.
    rng = random.Random(SEED ^ (zlib.crc32(tier_key.encode()) & 0xFFFFFFFF))

    canon = read_canonical()
    n_canon = len(canon)
    n_noise = round(total * noise_frac)
    n_dist = round(total * dist_frac)
    n_ctx = total - n_canon - n_noise - n_dist
    if n_ctx < 0:
        n_dist += n_ctx
        n_ctx = 0

    plan = (["dist"] * n_dist) + (["noise"] * n_noise) + (["ctx"] * n_ctx)
    rng.shuffle(plan)

    tmin = datetime(9999, 1, 1)
    tmax = datetime(1, 1, 1)
    counts = {"canonical": n_canon, "dist": 0, "noise": 0, "ctx": 0}

    # writer: flat .md, sharded .md (part-NNNN/file.md), or sharded jsonl
    # (part-NNNN.jsonl, one record per line). Global index drives shard rotation.
    state = {"shard": -1, "dir": dest, "fh": None}
    def write_doc(gi, fname, content, record):
        shard = gi // SHARD_SIZE
        if jsonl:
            if shard != state["shard"]:
                if state["fh"]:
                    state["fh"].close()
                state["shard"] = shard
                state["fh"] = open(os.path.join(dest, f"part-{shard:04d}.jsonl"), "w")
            state["fh"].write(json.dumps(record, ensure_ascii=False) + "\n")
            return
        if sharded:
            if shard != state["shard"]:
                state["shard"] = shard
                state["dir"] = os.path.join(dest, f"part-{shard:04d}")
                os.makedirs(state["dir"], exist_ok=True)
            path = os.path.join(state["dir"], fname)
        else:
            path = os.path.join(dest, fname)
        with open(path, "w") as fh:
            fh.write(content)

    gi = 0
    # canonical first (land in part-0000 when sharded); content/fields verbatim
    for fn, content in canon:
        write_doc(gi, fn, content, parse_md(content))
        gi += 1

    seq = 31
    for cls in plan:
        if cls == "dist":
            st, author, recip, loc, reliab, body, tense = t_distractor(rng)
            profile = "distractor"
        elif cls == "noise":
            st, author, recip, loc, reliab, body, tense = t_noise(rng)
            profile = "noise"
        else:
            st, author, recip, loc, reliab, body, tense = t_context(rng)
            profile = "context"

        event_dt = pick_event_dt(rng, profile)
        ts, suffix = assign_timestamp(rng, event_dt, tense)
        if suffix:
            body = body + suffix

        slug = st.replace("_", "-")
        source_id = f"source_{seq:07d}_{cls}_{slug}"
        fname = source_id + ".md"
        doc = render(source_id, st, author, recip, ts, loc, reliab, body)
        record = {"source_id": source_id, "source_type": st, "author": author,
                  "recipient": recip, "timestamp": iso(ts), "location": loc,
                  "reliability_prior": reliab, "text": body}
        write_doc(gi, fname, doc, record)

        counts[cls] += 1
        if ts < tmin: tmin = ts
        if ts > tmax: tmax = ts
        seq += 1
        gi += 1

    if state["fh"]:
        state["fh"].close()

    manifest = {
        "tier": tier_key,
        "folder": folder,
        "total_documents": n_canon + counts["dist"] + counts["noise"] + counts["ctx"],
        "composition": counts,
        "fractions": {
            "noise_pct": round(100 * counts["noise"] / total, 2),
            "distractor_pct": round(100 * counts["dist"] / total, 2),
            "context_pct": round(100 * counts["ctx"] / total, 2),
            "canonical_pct": round(100 * counts["canonical"] / total, 2),
        },
        "timestamp_range": {"min": iso(tmin), "max": iso(tmax)},
        "output_mode": mode,
        "shard_size": SHARD_SIZE if sharded else None,
        "num_shards": ((n_canon + counts["dist"] + counts["noise"] + counts["ctx"] + SHARD_SIZE - 1) // SHARD_SIZE) if sharded else None,
        "seed": SEED,
        "note": "canonical source_001..source_030 copied verbatim from raw_toy_sized; "
                "qrels/test.tsv references only the canonical ids.",
    }
    with open(os.path.join(MANIFEST_DIR, f"manifest_{tier_key}.json"), "w") as fh:
        json.dump(manifest, fh, indent=2)
    return manifest

def main():
    if len(sys.argv) < 2:
        print("usage: gen_redhood.py <tier>", file=sys.stderr); sys.exit(2)
    raw = " ".join(sys.argv[1:]).strip().lower()
    key = TIER_ALIASES.get(raw, raw.replace(" ", "_"))
    if key not in TIERS:
        print(f"unknown tier '{raw}'. choices: {list(TIERS)}", file=sys.stderr); sys.exit(2)
    m = build(key)
    print(json.dumps(m, indent=2))

if __name__ == "__main__":
    main()
