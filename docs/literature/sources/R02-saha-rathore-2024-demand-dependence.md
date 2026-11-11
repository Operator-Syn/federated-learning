---
id: R02
title: "Saha & Rathore 2024 — medication demand dependencies, multi-agent RL"
role: method + centralised comparator
status: skimmed
created: 2026-10-22
---

# R02 — A smart inventory management system with medication demand dependencies in a hospital supply chain

**Citation.** Saha E, Rathore P. A smart inventory management system with medication demand
dependencies in a hospital supply chain: a multi-agent reinforcement learning approach.
*Computers & Industrial Engineering* 191:110165, May 2024. doi:10.1016/j.cie.2024.110165.
Paywalled.

**Artifact.** `../snapshots/R02-cie-110165-fulltext-mirror.md` — introduction, literature review,
research gap, and conclusions retrieved through the doi.org landing page. Model formulation,
Table 1 (study comparison) and the case-study tables are behind the paywall and were **not** read.

## Problem and research questions

A hospital supply chain (HSC) runs from pharmaceutical suppliers to the hospital pharmacy (HP) and
then to points of care (POCs — ICU, HDU, wards). Medicines are stored at multiple locations with
limited capacity; patient arrivals are random; orders can be expedited at extra cost; unused
medicines return from POCs to HP.

The authors' stated novelty is **demand dependence**: some medicines must be administered together
(a main drug plus a supporting drug, at the same time), so a shortage of one blocks treatment and
piles up the other. Their questions:

- RQ1 — is knowledge of demand dependence among medicines useful for inventory management?
- RQ2 — what are the optimal control policies for HP *and* each POC under uncertain, dependent demand?
- RQ3 — do intelligent approaches beat traditional techniques?

## Method

Multi-agent reinforcement learning over a multi-item, multi-location, capacity-and-service-level
constrained inventory problem. Cost function includes ordering, holding, expediting, expiration and
return costs. Traditional `(s,S)` and can-order `(s,c,S)` policies are extended into a
`(s, c, S′, S)` policy that encodes dependence and joint replenishment. Validated on a case study:
a multispecialty hospital in eastern India, 12 months of medication orders from roughly 25,000
admitted patients, extracted from the hospital information system.

## Findings

| Comparison | Reported effect |
|---|---|
| `(s,c,S′,S)` vs `(s,S)` (ignores dependence and joint replenishment) | ≈ **35.71% lower cost** |
| `(s,c,S′,S)` vs `(s,c,S)` (joint replenishment, no dependence) | ≈ **3.89% lower cost** |
| Demand dependence level 50% → 90% | total cost falls as dependence rises, without loss of service level |
| Cost sensitivity | higher ordering/holding cost lowers reorder and can-order levels; higher expediting cost raises all four policy parameters |

Interpretation the authors draw: the *information* that two medicines are consumed together is
worth more than a more sophisticated policy that ignores it.

## Relevance to this thesis

1. **Structural template for the demand model.** HP → POC is the same shape as RHU/CHO → barangay
   health station: a central store, satellite locations with limited shelf space, emergency
   requisition at extra cost, returns of unused stock. The vocabulary transfers directly.
2. **A cheap, high-yield feature idea.** Their demand-dependence construct is reusable: ORS and
   paracetamol move together during a dengue surge, exactly the vignette in
   `docs/proposal/novelty-and-usecase.md`. A co-consumption feature costs nothing to compute from the stock
   card and is defensible against "why these features" in RQ1.
3. **The counterfactual arm.** This is the strongest available example of what a *centralised*
   data-pooling solution looks like and what it buys (35.71% over a naive policy). The federated
   arm has to be judged against that, not against a strawman.
4. **Evidence that RL beats classical policy in this setting** — which is why the candidate model
   list in `docs/proposal/topic-2-proposal.md` §3.2 is defensible, and why a decision-aware objective (R03) is
   more than a fashion.

## Limits and how not to cite it

- **Centralised by construction.** One hospital, one information system, 25,000 patients' records in
  one place. It therefore cannot speak to data separation — the condition this thesis is built on.
  Use it as the centralised baseline, never as evidence for federation.
- Hospital scale, not primary care. POC demand is driven by admitted inpatients, not by walk-in
  consults and monthly requisitions.
- Rich data assumption: "medication order information is explicitly extracted from the system" —
  a barangay BHS with a paper stock card cannot supply this. Their feature set is aspirational for
  the target setting, which is an argument for the U1 feature audit, not against the approach.
- Single institution, so no cross-facility heterogeneity, no client drift, no participation problem.

## Citing sentence

> When prescribed medicines are consumed in dependent combinations, encoding that dependence in the
> replenishment policy reduces total inventory cost by roughly a third relative to a policy that
> treats items independently, and reinforcement-learning agents can learn such multi-location
> policies directly from institutional ordering records (Saha & Rathore, 2024).
