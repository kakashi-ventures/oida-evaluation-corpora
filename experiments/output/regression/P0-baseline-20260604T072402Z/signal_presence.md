# signal_presence.md

Proves the live signals are **non-constant** (roadmap §9 / IC decision #2).
A constant signal is reported as ABSENT.

## Per-query L1 NDCG@10 distribution (per corpus)

| corpus | n_q | min | median | max | spread | non-constant |
|---|---|---|---|---|---|---|
| org-consulting-clearpath | 26 | 0.0000 | 0.4002 | 0.9560 | 0.9560 | True |
| org-iot-fireglass | 20 | 0.1270 | 0.6154 | 0.9652 | 0.8383 | True |
| org-vc-vertexminds | 20 | 0.0321 | 0.5074 | 0.9861 | 0.9540 | True |
| inv-mystery-redhood | 8 | 0.1672 | 0.5615 | 0.6591 | 0.4919 | True |
| inv-ashford-mystery | 5 | 0.0000 | 0.1815 | 0.6160 | 0.6160 | True |

### Sample per-query NDCG@10 (first corpus, up to 12 queries)
`org-consulting-clearpath`: 0.3669, 0.8175, 0.6635, 0.9560, 0.6488, 0.4229, 0.0000, 0.3706, 0.7055, 0.3549, 0.0685, 0.0000

## score_components spread (similarity / regime_adjusted_score)

~3 sampled queries per corpus; spread>0 proves non-constant scoring.

### org-consulting-clearpath
- q01 (n_docs=12): similarity[min=0.4523 max=0.5555 spread=0.1031 nonconst=True] regime_adjusted_score[min=0.4523 max=0.7390 spread=0.2867 nonconst=True]
- q02 (n_docs=15): similarity[min=0.4258 max=0.5407 spread=0.1149 nonconst=True] regime_adjusted_score[min=0.2626 max=0.7326 spread=0.4700 nonconst=True]
- q03 (n_docs=14): similarity[min=0.3764 max=0.5731 spread=0.1967 nonconst=True] regime_adjusted_score[min=0.3764 max=0.6457 spread=0.2693 nonconst=True]

### org-iot-fireglass
- q01 (n_docs=13): similarity[min=0.4469 max=0.6436 spread=0.1967 nonconst=True] regime_adjusted_score[min=0.3178 max=0.9010 spread=0.5832 nonconst=True]
- q02 (n_docs=18): similarity[min=0.3776 max=0.6799 spread=0.3023 nonconst=True] regime_adjusted_score[min=0.3927 max=0.7004 spread=0.3078 nonconst=True]
- q03 (n_docs=19): similarity[min=0.3639 max=0.5051 spread=0.1412 nonconst=True] regime_adjusted_score[min=0.3639 max=0.5523 spread=0.1884 nonconst=True]

### org-vc-vertexminds
- q01 (n_docs=14): similarity[min=0.4628 max=0.7662 spread=0.3034 nonconst=True] regime_adjusted_score[min=0.3509 max=0.8196 spread=0.4686 nonconst=True]
- q02 (n_docs=9): similarity[min=0.4058 max=0.6473 spread=0.2415 nonconst=True] regime_adjusted_score[min=0.3648 max=0.8366 spread=0.4719 nonconst=True]
- q03 (n_docs=11): similarity[min=0.3861 max=0.6510 spread=0.2649 nonconst=True] regime_adjusted_score[min=0.2317 max=0.6510 spread=0.4194 nonconst=True]

### inv-mystery-redhood
- q01 (n_docs=21): similarity[min=0.0978 max=0.3853 spread=0.2875 nonconst=True] regime_adjusted_score[min=0.1035 max=0.5394 spread=0.4359 nonconst=True]
- q02 (n_docs=21): similarity[min=0.1059 max=0.3839 spread=0.2779 nonconst=True] regime_adjusted_score[min=0.1483 max=0.5374 spread=0.3891 nonconst=True]
- q03 (n_docs=20): similarity[min=0.0789 max=0.5310 spread=0.4521 nonconst=True] regime_adjusted_score[min=0.1104 max=0.5310 spread=0.4205 nonconst=True]

### inv-ashford-mystery
- q01 (n_docs=21): similarity[min=0.1266 max=0.3709 spread=0.2444 nonconst=True] regime_adjusted_score[min=0.1266 max=0.3709 spread=0.2444 nonconst=True]
- q02 (n_docs=21): similarity[min=0.0809 max=0.4342 spread=0.3533 nonconst=True] regime_adjusted_score[min=0.0809 max=0.4342 spread=0.3533 nonconst=True]
- q03 (n_docs=21): similarity[min=0.1104 max=0.4603 spread=0.3499 nonconst=True] regime_adjusted_score[min=0.1104 max=0.4603 spread=0.3499 nonconst=True]

## Epistemic signals (dialectic_resolutions / contradiction_edge_count)

**ABSENT pre-Phase-1, by design.** The cross-document epistemic graph is
built in Phase 1; the contradiction path activates in Phase 2. The adapter
retains these fields (P0-S6) but they are empty/zero on the burned corpora
today — reported here as ABSENT, not as a regression.

- org-consulting-clearpath: dialectic_resolutions total=0 (max/q=0), contradiction_edge_count total=0 (max/q=0) -> ABSENT
- org-iot-fireglass: dialectic_resolutions total=0 (max/q=0), contradiction_edge_count total=0 (max/q=0) -> ABSENT
- org-vc-vertexminds: dialectic_resolutions total=0 (max/q=0), contradiction_edge_count total=0 (max/q=0) -> ABSENT
- inv-mystery-redhood: dialectic_resolutions total=0 (max/q=0), contradiction_edge_count total=0 (max/q=0) -> ABSENT
- inv-ashford-mystery: dialectic_resolutions total=0 (max/q=0), contradiction_edge_count total=0 (max/q=0) -> ABSENT
