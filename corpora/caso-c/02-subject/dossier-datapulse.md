# DataPulse Dossier

**Date:** November 14, 2025
**Analyst:** Tomás Herrera
**For:** Daniel Reeves, Ava Lindström
**Status:** PASS

---

## Executive Summary

DataPulse is a real-time behavioral analytics platform targeting e-commerce fashion brands. The company leverages lightweight SDK instrumentation to capture micro-interactions (scroll depth, hover duration, zoom patterns, product comparison sequences) and delivers merchandising insights within seconds. The founders claim this capability drives an 18% uplift in conversion rates through dynamic product layout optimization.

We recommend **PASS** on this investment. While the product demonstrates technical competency and addresses a legitimate pain point in fashion retail, the combination of aggressive valuation, inconsistent traction metrics, and elevated churn presents unacceptable risk at this stage.

---

## Company Overview

**Founders:**
- **Simone Marchetti** (CEO) — Former merchandising director at Gideon, an Italian mid-market fashion group. 8 years in retail optimization. No prior startup experience.
- **Elena Varga** (CTO) — Previously engineering lead at Wove, a now-defunct real-time personalization startup. 5 years building analytics infrastructure. MSc Computer Science, University of Milan.

**Product & Technology:**

DataPulse provides a JavaScript SDK (< 3 KB minified) that customers embed in product pages. The SDK captures:
- Scroll velocity and depth
- Hover time on product attributes
- Zoom interactions (if applicable)
- Product comparison sequences
- Time-to-add-to-cart

Events stream to DataPulse's cloud backend (AWS, region eu-west-1). The platform aggregates these signals into a real-time dashboard displaying:
- Heat maps of product performance
- Behavioral micro-segments
- Recommended product rearrangements
- A/B test integration API

The founders claim the core algorithm uses unsupervised learning to detect anomalous purchasing intent patterns, though we could not review the underlying model or request historical performance validation.

**Market Position:**

DataPulse targets e-commerce fashion retailers with >€2M annual GMV. The primary competitor set includes Contentsquare (expensive, broad), Optimizely (legacy, slow), and scrappy custom solutions built in-house at larger retailers. Secondary competitors: Hotjar (heatmaps only) and smaller data enrichment vendors.

---

## Traction & Metrics

### Key Claims vs. Verified Reality

**Monthly Active Users (MAU):**
- **Pitch materials state:** 50,000 MAU
- **Our independent verification:** 38,200 MAU as of October 2025 (via dashboard access granted during due diligence)
- **Founder explanation:** "Seasonal fluctuation and some test accounts." When pressed for a monthly breakdown, Simone could not provide a coherent narrative. This is a material discrepancy and raises questions about either (a) careless metrics reporting or (b) deliberate misrepresentation.

**Paying Customers:**
- 4 customers under contract
- Named clients: 2 mid-market fashion groups (€30M+ GMV each), 1 e-commerce marketplace, 1 boutique chain

**Monthly Recurring Revenue (MRR):**
- €8,000 at end of October 2025
- Contract values: €1.2K–€3K/month; primarily consumption-based with €500 minimum floors

**Customer Retention:**
- 6% monthly churn observed over last 4 months
- Annualized churn: ~72%
- One customer departed in September citing "lack of ROI differentiation from in-house tools"

**Revenue Growth:**
- 40% YoY (but baseline is small; Q4 2024 MRR was ~€5.7K)
- Trajectory is positive but not exceptional

---

## Financial Snapshot

- **Runway:** ~18 months at current burn (~€25K/month)
- **Burn composition:** 3 engineers, 1 product manager, 1 sales/ops, CEO. Cloud costs ~€2.2K/month; rest is payroll
- **Ask:** €350K for 5% equity at €6.65M pre-money valuation (Seed round)
- **Post-money:** €7M

---

## Assessment by Dimension

### Market

The behavioral analytics market is fragmented and growing. However, DataPulse's TAM within fashion e-commerce is narrow. European fashion e-commerce represents ~€150B in online GMV; perhaps 5–10% of that is held by retailers sophisticated enough to adopt real-time behavioral tools (~€7.5–15B serviceable market).

The company has not articulated a credible path to horizontal expansion (e.g., travel, luxury goods, FMCG). This constrains the long-term narrative.

**Rating: 3.5/5**

### Product

The SDK is well-engineered, lightweight, and non-intrusive. The dashboard UX is clean. The architecture (event streaming, real-time aggregation) is sound for the problem.

However, we have low confidence in the claimed 18% conversion lift. This number comes from two customer case studies, neither independently verified. Simone acknowledged that one customer had "some other merchandising changes in parallel," muddying the attribution. The other customer provided a testimonial but no raw data.

The product lacks defensibility. A competent engineering team could replicate the core insight in 6–12 months. Barriers to entry are primarily distribution and customer relationships, not IP.

**Rating: 4.0/5**

### Team

Simone is credible on retail domain knowledge but has never scaled a SaaS company. Elena is solid on infrastructure but was at Wove, which shuttered in 2021 — a signal of either poor market timing or operational challenges.

The advisory board includes one fashion retail executive and one data science consultant. No venture or GTM expertise visible.

We have medium confidence in execution risk.

**Rating: 3.0/5**

### Traction

4 customers generating €8K MRR is early-stage but real. The 6% monthly churn is a significant red flag. In cohort analysis, we'd expect to see either (a) stable churners (a few customers leaving) or (b) retention curves that plateau after month 4–6. Instead, DataPulse is losing customers in month 7–8 of relationship, suggesting product-market fit challenges or escalating price resistance.

The MAU discrepancy between pitch and reality erodes confidence in all self-reported metrics.

**Rating: 3.0/5**

### Strategic Fit

DataPulse is not a natural fit for Vertex Minds. We focus on AI-native businesses with defensible algorithms or data moats. DataPulse's core value is behavioral instrumentation, not AI per se. The founders have not positioned the company as leveraging large language models, computer vision, or other forms of AI differentiation.

That said, the product addresses a real problem for our fashion/retail market contacts.

**Rating: 2.0/5**

---

## Red Flags & Concerns

1. **Metrics Inconsistency:** The 50K → 38K MAU discrepancy is material. Even if attributable to seasonal factors, the inability to articulate the variance suggests either (a) poor analytics discipline or (b) intentional misrepresentation.

2. **High Churn:** 6% monthly churn on a 4-customer base means one customer every ~4 months. This is unsustainable and suggests customers are not realizing promised ROI or hitting pricing resistance.

3. **Attribution Risk:** The +18% conversion claim rests on shallow evidence. Without rigorous A/B testing or cohort analysis, we cannot validate the claimed value prop.

4. **Valuation:** €6.65M pre-money for €8K MRR is a 100x multiple on current revenue. Even at 3x growth, this would imply a ~33x multiple in 12 months. This is high for an unproven product in a fragmented market.

5. **No Obvious Exit Path:** Consolidation opportunities exist (Contentsquare, Optimizely), but DataPulse is not yet large enough to be a credible M&A target.

---

## Questions for Founders

If we were to reconsider, we would require:

1. Detailed monthly cohort retention curves for all 4 customers (names redacted if needed).
2. Granular monthly breakdown of MAU from January 2024 to October 2025, with explanations for any anomalies.
3. Raw attribution data from the two case study customers, including A/B test design or statistical methodology used to isolate the 18% lift.
4. A revised financial model showing path to €50K+ MRR with realistic CAC/LTV assumptions.

---

## Recommendation

**PASS**

DataPulse is a competent team building a technically sound product in a real market. However, the valuation is aggressive relative to traction, the churn profile is concerning, and the metric discrepancies undermine trust. The company would be a stronger fit at a €4–4.5M pre-money valuation with evidence of improved retention and customer concentration.

We recommend a courtesy follow-up in 12 months to assess progress.

---

**Prepared by:** Tomás Herrera
**Date:** November 14, 2025
**Next Review:** Q4 2026 (if founders reach out)