# OIDA Evaluation Corpora

Companion data for the paper:

> **Retrieval Is Not Enough: Why Organizational AI Needs Epistemic Infrastructure**
>
> Federico Bottino, Carlo Ferrero, Nicholas Dosio, Pierfrancesco Beneventano
>
> [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX)

## Overview

This repository contains the three evaluation corpora used to develop and test the OIDA framework — an epistemic infrastructure for organizational AI that structures knowledge as typed Knowledge Objects with class-specific decay, signed contradiction propagation, and modeled ignorance.

Each corpus is a synthetic but structurally realistic organizational knowledge base, designed to span diverse epistemic situations: binding decisions, open questions, contested hypotheses, contradictory evidence, and evolving plans.

## Corpora

| Corpus | Domain | Description | Files | Size |
|---|---|---|---|---|
| **Caso A** | Consulting / Operations | Process review engagement for a compliance firm (ClearPath Solutions) | 46 | 318 KB |
| **Caso B** | IoT / Product Development | Cloud platform build for a smart fire-resistant window manufacturer (FireGlass) | 47 | 566 KB |
| **Caso C** | Venture Capital | Investment committee deliberation for a demo day event (Vertex Minds) | 77 | 376 KB |

Caso A ("ClearPath") is the primary evaluation corpus referenced in the paper's Brook vs. Cowork comparison (Section 4.2).

## Document Categories

Each corpus is organized into eight categories reflecting typical organizational knowledge sources:

| # | Category | Content |
|---|---|---|
| 01 | `scope` | Project briefs, requirements, statements of work |
| 02 | `subject` | Domain observations, process maps, technical documentation |
| 03 | `internal-comms` | Internal emails and Slack channels |
| 04 | `external-comms` | Client-facing emails and Slack channels |
| 05 | `meetings` | Meeting notes, reviews, workshops |
| 06 | `market-context` | Industry reports, competitive analysis, market data |
| 07 | `documents` | Formal deliverables, proposals, reports |
| 08 | `agenda` | Calendar events, sprint timelines, schedules |

## File Formats

- `.md` — Markdown documents (emails, meeting notes, reports, briefs)
- `.json` — Structured data (Slack channel exports, calendar events)
- `.jsonl` — Line-delimited JSON (daily calendar snapshots)
- `.csv` — Tabular data (bottleneck analyses, sprint timelines, schedules)

## Usage

These corpora can be used to:

1. **Reproduce paper results** — Ingest into OIDA (or any knowledge system) and run the EQS evaluation protocol described in Section 4.1
2. **Benchmark epistemic systems** — Test whether your system can distinguish decisions from hypotheses, surface contradictions, and model organizational ignorance
3. **Compare RAG approaches** — Use as input corpora for GraphRAG, LightRAG, or other retrieval-augmented generation systems

## Citation

```bibtex
@article{bottino2026retrieval,
  title={Retrieval Is Not Enough: Why Organizational AI Needs Epistemic Infrastructure},
  author={Bottino, Federico and Ferrero, Carlo and Dosio, Nicholas and Beneventano, Pierfrancesco},
  journal={arXiv preprint arXiv:XXXX.XXXXX},
  year={2026}
}
```

## License

This work is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). You are free to share and adapt the material with appropriate attribution.

## Acknowledgements

This work was developed within the research infrastructure of PoggioAI. We thank Alberto Trivero and Tommaso Portaluri for discussion on AI, statistical, and informatics matters.
