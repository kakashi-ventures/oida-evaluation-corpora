# SEP-1 Bundle Compliance — Manual Chart Abstraction (Quality Dept)

**Date:** February 20, 2026
**Analyst:** Sandra Pell, Quality Data Analyst
**Method:** Manual abstraction per CMS SEP-1 specifications, random 30-chart sample (Q4 2025 adult sepsis cases)

---

## Headline

**SEP-1 3-hour bundle compliance: 62%** (18 of 29 abstractable charts; 1 excluded as non-sepsis on review).

This is the figure I am submitting as the official Quality Department baseline, computed strictly to CMS abstraction rules.

## Why this is lower than the dashboard number

Clinical Informatics' EHR dashboard reports **84%** for what looks like the same measure. The numbers are not comparable, and the difference is not an error in either system — it is a definition difference:

- **Manual abstraction (this report, 62%)** applies the full CMS SEP-1 "all-or-none" logic: a case fails if *any* element (lactate, blood cultures before antibiotics, broad-spectrum antibiotics within 3h, repeat lactate where indicated, timely fluids) is missed or late. It also applies CMS time-zero rules strictly.
- **EHR automated flag (dashboard, 84%)** counts a case as compliant when the *antibiotic order is placed* in the sepsis order set. It does not verify that every bundle element was completed on time, and it uses order-placement time rather than administration time.

So the dashboard measures "bundle *initiated*," and abstraction measures "bundle *completed to spec*." They will not converge without a definition change.

## Recommendation

The committee should pick ONE method of record before go-live. I recommend manual abstraction for any externally reported or board-reported figure, because that is what CMS will hold us to. The EHR flag is useful for real-time prompting but should not be reported as the compliance rate.

*(This divergence remained unresolved as of protocol approval in April.)*
