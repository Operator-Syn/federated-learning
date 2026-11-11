---
title: "PH Core IG — group brief and paper-ready text"
type: paper-brief
course: CSC198
group: Beira, Jagonia, Ybanez
status: draft
created: 2026-10-22
updated: 2026-10-22
source: "fhir.doh.gov.ph/phcore v0.2.0 (ci-build, generated 2026-10-20), accessed 2026-10-22; cross-checked against FHIR R4 4.0.1 resource list"
---

# PH Core IG — what the group needs to know, and what goes in the paper

## 1. The note

For the group, and for anyone who asks why we are leaning on this at all.

**What it is.** The Philippines has a draft national FHIR standard — PH Core — currently at version 0.2.0. It is not a student or vendor effort. The UP Manila National TeleHealth Center maintains it under DOH guidance, with technical assistance from CSIRO Australia, and the guide itself states that program-specific guides should inherit from PH Core rather than invent their own. It takes FHIR R4 as its base and adds the Philippine layer: PhilHealth and PhilSys identifiers, PSGC geography down to the barangay, PH FDA drug codes, published across 22 resource profiles. Whichever way the draft evolves, that is the direction national interoperability is being pointed at, and a data contract that anticipates it is worth more than one we invent from scratch.

**Why it helps us specifically — and why the narrowness is the useful part.** PH Core profiles Patient, Encounter, Observation, Condition, the whole Medication family, Provenance, Organization and Location. That covers the patient side of our feature set and the dispensing side of the commodity story. It does not cover inventory. FHIR R4 itself has `SupplyRequest` and `SupplyDelivery` for requisitions and deliveries, but no resource for stock on hand — `InventoryItem` only arrives in R5 — and PH Core profiles none of the three. There is also no standard element anywhere for unmet demand: the patient turned away because the shelf was empty.

So we are not conforming to PH Core; we are deriving from it, and declaring an extension for the inventory side. That sounds like a compromise and is actually the stronger position. Two of the quantities our model depends on most — current stock, and demand that went unserved — are not representable in the national standard today. That is a gap in the standard, not a failure in our pipeline, and stating it precisely is more defensible than quietly inventing a schema and hoping nobody asks why.

**On the draft status.** We do not hide it and we do not apologise for it. We cite v0.2.0 as a draft, pin the version because it is a ci-build that will change, and say plainly that no published version is normative. What we get in exchange is a target with institutional backing and published artifacts we can actually validate against. That is a stronger footing than an ad hoc dictionary, and it costs one paragraph to disclose.

## 2. What PH Core actually is

- **Base:** FHIR R4 4.0.1 only. Dependencies: `hl7.fhir.r4.core#4.0.1`, THO 7.4.0, Extensions Pack 5.3.0.
- **Publisher:** UP Manila National TeleHealth Center, under DOH guidance, technical assistance from CSIRO Australia.
- **Status:** draft, ci-build, package `fhir.ph.core#0.2.0`. Banner says "not for public consumption" and that data models may change. Intended to be validated at a Philippine Connectathon.
- **Structure:** three layers — FHIR R4 base → PH Core (profiles, extensions, local terminology, actors) → program-specific IGs that inherit from PH Core.
- **Size:** 22 resource profiles, 8 datatype profiles, 12 extensions, 9 value sets, 6 code systems, 8 naming systems, 3 actor definitions (Consumer, Creator, Server).

**Philippine identifiers it defines:** PhilHealth PIN (member), PAN (accredited institution), PEN (employer), PhilSys national ID, DOH NHFR health facility code, HCPN network code, DOH- and PhilHealth-assigned procedure IDs. Patient identifiers are also sliced for TIN, SSS/GSIS, driver's licence, passport.

**Terminology:** PSGC (region/province/city/barangay), PSOC (occupation), PSCED (education), PH FDA Certificate of Product Registration (drugs), locally published Indigenous Groups and PWD disability-type code systems. Clinical examples use LOINC and SNOMED CT.

**Two local rules that will bite any mapper:**
1. Middle name goes in `given[1]`, not an extension or suffix.
2. Age is never stored. It is back-derived into `birthDate` at the granularity known (`YYYY`, `YYYY-MM`, or full date), approximation flagged in display, and dynamic age elements are prohibited.

**What it does not contain** (verified against the artifacts summary, not assumed):
- No CapabilityStatement — only ActorDefinitions. No defined server interaction surface.
- No ConceptMap at all — nothing that maps a legacy or program vocabulary onto PH Core.
- No Bulk Data (`$export`) guidance.
- No DiagnosticReport or Questionnaire profile. Composition and Coverage exist only as examples.
- No SupplyRequest, SupplyDelivery, or inventory resource of any kind.
- PSGC, PSOC and PSCED ship as **Mock** code systems pending PSA alignment.
- "There are no Global profiles defined." Must Support is not mandatory.

## 3. The finding that belongs in our methodology

FHIR R4 4.0.1 has `SupplyRequest` and `SupplyDelivery`, but **no inventory resource** — `InventoryItem` first appears in R5. **PH Core profiles neither.** And there is no standard element anywhere for *unmet demand* (a patient turned away because the shelf was empty).

This matters because our vignette is about ORS stock running out, and our friction list already says "consumption is censored." The standard confirms the friction architecturally: the two quantities the model most needs — stock on hand, and demand that went unserved — have no national FHIR representation at all. That is not our implementation failing. That is a gap in the standard.

**Coverage table — our feature set against the standard:**

| Our data element | FHIR R4 4.0.1 | PH Core profile | Verdict |
|---|---|---|---|
| Age, sex | `Patient.birthDate`, `.gender` | `ph-core-patient` | Covered; age must be back-derived, never stored |
| Barangay of residence | `Address` + PSGC | `ph-core-address` + barangay/province/region extensions | Covered, but code systems are **Mock** |
| TB symptoms and signs | `Observation` (LOINC) | `ph-core-observation` | Structurally covered; no PH value set for a TB symptom panel — we define the LOINC set |
| TB diagnosis | `Condition` (SNOMED CT) | `ph-core-condition` | Covered |
| Sputum / GeneXpert result | `Observation` | `ph-core-observation` | Covered |
| Dispensing quantity (ORS, amoxicillin) | `MedicationDispense.quantity` | `ph-core-medicationdispense` | Covered; drug code binds to PH FDA CPR (preferred) |
| Facility identity and network | `Organization.identifier` | NHFR / HCPN / PAN | Covered — useful as site metadata for client selection |
| Facility catchment and stratum | `Location` | `ph-core-location` | Covered |
| Who entered the record | `Provenance` | `ph-core-provenance` | Covered |
| **Stock on hand (stock card balance)** | **none** | **none** | **Not covered — we define it** |
| **Requisition to RHU** | `SupplyRequest` | none | R4 has the resource; PH Core does not profile it |
| **Delivery received** | `SupplyDelivery` | none | R4 has the resource; PH Core does not profile it |
| **Unmet demand** | **none** | **none** | **Not covered — no standard element exists** |

Consequence for Chapter 3: our data contract is **PH Core–derived, not PH Core–conformant**. Clinical and dispensing fields inherit from PH Core profiles. Inventory fields are declared as an explicit, documented extension set (or a sidecar table in the harness) with the gap named. We pin v0.2.0 and say so in the methods.

## 4. Claims we can make, and claims we must not make

| Safe to write                                                                | Do not write                                                              |
| ---------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| PH Core is the intended national profile baseline, currently draft at v0.2.0 | PH Core is the Philippine FHIR standard that systems must follow          |
| Our contract inherits from PH Core profiles where coverage exists            | Our pipeline is PH Core conformant / certified                            |
| FHIR reduces structural variance to a testable minimum                       | FHIR makes Philippine health data interoperable                           |
| The inventory gap is documented and we specify our own representation        | Our representation is compatible with a future national inventory profile |
| De-identification is a governance property we impose                         | FHIR or FL provides privacy protection                                    |
| We pin v0.2.0 because it is a ci-build and will change                       | v0.2.0 is stable / final                                                  |

One technical point worth anticipating from a panelist: conformance runs one way. A PH Core resource is always a valid R4 resource; a plain R4 resource is not necessarily PH Core. So PH Core is a subset, not a dialect — which is why there is no version-translation layer between PH Core and any R4 store, including a CODA-style node.

Second point: de-identification collides with the profile. `ph-core-patient` slices PhilHealth PIN and PhilSys ID as Must Support. A de-identified store will not validate as PH Core Patient unless a pseudonymous identifier slice is declared as a deliberate divergence. Say that we declare it, rather than letting a validator find it for us.

## 5. Where it goes in the paper

| Chapter | Use |
|---|---|
| Ch. 1 — Background | Two sentences: DOH has a draft national FHIR core; interoperability in the Philippines is policy-driven, not API-driven. Do not oversell it. |
| Ch. 2 — RRL | PH Core as the local instance of the FHIR-plus-FL literature (Mullie/CODA, McMurry/Cumulus). The gap: no reviewed work evaluates FL client selection under Philippine primary-care interoperability constraints. |
| Ch. 3 — Methodology, data contract | The coverage table above, plus the gap statement and the version pin. This is the section that earns reviewer trust. |
| Ch. 3 — Threats to validity | Add: "No confirmed structured export from iClinicSys; the PH Core mapping is a design artefact we specify, not a validated implementation." |
| Ch. 5 — Discussion | The inventory gap as a contribution-adjacent finding: what a national inventory IG would need to define before commodity forecasting is portable across LGUs. |

## 6. Citation block

> Philippine Department of Health & UP Manila National TeleHealth Center. (2026). *Draft Philippine Core FHIR Implementation Guide* (Version 0.2.0, ci-build, package `fhir.ph.core#0.2.0`, generated 2026-10-20). https://fhir.doh.gov.ph/phcore/en/index.html — accessed 2026-10-22. Draft; not for production use.

Supporting:
> Health Level Seven International. (2019). *FHIR Release 4 (v4.0.1)*. https://hl7.org/fhir/R4/

> Aguirre, A. et al. / Mullie, L. et al. (2024). CODA: an open-source platform for federated analysis and machine learning on distributed healthcare data. *JAMIA* 31(3), 651–665. https://doi.org/10.1093/jamia/ocad235

*(Fill in the CODA author list from the PDF in the repo before submission — I have the DOI and venue from the literature map but not the verified author string.)*

## 7. If a panelist pushes back

**"Is this standard even real if it's a draft?"**
It's a published, versioned, machine-readable package with named ownership and a stated governance process. That is what a draft standard looks like. We cite it as a draft and pin the version. Its artifacts still tell us what DOH intends to converge on, which is exactly what a data contract needs to anticipate.

**"Why model against something that may change?"**
Because the alternative is inventing a schema with no institutional backing. A pinned draft profile is a stronger foundation than a bespoke dictionary, and it costs us one paragraph to state the version risk.

**"Isn't FHIR enough on its own?"**
No. FHIR standardizes structure and APIs, not meaning. PH Core ships zero ConceptMaps, so every facility still maps its own vocabulary. That residual work is what our mapping table documents and what the literature names as CODA's costliest implementation barrier.
