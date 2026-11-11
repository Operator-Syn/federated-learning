---
id: R05
title: "Singh & Aggarwal 2025 — FedDQN-SC: federated learning + DQN for healthcare supply chains"
role: FL precedent / direct prior art
status: abstract-only
created: 2026-10-22
---

# R05 — Integrating Federated Learning and Deep Q-Networks for Resilient Healthcare Supply Chain Optimization amidst Uncertain Demand

**Citation.** Singh G, Aggarwal N. Integrating federated learning and deep Q-networks for resilient
healthcare supply chain optimization amidst uncertain demand. *2025 2nd International Conference on
Artificial Intelligence for Innovations in Healthcare Industries (ICAIIHI)*, Raipur, India,
4–5 December 2025. doi:10.1109/ICAIIHI67124.2025.11403491. IEEE, paywalled.

**Artifact.** `../snapshots/R05-ieee-11403491-abstract.md` — abstract and the first paragraph of §I.
No further text was accessible: the PDF requires purchase and the reference list is not published
on the landing page.

## What it does

**FedDQN-SC**: federated learning wrapped around Deep Q-Networks for distributed inventory
optimisation. Local DQN agents learn ordering policies on institutional data in place; only model
updates are transmitted, never raw records. Two additions address known FL failure modes:

- **FedProx** regularisation — a proximal term in the local objective that limits client drift when
  demand distributions are non-IID across institutions.
- **Differential privacy** — noise on the shared updates, and a stated concern for the communication
  bottleneck.

Motivating problem, in the authors' framing: uncertain demand, strict privacy restrictions, and
fragmented data across institutions; EOQ and base-stock models assume homogeneous, certain
environments and do not transfer to heterogeneous ones.

## Reported results (abstract only — not auditable)

| Metric | FedDQN-SC vs centralised and local baselines |
|---|---|
| Service level | up to **+18%** |
| Inventory held | up to **−22%** |
| Operating cost | up to **−15%** |
| Demand-shock scenario | service level held **above 80%** while the baseline fell **below 65%** |

## Relevance to this thesis

1. **Direct prior art — cite it, then differentiate.** This is the closest published work to the
   thesis: FL plus RL for ordering decisions in healthcare supply chains under uncertainty. Reviewers
   who know the area will look for it. Being cited first is a strength; being scooped in the
   literature review is not.
2. **It validates the vehicle.** The demand-shock result (service level held above 80% vs a baseline
   below 65%) is a reason to believe the rare-event argument in `docs/proposal/novelty-and-usecase.md` is
   plausible: a federated model that has seen other institutions' shocks does not collapse on its
   own. The thesis's H2 and H3 sharpen that into a per-facility, measurable claim.
3. **It leaves exactly the space the thesis occupies.** Three gaps are visible even from the
   abstract:
   - **Pooled reporting.** 18/22/15% are supply-chain-level averages against "baselines". Nothing is
     said about the distribution across institutions — who gained, who gained nothing, who was
     selected every round and who was never selected. That is the thesis's RQ4 and H4.
   - **Aggregation-side remedies only.** FedProx and DP fix *how updates are combined and protected*.
     They do not touch *which clients train*. Client selection is a different lever, and it is
     unexamined here — which makes the thesis complementary rather than competitive, and that is the
     sentence to write in §2.3.
   - **No intermittency model.** "Communication bottlenecks" is named as a motivation, not
     operationalised into availability probabilities, latency, stragglers, or a timeout rule. The
     thesis's three connectivity regimes are the missing instrument.
4. **Naming discipline.** Cite the 18/22/15% as *what the authors report*, in the section on prior
   FL work, with the venue named so the reader can weigh a two-author conference paper accordingly.
   Do not put it in a comparison table beside this thesis's own numbers.

## Limits and how not to cite it

- **Evidence quality is low.** Conference paper, short page budget, two authors, datasets described
  only as "pharmaceutical supply chain datasets", no per-client breakdown, no code, no data, no
  reproducibility artifacts. 43 full-text views and 1 citation at retrieval.
- **Abstract-level knowledge only.** Nothing here about local epochs, client counts, aggregation
  frequency, DP budget (ε), or how the FedProx term was tuned. Any claim about *how* it performs
  under heterogeneity is speculation.
- **Setting mismatch.** "Healthcare supply chain" here means institutional inventory, not primary-care
  barangay facilities on intermittent links. Its connectivity assumptions are unstated.

## Citing sentence

> Federated reinforcement learning has been applied to healthcare supply chain ordering, with local
> deep Q-network agents training in place and only model updates shared, reporting higher service
> levels and lower inventory and operating cost than centralised and local baselines and holding
> service level above 80% under demand shocks where baselines fall below 65% (Singh & Aggarwal,
> 2025); these results are aggregated at supply-chain level, and neither client selection nor
> intermittent participation is examined.
