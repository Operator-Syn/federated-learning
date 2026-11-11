---
id: R04
title: "Johnson & Ebakivie 2026 — Triple A review: analytics, AI, algorithms in healthcare inventory"
role: problem + stated gap
status: skimmed
created: 2026-10-22
---

# R04 — Triple A: How Analytics, AI, and Algorithms Are Improving Inventory Management in Healthcare

**Citation.** Johnson LL, Ebakivie O. Triple A: how analytics, AI, and algorithms are improving
inventory management in healthcare. *Logistics* 10(5):103, 1 May 2026.
doi:10.3390/logistics10050103. Systematic review, open access.

**Artifact.** `../pdf/logistics-10-00103-johnson-2026.pdf` (24 pp., 4.7 MB, sha256
`53d912a3e197b0d95fcbc93a19628637ed300176980d699c8cdb1fd2e6f438b3`) — the complete article, and the
authoritative text. `../snapshots/R04-logistics-10050103-article-page.md` is a grep-able copy of the
HTML page, truncated around 50k characters, so use the PDF for anything past the procurement
section.

## Method

Systematic review, 64 peer-reviewed articles, 2011–2025, descriptive plus content analysis.
Organising lens is the "Triple A" framework — **Algorithms** (EOQ through stochastic and robust
programming, rule-based, may not learn), **AI** (learns patterns: DRL, LSTM, MARL), **Analytics**
(descriptive, diagnostic, predictive, prescriptive). Applied across four inventory functions:
demand forecasting, tracking and control, classification, procurement. Contexts span hospitals,
pharmaceutical supply chains, and humanitarian supply chains.

## Findings worth carrying into Chapter 2

- **Integration beats single-method.** Combining Triple A approaches consistently outperforms
  single-method strategies, most visibly where RFID/IoT supplies the data that AI models consume.
- **Classification is the least studied function**, and it is absent from the emergency and
  humanitarian studies — which is strange, because those studies repeatedly name supply
  prioritisation as the operational bottleneck.
- **Emergency procurement is neglected** despite carrying the highest patient-safety stakes.
- **Implementation readiness, not technical capability, is the binding constraint.** The review's
  own summary: the field has hit diminishing returns on further technical development in tracking
  and control and is constrained by staff training, infrastructure cost, workflow disruption, and
  legacy-system compatibility.
- **Data quality decides whether the method works at all.** Point-of-use inventory control performs
  acceptably under moderate counting inaccuracy with adjusted base-stock levels, but degrades when
  data quality is poor (citing Neve & Schmidt).
- **Small establishments are structurally excluded.** AI adoption needs data, computation and money;
  fragmented datasets produce biased and unreliable models, and smaller health establishments cannot
  carry the cost.
- **Named constraints on generalisability:** data quality, interoperability, cybersecurity.
- **Named future work:** phased implementation, cloud-based platforms, **privacy-by-design**.

## Relevance to this thesis

1. **The gap statement, in a review's own words.** Privacy-by-design is *recommended* here and
   *studied* nowhere in the 64 articles. No federated architecture appears in the review. That
   sentence is the cleanest available justification for the thesis existing, and it is stronger
   coming from a 2026 systematic review than from the thesis asserting it.
2. **Why the contribution is about cost and equity rather than accuracy.** If implementation
   readiness is the constraint, then a study that reports wall-clock time-to-target, bytes
   transferred, and participation equity is answering the actual bottleneck. A study that reports
   another accuracy delta is not.
3. **Warrant for per-facility validation.** Their generalisability finding — models validated in one
   context and applied in another — is the argument for leave-one-facility-out testing in §3.2 of
   the proposal.
4. **Warrant for the U1 feature audit and the censored-demand worry.** Their data-quality finding is
   not a footnote in this literature; it is the mechanism by which these systems fail.
5. **Framing support for the ranking task.** Classification being the least-studied function, while
   being what a resource-constrained facility actually needs (which items, in what order), supports
   presenting the model output as a ranked shortlist under capacity rather than a probability.

## Limits and how not to cite it

- **It contains no federated learning.** Zero. It cannot support any claim about FL mechanisms,
  convergence, or privacy guarantees — only about the absence of such work in the reviewed corpus.
- Reviews inherit the weaknesses of what they review: mostly hospital and pharmaceutical-supply
  settings, thin on primary-care LMIC facilities, no meta-analysis.
- "Integration beats single-method" is a qualitative synthesis, not an effect size.
- The privacy-by-design recommendation is one clause in a conclusion; do not inflate it into the
  paper's central argument.

## Citing sentence

> A recent systematic review of 64 studies on analytics, AI, and algorithms in healthcare inventory
> management concludes that data quality, interoperability, and cybersecurity constrain
> generalisability, that implementation readiness rather than technical capability now limits
> adoption, and that privacy-by-design is a necessary direction — while reporting no federated
> architecture among the reviewed work (Johnson & Ebakivie, 2026).
