---
title: "HL7 FHIR and related literature for the federated health thesis"
type: literature-map
course: CSC198
status: working
created: 2026-10-22
updated: 2026-10-22
source: "Targeted web and Exa search; primary standards, peer-reviewed papers, and Philippine implementation references"
---

# HL7 FHIR and related literature for the thesis

## Thesis context

This review is mapped to the working study, **Evaluating Inclusion-Aware Client Selection for Federated Learning under Intermittent Connectivity**, calibrated to Iligan barangay health facilities. The approved novelty is: **Federated learning lets a facility benefit from events it has never experienced itself.** FHIR is relevant as an interoperability/data representation and extraction layer; it is not itself a federated-learning method or a privacy guarantee.

## Bottom line

Use FHIR to define a portable, locally normalized representation for the records/features used in the experiment, and to motivate a plausible integration path to Philippine health information exchange. The most useful literature is split across (1) FHIR+FL infrastructure, (2) intermittent client availability and selection, (3) rare/low-volume facility benefit and site-wise evaluation, and (4) Philippine health data standards. The thesis's distinctive gap is at their intersection: **how selection under real intermittent reachability distributes rare-event predictive benefit across small facilities**. None of the reviewed sources directly tests that exact combination.

## Curated sources and how to use them

### Standards and Philippine implementation context

1. **HL7 FHIR R4 RESTful API specification.** FHIR R4.0.1, HL7 International. The spec defines common REST interactions but explicitly leaves authentication, authorization and audit collection to other guidance, and servers declare their supported capabilities. Cite this for a standards-level description and for why the implementation must record a server's supported resources/interactions. [1]

2. **HL7 FHIR R4 Observation.** Use for measurements and simple assertions (e.g., vitals, symptoms, lab results); terminology codes and missingness need careful modeling. It is a resource definition, not a complete clinical data model by itself. [2]

3. **HL7 FHIR R4 MedicationRequest.** Represents an order/request for medication for a patient or group; distinguish it from MedicationDispense (supply provided) and MedicationAdministration (medicine actually administered). Do not assume it represents commodity inventory/requisition stock cards without a local profile or extension. [3]

4. **Draft Philippine Core FHIR Implementation Guide (PH Core IG), v0.2.0.** Directly relevant local profiles include Patient, Encounter, Observation, Condition, Organization, Location, Medication, MedicationDispense, MedicationRequest and Provenance. The guide clearly marks itself in development and not approved for public/production use: treat it as evidence of ongoing Philippine standardization, not a finalized requirement. [7]

5. **Zuniga et al. (2026), “Development and implementation of an interoperable local health information exchange platform for the attainment of universal health coverage in the Philippines,” Frontiers in Digital Health.** Reports SMILHIS pilots across Pulilan, Cagayan de Oro City and Pangasinan, using HL7 FHIR integration with local/national frameworks. This grounds the Philippine deployment motivation, but does not evaluate FL, client selection or an Iligan deployment. DOI: 10.3389/fdgth.2025.1650273. [8][20]

### FHIR and federated data / learning systems

6. **Choudhury et al. (2020), “Personal Health Train on FHIR: A Privacy Preserving Federated Approach for Analyzing FAIR Data in Healthcare,” CCIS conference proceedings.** FHIR is used to support federated cohort statistics (hypertension) without individual-level records leaving their source. Helpful architectural precedent for local execution and standardized data; it is not a client-selection experiment. DOI: 10.1007/978-981-15-6315-7_7. [5]

7. **Akhmetov, Latif, Tyler & Yazici (2025), “Enhancing healthcare data privacy and interoperability with federated learning,” PeerJ Computer Science 11:e2870.** Presents a FHIR+FL platform for wearable activity/energy-expenditure prediction, including local FHIR mapping agents and model training; reports FL comparable to centralized learning on evaluated classification/regression tasks. Closest direct precedent for combining the technologies, but domain and data differ from routine barangay records; mapping is described as manually implemented for each wearable data type in the article, so avoid repeating broad automation claims. DOI: 10.7717/peerj-cs.2870. [4][21]

8. **Mullie et al. (2024), “CODA: an open-source platform for federated analysis and machine learning on distributed healthcare data,” Journal of the American Medical Informatics Association 31(3):651–665.** CODA stores de-identified EHR data as FHIR R4 and imaging as DICOM at each site node, with an out-of-firewall orchestration hub that can only receive aggregates or model weights; no inter-site communication is permitted. It supports federated analytics (summarize/breakdown queries with small-cell suppression, meta-analysis) and FL via FedSGD/FedAvg. In a MIMIC-IV/CXR sandbox (4 sites × 1000 patients) FedAvg matched pooled training: AUC 0.82 vs 0.81, F1 0.58 vs 0.55. Feasibility deployment reached 8 of 9 Québec hospitals (>1M patients; 46,181,904 FHIR objects). The authors name legacy→FHIR mapping and terminology harmonization as the biggest barrier, and state that formal differential privacy/secure multiparty computation were deliberately not design requirements. Limitations they admit: single-centre dataset for the FL demonstration, no formal security audit, and an assumption of local FHIR-mapping expertise that did not uniformly hold. This is the closest infrastructure precedent for combining health data standards with real FL, but it is a hospital deployment rather than barangay facilities and does not study inclusion-aware participant selection or intermittency. DOI: 10.1093/jamia/ocad235. [24]

9. **McMurry et al. (2024), “Cumulus: a federated electronic health record-based learning system powered by Fast Healthcare Interoperability Resources and artificial intelligence,” Journal of the American Medical Informatics Association 31(8):1638–1647.** Uses SMART/HL7 Bulk FHIR to extract standardized EHR data; initial deployment involved five health systems and shared aggregate counts, not model weights. Excellent precedent for local data processing, FHIR-based extraction and governance; distinguish federated analytics from federated model training. DOI: 10.1093/jamia/ocae130. [6][16]

10. **Mandl et al. (2020), “Push Button Population Health: The SMART/HL7 FHIR Bulk Data Access Application Programming Interface,” npj Digital Medicine 3:151.** Describes asynchronous population-level FHIR exports in NDJSON. Useful if a facility has a FHIR endpoint and needs batch extraction for a local training pipeline; Bulk Data access is a data-export API, not an FL protocol. DOI: 10.1038/s41746-020-00358-4. [13][17][18]

11. **HL7 FHIR Bulk Data Access (Flat FHIR) Implementation Guide.** Consult the versioned specification before designing an export client; test actual server capabilities rather than assuming universal support. [18]

### Client selection, intermittent connectivity, and measurement

12. **Ribero, Vikalo & de Veciana (2022), “Federated Learning Under Intermittent Client Availability and Time-Varying Communication Constraints,” IEEE Journal of Selected Topics in Signal Processing.** Proposes F3AST, an adaptive sampling method for intermittent clients intended to reduce sampling-variance impact and avoid bias toward more available participants. Directly relevant to intermittency and sampling, but experiments use synthetic data, CIFAR100 and Shakespeare, not clinical records. DOI: 10.1109/JSTSP.2022.3224590. [9][14]

13. **Nishio & Yonetani (2019), “Client Selection for Federated Learning with Heterogeneous Resources in Mobile Edge,” ICC 2019 (FedCS).** Frames selection around resource constraints and round completion/communication time. Useful efficiency baseline for the thesis's resource-aware strategy; pair with explicit participation-equity measures because speed-prioritizing can sideline weak links. [10][19]

14. **Crowson et al. (2022), “A systematic review of federated learning applications for biomedical data,” PLOS Digital Health 1(5):e0000033.** Provides biomedical FL context and argues fairness should be considered across participant selection, optimization and benefit distribution, particularly where site data/resources vary. Useful for justifying per-facility and worst-site reporting. DOI: 10.1371/journal.pdig.0000033. [15][22]

### Rare-event and low-volume site relevance

15. **Lee et al. (2024), “An international study presenting a federated learning AI platform for pediatric brain tumors,” Nature Communications.** FL-PedBrain studies a scarce disease across 19 sites and reports benefit on out-of-network sites; it also analyzes heterogeneity and site imbalance. Supports the general rationale that federation can matter when cases are sparse and distributed, but does not establish that smaller sites necessarily benefit more or address selection policies. DOI: 10.1038/s41467-024-51172-5. [11]

16. **PHT/FAIR implementation guidance.** The HL7 FHIR for FAIR guide describes the Personal Health Train pattern (analysis travels to local data) and flags that local FHIR implementations may differ in supported search modifiers and resource relationships. This is a useful warning for interoperability assumptions and simulation-to-deployment limits. [23]

## iClinicSys vs CODA — different layers, and why that matters

The two are not substitutes. **iClinicSys** is a DOH-developed EMR/HIS for RHUs, HCs and BHS, acting as a system of record and the source of FHSIS and disease registry reporting; it is PhilHealth-validated for Primary Care Benefit/eKonsulta and eClaims, and DOH documents a hybrid architecture that operates offline and online for areas with limited connectivity. [25][26][29] **CODA** is a research federation layer with no clinical workflow; it coordinates federated analytics and model training above whatever systems already hold the data. [24]

Interoperability at the national level is policy-driven rather than API-driven: systems are expected to conform to national health data standards and pass Standards Conformance and Interoperability Validation before submitting to the National Health Data Repository, with the PH Core FHIR IG as the intended profile baseline — still explicitly in development and not approved for production use. [30][31]

Consequence for the study: a facility pipeline needs three things in sequence — (1) structured local data, which iClinicSys supplies; (2) a way to read it out locally as a defined schema, which is the unproven part; and (3) a federation protocol, which is the thesis contribution. CODA supplies (3) while assuming (1) and (2), and reported that legacy-to-FHIR mapping and terminology harmonization were its biggest implementation barriers. No reviewed source closes all three for Philippine barangay facilities.

Design obligations that follow:

- Define a minimal FHIR profile for the feature set as an explicit data contract, not as a claim that iClinicSys is FHIR-conformant.
- Document an iClinicSys→FHIR mapping as a design artefact the thesis specifies.
- Cite iClinicSys's offline/online operation as field evidence that intermittent operation is the normal case, not as an assumption.
- List the absence of a confirmed structured export from iClinicSys in threats to validity; a manual or scripted extract step is a real deployment cost.

Two Philippine field findings reinforce the same point. A study of iClinicSys implementation across Sorsogon City RHUs identified insufficient staff/IT personnel and encoders as the most crucial problem, alongside absent regular maintenance and upgrades. [28] A national formative evaluation of eHealth implementation likewise lists resource management (ICT equipment, stable internet, power supply) and system interoperability among the factors determining whether these systems work in practice. [27] Both support the thesis's stated friction that data entry, not modelling, is the binding constraint.

## PH Core IG v0.2.0 — what it actually specifies (checked 2026-10-22)

Source: https://fhir.doh.gov.ph/phcore/en/index.html and its artifacts/terminology pages. Package `fhir.ph.core#0.2.0`, ci-build, generated 2026-10-20.

- **Base and dependencies.** FHIR R4 4.0.1 (`hl7.fhir.r4.core#4.0.1`), HL7 Terminology (THO) 7.4.0, FHIR Extensions Pack 5.3.0, FHIR Tooling Extensions 1.1.2. No R4B/R5 divergence, so it lines up with CODA, which stores FHIR R4.
- **Governance and status.** UP Manila National TeleHealth Center under DOH guidance, technical assistance from CSIRO Australia. Banner disclaimer: draft, "not for public consumption", data models subject to change; intended to be validated at a Philippine Connectathon. No published version is normative.
- **Artifacts.** 22 resource profiles (AllergyIntolerance, Claim, Condition, Encounter, HealthcareService, Immunization, Location, Medication, MedicationAdministration, MedicationDispense, MedicationRequest, MedicationStatement, Observation, Organization, Patient, Practitioner, PractitionerRole, Procedure, Provenance, RelatedPerson, ServiceRequest, Task), 8 datatype profiles (PH Core Name, Address, NHFR Code, HCPN Code, PIN, PAN, PEN, PhilSys ID), 12 extensions, 9 value sets, 6 code systems, 8 naming systems, and 3 actor definitions (Consumer, Creator, Server).
- **Philippine identifiers.** PhilHealth PIN (member), PAN (accredited institution), PEN (employer), PhilSys national ID, DOH NHFR health facility code, HCPN network code, DOH-assigned procedure IDs, PRC licence in practitioner examples. Patient identifiers are also sliced to include TIN, SSS/GSIS, driver's licence and passport.
- **Terminology.** PSGC for region/province/city/barangay, PSOC for occupation, PSCED for educational attainment, PH FDA Certificate of Product Registration for drugs, a locally published Indigenous Groups code system, and a PWD disability-type code system. Clinical examples use LOINC and SNOMED CT (both with licence notices).
- **Local rules that constrain mapping.** Patient name convention: `given[0]` first name, `given[1]` middle name, `family` family name. Age must be back-derived into `birthDate` at the granularity known (`YYYY`, `YYYY-MM`, `YYYY-MM-DD`); dynamic age elements are prohibited.
- **What is absent.** No CapabilityStatement, no ConceptMap, no Bulk Data (`$export`) guidance, no Questionnaire/QuestionnaireResponse or DiagnosticReport profile, and "There are no Global profiles defined". PSGC, PSOC and PSCED code systems are published as *Mock* systems pending PSA alignment. Must Support is not the same as mandatory.

Consequences for this study: PH Core supplies the target schema but not the bridge. The iClinicSys→PH Core mapping remains ours to write as a ConceptMap or mapping table, and no server-conformance claim is possible without a CapabilityStatement. De-identification also collides with the profile: PH Core Patient slices the identifying identifiers (PIN, PhilSys) as Must Support, so a de-identified CODA node store will not validate as PH Core Patient unless a pseudonymous identifier slice is documented as a deliberate divergence.

## Proposed thesis connection

A defensible framing is: **FHIR provides a standardized, implementation-specific representation and extraction interface for local facility records; FL and client-selection policies determine how learning updates travel and which facilities influence the shared model.** The standards layer makes comparable inputs more plausible, while the thesis tests a different question: whether connectivity-aware selection preserves the value of rare-event learning for under-connected, low-volume facilities.

Practical design implications:

- Define a small, versioned FHIR profile/data dictionary for the chosen task and local input set; do not claim that base FHIR alone guarantees semantic equivalence.
- Report a resource/terminology mapping table and missingness rules. Potential patient/clinical resources include Patient, Encounter, Observation, Condition and Medication* resources; use actual inventory/requisition source fields where FHIR base resources do not fit.
- If data is exported from a FHIR server, record the CapabilityStatement, FHIR release, profiles, terminology systems, export parameters, and transformation steps. Bulk FHIR can provide local batch extracts, but it does not replace FL.
- Simulate FHIR normalization/mapping costs and realistic endpoint availability only if those are in scope; otherwise present FHIR as an integration pathway, not a tested experimental variable.
- Evaluate local-only versus federation per facility, with rare-event recall/AUPRC or capacity-constrained utility, worst-facility performance, participation frequency/starvation, and time/bytes-to-target. Link each facility's gain to its local record count and event rarity.
- Keep privacy claims precise: raw data locality is an architectural property; model updates may leak information. Do not claim that FHIR or FL alone guarantees privacy.

## Research gap and contribution opportunity

The strongest defensible gap is **not** “nobody combines FHIR and FL”—there are now several direct examples. Instead, the reviewed work does not evaluate the interaction among (i) facility-level rare-event benefit, (ii) intermittent participation and selection policy, and (iii) Philippine primary-care interoperability constraints. A contribution could be a controlled simulation/calibration study measuring whether inclusion-aware selection improves low-volume facility rare-event utility, and its time/communication cost, using a documented FHIR-aligned data contract.

## Quality and scope cautions

- FHIR standardizes structures and APIs, but semantic interoperability still depends on profiles, codes, local mappings and conformance testing.
- The Philippines Core IG located in this search is explicitly draft/in development; confirm its status before citing it as policy or normative guidance.
- Most direct FHIR+FL studies use wearables, oncology or large hospital systems; transfer to barangay facilities and TB/inventory workflows is not established.
- “Federated analytics” may mean counts/statistics rather than iterative model training. Label the distinction in the literature review.
- Search did not find a peer-reviewed Philippine study combining FHIR, FL client selection, intermittent connectivity and rare-event per-facility benefit; phrase this as a scoped search result, not a universal proof of absence.

## Sources

[1] https://hl7.org/fhir/R4/http.html
[2] https://hl7.org/fhir/R4/observation.html
[3] https://hl7.org/fhir/R4/medicationrequest.html
[4] https://peerj.com/articles/cs-2870
[5] https://link.springer.com/chapter/10.1007/978-981-15-6315-7_7
[6] https://academic.oup.com/jamia/article/31/8/1638/7690920
[7] https://fhir.doh.gov.ph/phcore/en/index.html
[8] https://www.frontiersin.org/journals/digital-health/articles/10.3389/fdgth.2025.1650273/full
[9] https://users.ece.utexas.edu/~gustavo/papers/RVD22j.pdf
[10] https://arxiv.org/pdf/1804.08333
[11] https://www.nature.com/articles/s41467-024-51172-5
[13] https://pmc.ncbi.nlm.nih.gov/articles/PMC7678833
[14] https://doi.org/10.1109/JSTSP.2022.3224590
[15] https://doi.org/10.1371/journal.pdig.0000033
[16] https://doi.org/10.1093/jamia/ocae130
[17] https://doi.org/10.1038/s41746-020-00358-4
[18] https://hl7.org/fhir/uv/bulkdata
[19] https://arxiv.org/abs/1804.08333
[20] https://doi.org/10.3389/fdgth.2025.1650273
[21] https://pubmed.ncbi.nlm.nih.gov/40567682
[22] https://journals.plos.org/digitalhealth/article?id=10.1371/journal.pdig.0000033
[23] https://build.fhir.org/ig/HL7/fhir-for-fair/PHT.html
[24] https://doi.org/10.1093/jamia/ocad235
[25] https://ro9.doh.gov.ph/iclinicsys
[26] https://ro2.doh.gov.ph/iclinicsys
[29] https://www.philhealth.gov.ph/advisories/2016/adv2016-0040.pdf
[30] https://www.philhealth.gov.ph/about_us/NationalHealthDataRepositoryFramework03282022.pdf
[31] https://fhir.doh.gov.ph/phcore/index.html
[27] https://pmc.ncbi.nlm.nih.gov/articles/PMC11272894
[28] https://uijrt.com/articles/v5/i7/UIJRTV5I70018.pdf
