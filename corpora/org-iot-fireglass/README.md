# org-iot-fireglass — Dataset Card

**Family:** organizational · **Domain:** IoT / Cloud platform / Product development

## Scenario

Innovative Windows LLC (40 employees, Verona, Italy) manufactures smart fire-resistant window systems with embedded IoT sensors. The team is building **FireGlass**, a cloud platform to monitor installations, manage field operations, and enable recurring software revenue as the company scales into European and North American markets. The project spans MQTT protocol integration, firmware coordination with hardware partner Helion Dynamics, field testing in Milan, and sprint-based development toward a launch.

The corpus covers the build across internal engineering channels, client-facing communications, sprint reviews, and formal deliverables.

## Why it is challenging

- **An evolving architecture decision.** A hybrid MQTT-backend + WebSocket-frontend design is chosen over direct browser-to-MQTT, with an engineer's pushback overruled on RBAC/audit grounds.
- **Internal-vs-client contradictions.** The timeline is framed internally as "lost ~2 sprints, 7 weeks left, tight" but to the client as a "potential 1–2 week slip, modules on track"; Milan field testing is reported bluntly internally (Unit C drops, no offline sensor logging) and softened to the client.
- **Unresolved external-dependency questions.** Helion's HelionLink v2.3 docs never arrive (only an auto-reply); the production MQTT broker choice waits on load testing; a topic-naming convention is left open.
- **Descoped-or-not ambiguity.** Sub-second real-time alerts that were promised at kickoff appear to be quietly descoped.

## Contents

| | |
|---|---|
| Documents | 47 (41 Markdown, 4 JSON, 2 CSV) |
| Queries | 20 (12 medium, 5 hard, 3 easy) |
| Qrels | 82 graded judgments (0–3) |
| Raw size | 672 KB |

## Example queries

- **q03** (medium) — internal vs client timeline → `03-internal-comms/email/budget-timeline-concern` (3), `04-external-comms/email/timeline-update-client` (3).
- **q12** (medium) — FG-001 duplicate-readings bug → `02-subject/known-issues` (3), `03-internal-comms/email/pre-launch-checklist` (2).

## Provenance & format

The 8-category source tree lives in `raw/`; `corpus.jsonl` is generated from it by `scripts/build_corpus.py`. See [`../../docs/format.md`](../../docs/format.md) and [`../../docs/relevance-guidelines.md`](../../docs/relevance-guidelines.md). This is a synthetic scenario; any resemblance to real companies is coincidental.
