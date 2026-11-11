---
title: "RRL relevance matrix"
type: literature-analysis
status: draft
created: 2026-10-22
sources: [R01, R02, R03, R04, R05]
---

# What these five sources are for

The set is deliberately uneven, and that is its value: only one of the five uses federated
learning. The other four do the work that an FL paper cannot do — they establish that the
problem is real, define the current practice the model must beat, and supply the forecasting
and inventory method the federated model will actually be trained on.

Read as a chain: **R01 and R04 establish the problem → R02 and R03 define the method class
and the comparator → R05 shows the FL variant exists and reports what it bought.** None of
them measures what this thesis measures.

## Role in Chapter 2

| ID | Role | Supports | Cannot support |
|----|------|----------|----------------|
| R01 | Problem, at primary-care scale | That medicine stockouts are a live primary-care failure mode with documented determinants; that the interventions which work are data-use and governance interventions; that the evidence base is LMIC primary care, not hospital pharmacy | Any claim about FL, about prediction accuracy, or about effect sizes transferable to Iligan |
| R04 | Problem + stated gap | That a 64-study review of analytics/AI/algorithms in healthcare inventory recommends *privacy-by-design* without studying it; that implementation readiness, data quality and interoperability — not model sophistication — are the binding constraints | Any FL mechanism claim; it contains no federated system |
| R02 | Method: demand model + centralized comparator | That RL-based inventory control beats classical `(s,S)`-type policies when items are dependent; that multi-location, capacity-constrained replenishment is the right formalisation for health-facility stock | Anything about training across institutions; its data is one hospital's 25,000-patient record set, pooled |
| R03 | Method: decision-aware forecasting | That forecasting should be trained against the inventory cost of being wrong, not against prediction error; that context-aware multi-source input beats single-source; that two-stage forecast-then-optimise is the dominant, weaker paradigm | That its covariates are collectable at a barangay counter; anything multi-institution |
| R05 | FL precedent, direct prior art | That FL + deep RL for ordering in a healthcare supply chain is feasible and survives demand shocks better than baselines | That its 18%/22%/15% gains are auditable — abstract only, no per-client reporting, no datasets named, conference-length paper |

## Mapping to the four research questions

| RQ (from `docs/proposal/topic-2-proposal.md`) | What these sources give it | What they leave open |
|---|---|---|
| RQ1 — which model is usable from BHS-collectable inputs, vs current practice | R03 justifies selecting on decision outcome rather than AUROC; R04's data-quality findings justify the feature audit (U1); R01 documents current practice — LMIS/min-max requisition — as the comparator | None of them evaluates a model at fixed diagnostic capacity; precision@k is ours to define |
| RQ2 — how selection strategy changes time to target, and how that shifts as connectivity degrades | R05 shows FL converges to a better policy than local-only; R04's "implementation readiness" argument is why wall-clock time belongs in the results at all | No source models intermittency, stragglers, or timeout rules. Zero coverage |
| RQ3 — how intermittent availability affects convergence and per-client performance | R05 names non-IID demand and communication bottlenecks and answers them with FedProx + DP, i.e. an *aggregation-side* fix | It does not report per-client degradation, so the "who gets worse" question is untouched |
| RQ4 — which policy reaches target fastest without starving a facility | R05's pooled 18%/22%/15% is exactly the reporting style that hides the distribution — cite it as the thing this thesis decomposes | No source measures participation equity, starvation, or minimum-client performance |

## The gap, stated in one paragraph

Four of these five studies assume the data can be assembled in one place: R02 pools a
hospital's records, R03 pools four Beijing data streams, R01's strongest interventions (LMIS,
MLSM) are centralised information systems, and R04 reviews 64 studies in which no federated
architecture appears at all — while explicitly recommending privacy-by-design as future work.
R05 closes that gap in principle and reports aggregate gains, but its unit of analysis is the
supply chain, not the facility. So the literature can say *federation is worth it on average*
and cannot say *which facility paid for the average*. That is precisely the question this
thesis asks, and it is asked with a metric none of the five report: per-client gain, per-client
participation, and the wall-clock price of including the weakest node.

## Three claims the set will not let you make

1. **Do not claim FL is unstudied in this domain.** R05 exists. The honest claim is that
   FL inventory studies report pooled outcomes and ignore participation.
2. **Do not claim accuracy improvements as the motivation.** R03 shows prediction accuracy is
   the wrong objective; R04 shows technical capability is not the binding constraint.
   Motivation must be rare-event coverage at low-volume facilities — the thesis's own novelty
   statement — not "FL makes the model better".
3. **Do not cite R01 or R04 as evidence about federated methods.** They are reviews of
   non-federated practice. Use them for the problem, the comparator, and the stated gap only.

## What this set is missing

The five sources cover the demand-forecasting vehicle and the problem statement. They do not
cover the contribution (C2), which is client selection under intermittency. Chapter 2 will be
lopsided without 4–6 more sources on:

- fairness-aware / inclusion-aware client selection (FedFS, q-FFL, FedSampling, LongFed)
- participation equity and starvation as measured quantities
- straggler-tolerant aggregation and asynchronous FL (FedProx, timeout/semicycle rules)
- client selection under system heterogeneity (Oort-style utility selection)
- FL deployment in low-resource health systems, as distinct from simulation

The proposal's reference list already names FedFS, LongFed and FedSampling; those three
should be promoted into this subsystem with notes before Chapter 2 is drafted.
