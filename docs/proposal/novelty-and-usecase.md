---
title: "Novelty statement and use-case vignette"
type: thesis-positioning
course: CSC198
group: Beira, Jagonia, Ybanez
status: fixed
created: 2026-10-20
updated: 2026-10-20
source: "brainstorm 2026-10-20; supplies Chapter 1 motivation for the Topic 2 study"
---

# The novelty, in one sentence

> **Federated learning lets a facility benefit from events it has never experienced itself.**

That is the claim the thesis is built on, and it is the sentence that should appear in
the abstract, the introduction, and the defense slides.

## Why this framing is the contribution

Most federated-learning-in-health papers compare mechanisms on benchmark data and report
that accuracy went up. That answers "does FL work" and nobody is surprised by the answer.

This thesis reframes FL's value as **coverage of rare events**, and then makes that
coverage measurable per facility. A barangay that has never recorded a dengue surge, a
faltering growth trajectory, or a stock-out cannot learn what one looks like. It has no
examples. Federation gives it the shape of an event it has not yet lived through.

The measurable form of the claim:

> A facility's gain from joining a federation should be **inversely related to its own
> record count** and **directly related to the rarity of the event being predicted.**

If that relationship shows up in the results, it is a real finding with an operational
consequence: federation pays for its coordination cost below some record threshold, and
stops paying above it. A health office can then decide which facilities to onboard first
instead of onboarding everyone for principle.

## Testable claims

These turn the vignette into a thesis. Each has a home in the results chapter.

| ID | Claim | How it is tested |
|----|-------|------------------|
| H1 | Per-facility gain from federation decreases as local record count increases | Plot gain vs local N per facility; fit a monotone curve |
| H2 | For rare events, federated models beat local-only models substantially in low-volume facilities | Local-only vs federated, per facility, rare-event metric (recall / precision@k / stock-out days avoided) |
| H3 | A cold-start facility is usable immediately under federation and unusable under local-only training | Hold one facility out entirely; compare its day-one performance under both setups |
| H4 | Inclusion-hostile client selection concentrates gain in frequently selected facilities, and starved facilities lose rare-event coverage | Rerun H1-H2 per selection strategy; interaction between participation count and gain |

**Falsification.** If gain is uniform across facility sizes, the novelty claim fails and
the study reverts to a plain selection comparison. Say this in the proposal. A hypothesis
nobody can falsify is not a hypothesis.

## The vignette (Chapter 1 motivation)

**Persona.** Ma'am Lorna, midwife, officer-in-charge of a coastal barangay health station
in Iligan. One barangay health worker assists her. She orders commodities monthly through
the Rural Health Unit on a paper requisition form. She has run out of oral rehydration
salts every rainy season for three years, so she now over-orders in June, and the excess
expires in December.

**Monday.** She dispenses ORS, amoxicillin, iron, and paracetamol, writing date, quantity,
and balance in the stock card. This is existing DOH-mandated work. Nothing extra is asked
of her.

**Friday, 6 p.m.** A scheduled job on the facility machine loads the last two years of
local dispensing records, fine-tunes a local copy of the model for a few epochs, and sends
**only the weights** to the city aggregator. The records never leave the building. The
message is smaller than a photograph, small enough for a mobile hotspot.

**Monday after.** She sees one line, not a chart: *ORS — 340 sachets, stock lasts 9 days.
Order this week.* It is pre-filled onto the requisition form she already signs. That is
the integration point: the model completes a form she was going to complete anyway.

**August, the month the city saves her.** Dengue spikes in three upland barangays; ORS and
paracetamol demand there triples for six weeks. Lorna's barangay has had no surge in three
years, so a model trained only on her records forecasts a normal August. She would run out
in eleven days. The federated model has learned the pattern from the three barangays that
just lived it, recognizes the same seasonal shape in her recent fever consults, and flags
the spike two weeks early. She orders ahead.

## What the vignette commits the design to

1. **The model predicts demand, not stock-out.** Stock-out is derived afterward by
   comparing predicted demand against current stock and delivery lead time. Predicting the
   stock-out directly gives a yes/no too late to act on.
2. **Training is invisible.** The midwife never trains anything. No dashboard, no console.
3. **Only weights leave the facility.** Not records, not aggregates of records.
4. **The output is a decision with a reason** — "340 sachets, 9 days of stock" — not a
   probability. Trust comes from the visible justification.
5. **Integration is a form that already exists.** The requisition, the Target Client List,
   the nutrition program list. Never a new application.
6. **Evaluation must be per facility.** Pooled accuracy would hide exactly the effect the
   thesis claims, because gains concentrate in small facilities.

## Friction to state honestly

- **Data entry is the real cost.** If the stock card is not digitized, there is no model.
  This is why the topic pairs naturally with iClinicSys adoption.
- **Consumption is censored.** When a facility runs out, recorded dispensing falls even
  though demand did not. A naive model learns "demand dropped." Handling this properly is
  a contribution in itself.
- **Cold start.** A new facility has no history. Under federation it inherits a usable
  prior on day one — which is a benefit to measure, not an assumption to make.
- **Trust.** The midwife must be able to argue with the output. Reasons, not scores.

## Open decisions

- **Which task carries the claim.** Commodity stock-out forecasting is the vehicle used in
  the vignette because the workflow, the data, and the failure mode are all concrete.
  Growth faltering and prenatal follow-up demonstrate the same novelty with different
  labels. The story is fixed; the vehicle is not.
- **Censored-demand handling.** Mask the affected periods, model unmet demand explicitly,
  or bound the estimate. Pick one and defend it.
- **Cold-start definition.** Zero records, or fewer than one season of records.
- **Record threshold.** The number below which federation pays. This is the headline
  deliverable and it can only come from the experiment.
