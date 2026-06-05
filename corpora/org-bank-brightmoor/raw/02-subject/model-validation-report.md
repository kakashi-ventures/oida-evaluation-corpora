# Independent Model Validation — Sentinel Transaction-Monitoring Model

**Date:** February 10, 2026
**Document type:** Model validation report (Model Risk Management, independent of the AML business line)
**Validator:** Model Risk Management, reporting to the CRO
**Model:** Sentinel Analytics transaction-monitoring scenario model (candidate configuration)
**Status:** FINAL — authoritative validation finding

---

## 1. Purpose

Independent validation, under the Bank's model-risk framework, of the candidate Sentinel transaction-monitoring model the vendor proposes the Bank adopt as part of remediation. The vendor's marketing materials claim the model delivers a **40% reduction in false positives** versus the Bank's prior monitoring configuration. This validation tests that claim on Brightmoor's own data.

## 2. Method

We replayed twelve months of Brightmoor production transaction data through both the prior configuration and the candidate Sentinel model, holding the alerting population constant, and compared alert volumes and the false-positive rate (alerts dispositioned as non-suspicious on full investigation). We assessed statistical significance of the difference.

## 3. Finding

On Brightmoor data, the candidate model produced a false-positive reduction of approximately **15% — not the 40% the vendor advertises — and the observed reduction was not statistically robust** (the confidence interval was wide and crossed thresholds that would let us call the effect reliable). Restated plainly: **we could not validate the vendor's 40% claim on our data, and we cannot reliably distinguish the measured ~15% from no effect at all.**

The likely explanation is portfolio-specific: the vendor's 40% figure appears to derive from institutions with a different customer and transaction mix. Brightmoor's commercial-heavy portfolio behaves differently, and the tuning that produced 40% elsewhere does not transfer.

## 4. Conclusion & recommendation

- The vendor's 40%-false-positive-reduction claim is **not substantiated on Brightmoor data**.
- The measured ~15% improvement is **not statistically robust** and should not be relied upon as a basis for reducing analyst capacity or relaxing coverage.
- The model is acceptable for use **only** with Brightmoor-specific tuning and ongoing performance monitoring; it must not be deployed on the strength of the vendor's portfolio-general claim.
- Any business case that assumes a 40% false-positive reduction (e.g., for staffing) is unsupported and should be revised.

This finding is independent of the AML business line and stands as the Bank's validated position on the model's performance.
