# Ashford County Epistemic Benchmark — Clean Scenario v0.1

A multi-source investigative corpus designed to test whether a knowledge-extraction system can perform **cross-incident pattern clustering** while correctly isolating an outlier event that superficially appears to belong to the cluster.

This benchmark is structurally a sibling of the Red Hood Epistemic Benchmark, but addresses a gap in Red Hood's design: Red Hood tests single-incident culprit identification with a single causal chain. This benchmark tests **comparative reasoning across four distinct incidents** — three of which share a hidden signature and one of which does not.

---

## The puzzle

Four young men died in Ashford between July 1988 and October 1990. The corpus contains thirty heterogeneous sources distributed across the four cases plus three cross-cutting documents (a newspaper article, a false-lead clearance, and a noise document) and one false-lead witness statement.

The tested system must, using only the sources:

1. Identify the three deaths that share a recurring offender signature.
2. Identify the one death that does not.
3. Identify the most likely killer of the outlier, distinct from the serial offender.
4. Resist a high-circulation newspaper article that misframes all four as a single pattern.
5. Resist a witness statement that places the serial offender's description near the outlier scene (the witness's own dating is internally contradicted).
6. Resist a "photographer suspect" false lead with a verified alibi.

The system must not name the serial offender personally — the corpus does not contain enough to do so. A well-calibrated answer says the offender is an unidentified male matching a recurring description.

---

## What the benchmark exercises

| Capability | How |
|---|---|
| Cross-incident clustering | Pattern markers are distributed across 5 dimensions and 6+ sources; no single source carries the full pattern |
| Anti-pattern recognition | The outlier case has a coherent counter-signature: at-home, manual struggle, ligature not sedation, no theft, known associate, weak alibi |
| Source-reliability gradient | Reliability priors range from 0.38 (unreliable witness) to 0.92 (administrative bulletin) — the highest-reliability source is also the most irrelevant |
| Contradiction handling | Direct contradiction between two witnesses' accounts of the same alibi (Vail says ~6 hours at friend's place; friend says ~2 hours) |
| False-lead resistance | Three deliberate false leads with different failure modes: misframing (newspaper), surface match with verified alibi (Pelham), surface match with self-contradicting witness (Kell) |
| Noise rejection | A high-reliability county-fair bulletin with zero relevance to any case |
| Bounded inference | The strongest physical link to the serial offender (a pawned camera under a fake ID) has its photocopy of the ID lost in a 1991 flood — system should treat as strong but not conclusive |

---

## Structure

```
ashford_benchmark/
  README.md                                # this file
  ground_truth/
    ground_truth.md                        # NOT to be shown to tested systems
  corpus/
    clean/
      source_001_missing_persons_reyes.md
      ...
      source_030_county_fair_bulletin.md   # 30 source files
  metadata/
    source_metadata_clean.json             # per-source roles, reliability, expected salience
```

Every source carries the canonical header:

```
SOURCE_ID:
SOURCE_TYPE:
AUTHOR:
RECIPIENT:
TIMESTAMP:
LOCATION:
RELIABILITY_PRIOR:
TEXT:
```

---

## Notes on design

This corpus was built in response to a critique of an earlier four-file version of the same case: the original version concentrated every signature element into one of four files, which meant a reader who noticed any one dimension was most of the way to the answer. That structure measures pattern recognition, not epistemic reconstruction.

The signature here is distributed across at least six sources per dimension. The outlier case's anti-signature is also distributed (scene report, autopsy, detective's case note). A model that "solves" the puzzle by activating a serial-killer schema rather than by reasoning from the sources should fail to cite the specific evidential chain the gold answer requires.

The benchmark deliberately does not include enough to identify the serial offender personally. A model that names a specific real or fictional individual is over-reaching the evidence.

---

## Recognition-confound risk

The Subject P signature in this corpus (Midwestern industrial setting, gay-bar lure, sedation, photography motif, soft-spoken white man) overlaps with a well-known historical case. A model that pattern-matches to that historical case rather than reasoning from sources is producing the right answer for the wrong reason. To probe this, the recommended evaluation includes:

- Comparing model citations against the actual source distribution. A model reasoning from the corpus will cite specific source IDs and chain them through specific pattern dimensions. A model schema-activating will produce a fluent narrative that does not map back to source IDs.
- Inverting one of the pattern markers in an ablation (e.g., swap rum-and-coke for whiskey-sour) and checking whether the model still produces the same identification — a model reasoning from corpus will update; a model schema-activating may not.

This recognition-confound risk is the principal known weakness of this benchmark and should be foregrounded when reporting results.
