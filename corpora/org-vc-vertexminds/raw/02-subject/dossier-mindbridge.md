# VERTEX MINDS LLC — INVESTMENT DOSSIER

**Company:** MindBridge
**Sector:** HR Tech / Employee Engagement / Predictive Analytics
**Stage:** Pre-Seed
**Date:** November 20, 2025
**Analyst:** Tomás Herrera
**IC Members:** Daniel Reeves, Ava Lindström
**Classification:** CC BY 4.0 (Anonymized Research Corpus)

---

## EXECUTIVE SUMMARY

MindBridge is an early-stage SaaS platform that uses sentiment analysis on internal communications (Slack, email, employee surveys) to predict employee turnover risk 60 days in advance. The founding team believes their predictive model can help HR teams reduce involuntary turnover by up to 25% through proactive retention interventions.

**Investment Ask:** €150,000 (10% equity, pre-money €1.35M)
**Recommendation:** **CONDITIONAL PASS**

The team is talented and the problem space is real, but the company is pre-product-market-fit with zero revenue and unvalidated unit economics. We recommend revisiting in 90 days if specific milestones are achieved.

---

## TEAM ASSESSMENT

### Founders

**Anna Kowalski — CEO & Co-Founder**
Background: 6 years in HR technology (2 years as product manager at a larger HRIS platform, 3 years at a smaller HR analytics startup). MBA from London Business School. Strong understanding of HR workflows and buyer personas. Good communicator. This is her first CEO role.

**Raj Patel — CTO & Co-Founder**
Background: MS in Machine Learning from Stanford. 4 years in data science roles (most recently at a fintech company building risk scoring models). Published research on time-series classification (relevant to turnover prediction). Strong technical foundation.

### Organization

Team: 3 people (founders + 1 full-stack engineer hired 2 months ago). Remote-first. Bootstrap-funded to date (~€40K from founders). No external investors or advisors noted.

---

## PRODUCT & TECHNOLOGY

### Core Offering

MindBridge integrates with workplace communication platforms (Slack, Microsoft Teams, email) and employee survey tools to:

1. **Extract sentiment signals** from employee communications
2. **Build predictive turnover model** using historical data
3. **Identify at-risk employees** 60 days before resignation
4. **Alert HR managers** with recommended retention actions

### Technology Approach

The core model is a supervised classification model (logistic regression or gradient boosted trees—we didn't see the exact architecture) trained on historical employee communication data and actual departure events. The model extracts text features (word embeddings, sentiment scores) and temporal patterns (communication frequency changes, tone shift over time).

Data is sourced from (1) beta customer communication archives, (2) publicly available HR/turnover datasets (e.g., IBM HR dataset).

### Performance Claims

- **Model Accuracy:** 72% on historical test set (binary classification: will/won't leave in next 60 days)
- **Precision:** Not clearly stated
- **Recall:** Not clearly stated

**Note:** 72% accuracy on a historical dataset is not compelling evidence of real-world performance. Without precision/recall breakdowns, we cannot assess whether the model is actually useful for identifying at-risk employees. If recall is low (many departing employees not flagged), the model is not useful for retention purposes. If precision is low (many false positives), HR teams will ignore alerts.

### Privacy & Compliance

MindBridge reads internal communications (Slack, email, surveys). This raises significant GDPR, works council, and data privacy concerns:

1. **GDPR Compliance:** Processing employee communications requires explicit consent and lawful basis. In EU, works councils may need to be consulted. The company has not completed a GDPR audit.

2. **Employee Privacy:** Sentiment analysis on internal comms is perceived as surveillance by many employees. Implementation could trigger labor relations issues.

3. **Inference Liability:** Predicting turnover from sentiment could create legal exposure if the model makes protected category inferences (age, gender, etc.) or if predictions are used to discriminate against employees.

The company acknowledges these risks but has not yet built compliance into the product (data minimization, consent flows, audit logging).

---

## MARKET & TRACTION

### TAM Estimate

**Estimated TAM: €4.5B annually**

Derived from:
- ~8 million mid-to-large enterprises globally with 500+ employees
- Average HR tech spend: €500-1,500/year per employee (including payroll, benefits, analytics)
- Turnover/retention SaaS segment: ~€4.5B globally

EU-5 TAM: ~€1B (more regulated, smaller enterprise base, higher compliance costs)

### Current Traction

- **Active Pilots:** 3 companies (all unpaid, in-product testing)
- **Revenue:** €0
- **Estimated MRR:** €0
- **Pilot Details:**
  - Company A (200-person tech firm): Pilot running 6 weeks, feedback is positive but they haven't committed to purchase
  - Company B (500-person manufacturing firm): Pilot running 4 weeks, engagement is moderate, concerns about employee privacy
  - Company C (100-person consulting firm): Pilot running 2 weeks, very early

### Unit Economics (Estimated/Unvalidated)

- **Proposed Pricing:** €2,500-5,000/month per customer (based on employee headcount tiers)
- **CAC:** Unknown; pilots acquired through founder networks (not yet paid customer acquisition)
- **LTV:** Unknown; no paying customers to evaluate retention
- **Expected CAC (if sales hires):** €8,000-12,000 (typical for HR SaaS enterprise sales)
- **Implied LTV/CAC:** ~3-5x (if pricing holds and average customer lifetime is 3 years)—acceptable but unproven

---

## COMPETITIVE LANDSCAPE

### Existing Solutions

1. **Workday, SAP SuccessFactors, Mercer Rhumbline:** Large HR systems with embedded analytics modules. Turnover prediction is 1 of 100 features. Integration is deep but prediction quality is mediocre (these systems lack real-time communication signals).

2. **Culture Amp, Peakon, Humu:** Employee engagement platforms with survey-based feedback. Some predictive analytics but not focused specifically on turnover. More mature, well-funded, better brand awareness.

3. **LinkedIn Recruiter/Talent Insights:** LinkedIn's talent insights include attrition benchmarking but not individual prediction. No direct competitor here yet.

4. **Internal HR builds:** Some large enterprises (Google, Meta) build proprietary turnover prediction models. Not a commercial threat.

### Competitive Position

MindBridge's differentiation: real-time communication signals (Slack, email) vs. periodic surveys. This is a real advantage IF the model actually works and IF customers trust it. However, the communication-based approach also creates privacy concerns that larger vendors can avoid.

---

## FINANCIAL REVIEW

### Historical Burn

- **Bootstrapped Capital:** ~€40K from founders
- **Monthly Burn:** ~€4,500 (minimal salary for founders, basic cloud infrastructure)
- **Runway (current):** ~9 months

### Use of Funds (€150K)

- €60K: Product development (GDPR compliance, data minimization, consent flows, integrations)
- €50K: GTM (1 sales hire, marketing, customer success)
- €40K: Infrastructure & data (model retraining, validation, customer data storage)

### Burn Projection (Post-Round)

If the company hires 1 sales person and maintains engineering focus:
- **New Monthly Burn:** €8,000-10,000
- **Runway (post-€150K):** ~15-18 months
- **Revenue Breakeven:** Unlikely to achieve in this period (requires 2-3 paying customers at €3,000+/month MRR)

---

## RISK ASSESSMENT

### Critical Risks

1. **Zero Revenue / Pre-PMF:** The company has no paying customers and is entirely dependent on finding product-market fit. The product is unvalidated at any meaningful scale.

2. **Model Validation Gap:** The 72% historical accuracy claim is not impressive and lacks precision/recall metrics. Real-world performance could be significantly worse, especially if:
   - Historical data is different from current communication patterns
   - The model overfits to the training dataset
   - Real-world churn is driven by factors not reflected in sentiment (e.g., market downturn, team restructuring)

3. **Privacy & Compliance Minefield:** GDPR, works councils, employee consent, data minimization—these regulatory burdens are significant in EU. The company has not yet built compliance into the product. A customer GDPR violation could create liability for MindBridge.

4. **Unproven Customer Willingness to Pay:** Pilots are free. Even if sentiment analysis works, customers may not want to buy a tool that monitors employee communications (perception of surveillance). HR teams may lack budget or business case.

5. **Chicken-and-Egg Problem:** To improve the model, the company needs customer data. To win customers, the company needs a better model. Bootstrapping this cycle is difficult.

### Medium Risks

1. **Competitive Threat:** Larger vendors (Culture Amp, Peakon) could add turnover prediction modules at lower price points.

2. **Regulatory Headwinds:** Future EU regulations on AI and workplace monitoring could restrict the use of sentiment analysis on employee communications.

3. **Sales Cycle:** HR SaaS enterprise sales have long cycles (6-12 months) and high CAC. Even if the product is good, revenue ramp will be slow.

---

## CONDITIONAL RECOMMENDATION

**Status: CONDITIONAL PASS**

We recommend **revisiting this investment in 90 days** if and only if the following conditions are met by February 15, 2026:

### Condition 1: At Least 1 Paying Customer
- A beta pilot must convert to a paid contract
- Minimum contract value: €2,500/month (12-month term preferred)
- This validates customer willingness to pay and addresses the zero-revenue risk

### Condition 2: Improved Model Validation
- Model accuracy must exceed 80% on live production data (not historical test set)
- Precision and recall metrics must be provided
- This addresses the unvalidated claims risk and demonstrates real-world performance

### Condition 3: GDPR Compliance Audit Completed
- A third-party audit (or reputable legal firm) must confirm GDPR readiness
- Consent flows, data minimization, and privacy controls must be documented and implemented
- This addresses regulatory risk and reduces liability exposure

---

## INVESTMENT THESIS (IF CONDITIONS ARE MET)

If the above conditions are satisfied, MindBridge becomes a more compelling investment:

- **Market:** Large and growing (retention is increasingly a C-suite priority)
- **Team:** Talented and focused
- **Differentiation:** Real-time communication signals are unique approach (if model works)
- **Unit Economics:** Appear reasonable (3-5x LTV/CAC at scale)

At that point, a €150K investment would be appropriate to fund continued product development, initial sales, and geographic expansion.

---

## CURRENT INVESTMENT DECISION

Given that **conditions are not currently met**, we recommend **deferring this investment** and revisiting in 90 days.

If the team wants to proceed with funding before these milestones are achieved, it should be from impact investors or mission-driven funds aligned with "future of work" thesis, not from Vertex Minds at this stage.

---

**Prepared by:** Tomás Herrera
**Date:** November 20, 2025
**Status:** CONDITIONAL — Revisit in 90 Days
**Follow-Up Required:** Confirm milestone achievement before next IC meeting
