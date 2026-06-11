# office-threads — Dataset Card

**Family:** communication · **Domain:** Office communications / multi-channel reasoning · **Language:** Italian

## Scenario

One working week (4–10 June 2026) of multi-channel workplace communications — emails, WhatsApp messages, Slack DMs and channel posts, calendar invites, and document attachments — centred on Marco Ferri at Nova Venture Accelerator (NVA), a fictional Italian company. The 29 sources interleave four mundane threads: a client meeting with its travel logistics, an Edenred meal-voucher order, a contracts submission, and the monthly timesheet collection.

Unlike the `org-*` knowledge bases, there is no authoritative document layer: ground truth is scattered across channels, and much of it lives in the *headers* rather than the message bodies — send vs read timestamps, CC lists, attachment links, reliability priors. Several claims made in the messages are simply false, and the record that refutes them sits in a different channel.

## Why it is challenging

- **Information gaps.** The replacement (Italo) tickets for the Wednesday trip carry only a booking code — the corpus never states the departure time. The superseded Trenitalia tickets *do* state one (14:10), but for the wrong day: a perfect topical match that is the wrong answer (q01).
- **Multi-hop inference.** Sara has no meal vouchers because part-timers were excluded from the order (one email) *and* her timesheet shows a 3-day week (an attachment two threads away) — no single document states the cause (q02). Marco's confident "you all have them" reply is a judged-0 false explanation.
- **Claims vs records.** Marco claims the regolamenti invite was already sent on 5 June; the invite's own timestamp says 8 June (q03). His contracts email asserts "Laura is in copy" while its header reads `CC: (nessuno)` (q07).
- **Information asymmetry.** Davide's "venite qua" (come here in person) reaches Marco alone, on WhatsApp; Stefano, who only saw the calendar invite, believes the meeting is remote and says so (q05).
- **Holiday inference.** Whether NVA is closed on 1 May is never stated; it must be inferred from the timesheet instructions — against a timesheet that erroneously marks the holiday as worked (q09).

## Contents

| | |
|---|---|
| Documents | 29 (all Markdown, Italian) |
| Queries | 9 (5 hard, 3 medium, 1 easy) |
| Qrels | 40 graded judgments (0–3) |
| Raw size | 116 KB |

Each source carries a canonical header:

```
SOURCE_ID:
SOURCE_TYPE:
AUTHOR:
RECIPIENT:
TIMESTAMP:
READ_TIMESTAMP:
CHANNEL:
SUBJECT:
RELIABILITY_PRIOR:
TEXT:
```

The nine queries each target a distinct situation: information-gap detection, multi-hop inference, contradiction detection (×2), information asymmetry, temporal inference (×2), claim verification, and plausible inference.

## Qrels rationale

Judgments follow the graded rubric in [`../../docs/format.md`](../../docs/format.md) (3 = directly answers / binding record, 2 = strong support, 1 = weak/contextual, 0 = explicitly judged non-relevant trap), with epistemic primacy over topicality. Conventions used:

- For contradiction-detection queries (q03, q04) both sides of the contradiction are graded 3, mirroring the derivation used in `inv-mystery-redhood`.
- Explicit 0s mark on-topic traps: the wrong-day Trenitalia tickets for the departure-time query (q01) and Marco's false "you all have them" explanation for the voucher query (q02).

## Example query

- **q05** (hard) — *"Dove si svolge la riunione con Rossi?"* → top judged docs `source_002_whatsapp_davide_to_marco` (3, the private "venite qua"), `source_009_whatsapp_stefano_remote` (3, the asymmetric remote belief), `source_004_slack_marco_to_laura_tickets` (2), `source_001_calendar_invite_rossi_meeting` (2).

## Provenance & format

The 29 sources live in `raw/` as `source_*.md`; `corpus.jsonl` is derived from `raw/`. See [`../../docs/format.md`](../../docs/format.md). This is a fictional scenario; all persons and companies are invented.
