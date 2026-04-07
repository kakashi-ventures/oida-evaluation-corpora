# Corpus Document Schema

Each corpus follows an 8-category directory structure representing typical organizational knowledge sources.

## Categories

### 01-scope
Project-level framing documents: briefs, requirements, statements of work. These typically contain DECISION and CONSTRAINT class knowledge.

### 02-subject
Domain-specific content: process maps, technical documentation, observations, analyses. Rich in OBSERVATION, EVIDENCE, and HYPOTHESIS classes.

### 03-internal-comms
Internal communications organized by channel:
- `email/` — Internal email threads (Markdown)
- `slack/` — Slack channel exports (JSON/JSONL)

Contains a mix of all epistemic classes, often including informal HYPOTHESIS and QUESTION objects.

### 04-external-comms
Client-facing and external communications:
- `email/` — External email threads (Markdown)
- `slack/` — Client Slack channel exports (JSON)

Typically contains NARRATIVE, PLAN, and DECISION classes with higher formality.

### 05-meetings
Meeting notes, workshop outputs, review sessions. These are key sources of DECISION, QUESTION, and EVALUATION objects, as organizational decisions are often made and recorded in meetings.

### 06-market-context
Industry reports, competitive analyses, market data. Primarily EVIDENCE and OBSERVATION classes with external provenance.

### 07-documents
Formal deliverables: proposals, contracts, reports, presentations. Typically DECISION, PLAN, and EVALUATION classes.

### 08-agenda
Temporal artifacts: calendar events, sprint timelines, schedules. Structured data (JSON, JSONL, CSV) providing the temporal backbone of the organizational context.

## File Format Conventions

| Format | Extension | Usage |
|---|---|---|
| Markdown | `.md` | Emails, meeting notes, reports, briefs — all narrative documents |
| JSON | `.json` | Slack channel exports, calendar events |
| JSONL | `.jsonl` | Daily calendar snapshots (one event per line) |
| CSV | `.csv` | Tabular data: bottleneck analyses, timelines, schedules |

## Markdown Document Structure

Narrative documents (emails, meeting notes) follow consistent conventions:

- **Title** as H1 heading
- **Metadata block** with date, participants, and document type
- **Body** with organizational content
- Natural language with realistic organizational detail
