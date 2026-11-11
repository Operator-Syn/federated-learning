---
id: R01
title: "Aryani et al. 2026 — medicine stockouts in primary health care (scoping review)"
role: problem
status: skimmed
created: 2026-10-22
---

# R01 — Determinants, models, performances, and strategies of supply chain to address medicine stockouts in primary health care

**Citation.** Aryani F, Destiani DP, Satibi S, Harsanto B, Pradipta IS. Determinants, models,
performances, and strategies of supply chain to address medicine stockouts in primary health care:
a scoping review. *Journal of Pharmaceutical Policy and Practice* 19(1):2659077, 2026.
doi:10.1080/20523211.2026.2659077. Review article, CC BY-NC, open access.

**Artifact.** `../fulltext/R01-jppp-19-2659077.jats.xml` — complete JATS full text. PDF blocked by
an NCBI proof-of-work challenge; the XML is the better source anyway.

## Method

PRISMA-ScR scoping review, guided by the Antecedent–Decision–Outcome (ADO) framework and analysed
thematically through the Pharmaceutical Management Framework. PubMed, Scopus, EBSCO, January 2010
– January 2025. 307 records identified, **28 included**. Exclusions: industry supply chains,
wholesalers, vaccines, and reviews. Settings are primary health care, largely LMIC.

## Findings

**Antecedents** — four themes, 14 subthemes: (1) the medicine management cycle (selection,
planning, distribution, use); (2) management support, split into management information systems,
funding, human resources, organisation; (3) policy, law and regulation; (4) external system and
environmental factors (suppliers, climate, imports, donations, global disruption).

**Decisions (models)** — three families:

- Technology-driven: MLSM (machine-learning stochastic inventory model, India), RbRM (rule-based
  reasoning, inter-facility stock sharing), DSM (dynamic system modelling), FROST stock tracker,
  GIS.
- Information systems: LMIS, IPLS (Ethiopia, forced max–min inventory control on paper
  requisition/resupply forms).
- Governance and supervision: SPARS, MaTHSS, DRF, Jazia Prime Vendor System, SC4CCM.

**Outcomes** — all models showed positive effect; representative figures:

| Model | Reported outcome |
|---|---|
| LMIS (Tanzania, Ethiopia) | stockouts 45% → 22% |
| MAUL PSSP (Uganda) | stockouts 46% → 4%; inventory accuracy 79% → 91%; availability 54% → 71%; fill rate 93% → 97% |
| Jazia PVS (Tanzania) | tracer medicine availability 69% → 94% |
| SPARS (Uganda) | >70% median improvement in management capacity within one year |
| MLSM (India) | substantially improved demand estimation in rural and urban clinics |
| IPLS (Ethiopia) | improved tracking/logistics data use; no explicit availability outcome reported |

The review's own conclusion on mechanism: models work by **improving data use, strengthening
logistics management, and fixing distribution** — not by better mathematics.

## Relevance to this thesis

1. **Chapter 1 problem statement.** This is the best available citation for "medicine stockouts in
   primary care are a live, documented, LMIC-relevant failure mode" — and, critically, at *primary
   care* rather than hospital-pharmacy scale. That matches barangay health stations better than any
   hospital paper in the set.
2. **The comparator for RQ1.** IPLS and LMIS define current practice: a forced max–min control
   system driven by paper resupply forms and periodic reporting. When the proposal says the model
   must beat "current practice at real capacity", this is what current practice is, with numbers
   attached (45%→22% for a well-run LMIS).
3. **Design constraint, not just motivation.** The review's determinants are information and
   management failures. That is an argument that the intervention should be *cheap at the point of
   data entry* — which is exactly the U1 condition (collectable at a counter in three minutes) and
   the reason training must be invisible to the midwife.
4. **The gap it leaves.** MLSM applies machine learning but on a centralised drug-logistics
   information system; nothing in the 28 studies is federated or even explicitly
   privacy-preserving across facilities. Data movement is assumed, not problematised.

## Limits and how not to cite it

- Scoping review, not a trial. It aggregates heterogeneous designs; the percentages in the table
  are not a meta-analytic estimate and must not be presented as one.
- No federated learning, no prediction-accuracy evaluation, no Philippine setting (Indonesia-led
  authorship, mostly African and South Asian evidence).
- Its outcome measures are availability and stockout rate. This thesis predicts demand; the link
  from forecast quality to stockout rate is the thesis's job to argue, not this paper's.

## Citing sentence

> Stockouts in primary health care are driven mainly by weaknesses in the medicine management
> cycle, management information systems, and governance rather than by the absence of forecasting
> mathematics, and the interventions with the strongest reported effects — logistics management
> information systems and supervision strategies — all depend on accurate, timely data use at the
> facility level (Aryani et al., 2026).
