# Corpora Overview

Three synthetic organizational knowledge bases designed to evaluate epistemic infrastructure systems. Each corpus simulates a realistic organizational context with diverse document types, epistemic tensions, and knowledge lifecycle patterns.

All organizations, people, and events are fictional.

## Corpus Summary

| Corpus | Domain | Organization | Documents | Format Mix |
|---|---|---|---|---|
| caso-a | Consulting / Operations | ClearPath Solutions (Florence) | 46 | 40 md, 3 json, 3 csv |
| caso-b | IoT / Product Development | Innovative Windows / FireGlass (Verona) | 47 | 41 md, 4 json, 2 csv |
| caso-c | Venture Capital | Vertex Minds (Milan) | 77 | 52 md, 18 jsonl, 4 json, 3 csv |

## Document Category Schema

Every corpus follows the same 8-category directory structure:

```
caso-X/
├── 01-scope/            # Project definition, requirements, briefs
├── 02-subject/          # Domain-specific observations, analyses, technical docs
├── 03-internal-comms/   # Internal emails (email/) and Slack channels (slack/)
├── 04-external-comms/   # Client/external emails and Slack channels
├── 05-meetings/         # Meeting notes, workshops, reviews
├── 06-market-context/   # Industry reports, competitor analysis, market data
├── 07-documents/        # Formal deliverables, proposals, contracts
└── 08-agenda/           # Calendar events, schedules, timelines
```

This structure mirrors the natural information sources of an organizational knowledge base and ensures each corpus contains a mix of formal documents, informal communications, structured data, and temporal artifacts.
