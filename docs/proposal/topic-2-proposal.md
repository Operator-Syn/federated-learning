---
title: "Topic 2 Proposal — Inclusion-Aware Client Selection for FL under Intermittent Connectivity"
type: thesis-proposal
course: CSC198
group: Beira, Jagonia, Ybanez
status: draft
created: 2026-10-20
updated: 2026-10-20
source: "CSC198-Group-Beira-Jagonia-Ybanez.pdf (Topic 2), grounded in Iligan City CHO access"
---

# Inclusion-Aware Client Selection for Federated Learning under Intermittent Connectivity

**Working title.** Evaluating Inclusion-Aware Client Selection for Federated Learning under Intermittent Connectivity: A Simulation Study Calibrated to Iligan City Barangay Health Facilities

**One line.** When health centers connect unreliably, the way the server picks which centers to train with decides both how fast the model becomes usable and whether the least-connected centers ever influence it.

## 1. Problem

FedAvg selects clients uniformly at random each round. That assumes clients are interchangeable and always reachable. In a city health system split across many barangay facilities, neither holds:

- Facilities differ in bandwidth, power stability, and staff availability.
- A round cannot complete until the slowest selected client responds, so a straggler taxes every other participant.
- A selection policy that simply prefers fast clients reaches a target faster, but may permanently exclude low-participation facilities from the global model.

The result is a policy trade-off that nobody has measured for this setting: **efficiency against inclusion.**

## 2. Contributions and research questions

Two linked contributions, in this order:

**C1 - A usable prediction model.** A risk model built only from inputs a barangay health facility can actually collect, validated for discrimination, calibration, and net clinical benefit, and compared against current practice at the real operating capacity.

**C2 - A distributed way to train it.** Evidence on what it costs, in wall-clock time and participation equity, to train that model across facilities with unreliable connectivity, and which client selection policy pays least for it.

The link between them is the thesis claim: a model can only be called deployable in this health system if it can be *trained* without moving records out of facilities. C2 is not decoration on C1; it is one of C1's usability conditions.

**RQ1 (model).** Which candidate model achieves clinically usable performance from BHS-collectable inputs, and how does it compare with current practice at the available testing capacity?

**RQ2 (efficiency).** How do client selection strategies affect time to reach the target performance, and how does that gap change as connectivity degrades?

**RQ3 (robustness).** How does intermittent client availability affect convergence and per-client predictive performance?

**RQ4 (inclusion).** Which selection policies reach the target in the least time without driving any facility below a participation floor, and what does that floor cost?

RQ4 is framed as a constrained comparison rather than "does resource-aware selection disadvantage anyone." The weaker framing invites a yes/no answer the data cannot settle; the constrained framing produces a policy recommendation.

## 3. The model (Contribution C1)

### 3.1 What "usable" means, operationally

"Usable" is a claim that must be defended, so it is defined as five testable conditions:

| ID | Condition | Test |
|----|-----------|------|
| U1 | Inputs collectable at a BHS counter in under three minutes, no new lab equipment | Feature audit against the existing intake form |
| U2 | Discrimination established | AUROC and AUPRC reported against the prevalence baseline; threshold agreed with adviser |
| U3 | Calibrated | Calibration slope 0.8-1.2, intercept near zero, Brier score reported |
| U4 | Beats current practice at real capacity | Precision@k above the existing symptom-based or nurse-judgement rule |
| U5 | Trainable without moving records | Satisfied only by the federated protocol in section 4 |

U5 is what forces the FL chapter to exist. If the model could be trained centrally, the second contribution would be optional, and reviewers will say so.

### 3.2 Candidate models and selection protocol

Train three candidates centrally on pooled data, choose by clinical utility rather than by accuracy:

| Candidate | Why it is in the comparison |
|-----------|----------------------------|
| Logistic regression, ~15 features | Interpretable, stable on few hundred records per facility, coefficients printable on a form |
| Gradient-boosted trees | Strong tabular baseline; Flower ships FedXgbBagging for the federated stage |
| Small MLP (64-32) | Capacity ceiling check, and the communication-cost contrast |

Selection protocol: 5-fold cross-validation stratified by facility, then leave-one-facility-out validation to test whether the model transports to an unseen facility. Report AUROC, AUPRC, Brier score, calibration slope and intercept, precision@k at capacity k, net benefit by decision-curve analysis, and subgroup performance by sex, age band, and facility stratum.

The winner is frozen before any federated run. Changing the model after seeing federated results invalidates the comparison.

### 3.3 Feature set (TB prioritization package)

All answerable at the counter; laboratory results are optional additions, not requirements.

| Group | Fields |
|-------|--------|
| Demographics | age, sex |
| Symptoms | cough >= 2 weeks, fever >= 2 weeks, weight loss, night sweats, hemoptysis, symptom count |
| History | close contact with a known case, prior TB treatment, diabetes comorbidity, smoking, HIV status if recorded |
| Diagnostics, if available | CXR abnormal, Xpert or smear result (label source, not always a feature) |
| Context | barangay notified-case rate |

### 3.4 Operating point and what the model outputs

A probability, a rank within the week's presumptive list, and a top-k shortlist where k equals the available GeneXpert or smear slots. The threshold is a capacity decision, not 0.5. Headline metrics are precision@k, cases found per 100 tests, and missed cases at that capacity.

### 3.5 Per-facility calibration

A score of 0.6 from a high-incidence upland barangay does not mean the same thing as 0.6 from Poblacion. Apply local Platt scaling or isotonic regression on held-out facility data and report scores before and after. Uncalibrated cross-facility scores are not comparable, and this is a deployment blocker that most FL papers ignore.

### 3.6 Go / no-go gate at week 6

If centralized AUROC is below 0.70, or calibration fails after correction, do not proceed to the federated chapter on that task. Switch to defaulter prediction, which has a cleaner and more abundant label, or reframe. A model that cannot be called usable cannot carry a claim about training it.

## 4. Design

### 4.1 Clients

Primary: facility clusters derived from Iligan City's 44 barangays, grouped into 10-15 units by catchment size and connectivity stratum, because many barangays hold too few records to train stably on their own.

Stratification (to be confirmed with CHO facility metadata, not assumed):

- Dense urban (Poblacion, Tibanga and similar)
- Coastal / peri-urban
- Upland (longest travel, weakest links)

Fallback if facility-level separation is not permitted: public tabular dataset with simulated clusters. The study must then say so plainly in every results table.

### 4.2 Data

Preferred: one program whose national form is standardized, so facilities produce comparable schemas.

1. **TB DOTS register** — first choice. Nationally standardized columns; free X-ray, skin test, and GeneXpert at health centers makes test allocation a real constraint.
2. **Immunization or prenatal register** — second choice, also standardized, higher volume.
3. **iClinicSys export** — best case if deployed; confirm version and export format first.

Fallback dataset: CDC Diabetes Health Indicators (UCI, ~253,680 rows; 21 features binary, 35 features three-class). Pima is rejected: 768 rows across 10+ clients is roughly 77 records per client, which is not trainable.

Predictive target must be a decision someone makes, not a label that happens to exist. Candidates, in order of operational value:

- Ranked shortlist for scarce diagnostic slots (yield per 100 tests)
- Referral priority from BHS to city level
- Defaulter risk for scheduled follow-up

### 4.3 Strategies compared

| ID | Strategy | Definition | Role |
|----|----------|------------|------|
| S1 | Uniform random | Sample k of N uniformly each round | Baseline |
| S2 | Resource-aware greedy | Prefer k lowest estimated communication time | Efficiency ceiling, inclusion risk |
| S3 | Availability-first | Prefer currently reachable clients | Realistic naive policy |
| S4 | Fair sampling (FedFS-style) | Raise selection probability of under-participating clients | Inclusion ceiling, efficiency cost |
| S5 | Intermittent participation | Clients drop out per measured probability | Real-world stress baseline |

S2 alone is the PDF's strawman. S4 is what makes the comparison publishable: it establishes whether inclusion is *expensive* or *free*.

### 4.4 Intermittency model

Three regimes, each a labeled parameter set:

| Regime | Online probability | Latency | Dropout |
|--------|-------------------|---------|---------|
| Good | 0.95 | low, stable | rare |
| Mixed | 0.75 | variable | occasional |
| Poor | 0.50 | high, heavy tail | frequent |

Parameters come from one of two sources, and the proposal must name which:

- **Measured** — facility metadata and a one-afternoon connectivity check at a sample of facilities. Preferred; converts "simulated network" into a measured constraint.
- **Assumed** — literature-typical values, explicitly labeled as assumptions with sensitivity analysis across the range.

Straggler rule, fixed before any run: a round proceeds after a timeout with whatever updates arrived, and clients that miss the timeout count as non-participating. The alternative rule (restart the round) must be reported as an ablation because it can flip the ranking.

### 4.5 Metrics

Primary:

- **Time to target** — wall-clock seconds until Macro-F1 first crosses a threshold fixed in advance, derived from a centrally trained reference model.
- **Participation equity** — minimum-to-maximum rounds-participated ratio, plus a starvation count (clients selected in fewer than x% of rounds).

Secondary:

- Macro-F1 at a fixed round budget
- Worst-client Macro-F1
- Cumulative bytes transferred, and bytes to target
- Rounds to target

Accuracy alone is not reported as a headline number; it hides class imbalance.

### 4.6 Experiment matrix

3 connectivity regimes x 5 strategies x 3 heterogeneity levels (IID, moderate, severe Dirichlet) x 3 seeds = 135 runs, plus timeout-rule ablations. Fixed across all runs: model, local epochs, batch size, learning rate, k, target threshold, evaluation split.

Report median with interquartile spread across seeds. A single-seed "faster" result is not a result.

## 5. Two-phase plan

**Phase A — model and harness (weeks 1-6).** Weeks 1-3: train and select the model (RQ1), fix the winner, record its communication footprint. Weeks 4-6: build partitioning, simulation, strategy plug-ins, metrics, and logging. Deliverable: a frozen model plus a reproducible pipeline where every number in the results chapter can be regenerated from a config file. The week-6 gate in 3.6 is the decision point.

**Phase B — Iligan calibration (weeks 7-12).** Replace assumed parameters with measured ones; rerun the matrix on the frozen model; if record-level access is granted, rerun on real facility partitions and report both. Deliverable: the calibrated comparison plus a written policy recommendation for the CHO.

This structure means a denial or delay on data access downgrades the thesis rather than killing it.

## 6. What this contributes

1. **A calibrated TB presumptive prioritization model** built only from BHS-collectable inputs, validated with leave-one-facility-out testing and decision-curve analysis against the current rule at real testing capacity.
2. **A measured, not assumed, intermittency model** for a Philippine city health system, derived from facility metadata and a bounded connectivity check.
3. **Evidence on what inclusion costs**: whether fairness-aware selection is expensive or free at this scale, expressed in minutes of training time.
4. **A selection policy the CHO could adopt**, with its price stated rather than implied.

## 7. Threats to validity

- **Simulated, not deployed.** All results are in-silico. Say it in the abstract, not only in limitations.
- **Single city.** Findings generalize to similar facility networks, not to all LGUs.
- **Target choice determines the answer.** Fix it in methodology; report sensitivity to plus/minus 0.02.
- **Facility counts are small.** 10-15 clients limits statistical power; report effect sizes, not just significance.
- **Baseline fairness.** Both arms get the same k, the same timeout, and the same round budget. An unfair baseline manufactures the result.

## 8. Ethics and data governance

- Data sharing agreement with the city health officer; university research ethics clearance; DPA-compliant safeguards.
- On-site processing only. Line lists do not leave CHO premises; only aggregates and model parameters do.
- Small-cell suppression: any per-facility figure resting on fewer than a threshold number of records is suppressed before reporting. A barangay with three TB cases is a very short list.
- No claim that FL or any selection policy provides privacy protection. Privacy is a governance property here, not a measured one.

## 9. Honest objection to answer in Chapter 1

If all facility data physically sits on one CHO server, federated learning is not strictly necessary and centralized training would be simpler. The defense: facility-level separation is real policy, data is meant to stay at the point of care, and the architecture under evaluation is the deployment target. Frame it as an evaluated deployment design, never as a necessity claim.

## 10. Deliverables

- Reproducible experiment harness (config-driven, seeded)
- Results chapter: 3 regimes x 5 strategies, time-to-target and equity tables
- Calibration appendix: measured facility parameters, or stated assumptions with sensitivity
- One-page policy recommendation for the CHO

## References

Checked 2026-10-20.

- Flower: A Friendly Federated Learning Framework — FedFS fair sampling strategy described in appendix. https://arxiv.org/pdf/2007.14390
- Flower documentation, strategy tutorials and tabular example. https://flower.ai/docs/framework/tutorial-series-use-a-federated-learning-strategy-pytorch.html
- LongFed: Emulating Full Participation, fair client selection. https://arxiv.org/html/2405.13584v2
- FedSampling: A Better Sampling Strategy for Federated Learning (IJCAI 2023). https://www.ijcai.org/proceedings/2023/0462.pdf
- CDC Diabetes Health Indicators, UCI (~253,680 rows). https://archive.ics.uci.edu/dataset/891/cdc+diabetes+health+indicators
- DOH iClinicSys, primary care EMR for RHU/HC/BHS. https://ro9.doh.gov.ph/iclinicsys/
- Iligan City free TB treatment services, diagnostics at health centers. https://pia.gov.ph/news/iligan-strengthens-citys-free-tb-treatment-services/
- Iligan City CHO laboratory services. https://www.iligannews.com/iligan-city-health-office-offers-affordable-laboratory-tests/
- TCI Philippines and Iligan City data quality management engagement. https://tciurbanhealth.org/collaborative-efforts-between-tci-philippines-and-iligan-city-enhance-commitment-to-data-quality-management/
- Federated learning in healthcare: review of the deployment gap between simulated and real-world implementations. https://link.springer.com/article/10.1140/epjs/s11734-026-02475-9