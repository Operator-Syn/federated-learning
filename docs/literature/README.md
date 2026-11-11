---
title: "RRL subsystem — federated learning for demand forecasting in healthcare supply chains"
type: literature-subsystem
status: active
created: 2026-10-22
---

# Literature subsystem

Evidence base for the thesis's related-literature chapter. Every source gets a stable ID
(`R01`…), a note, and whatever artifacts could be lawfully retrieved. Claims in the proposal
or chapter draft should cite an `R-ID` so the trail back to text stays intact.

## Layout

```
docs/literature/
├── README.md                 # this file — index, access status, provenance
├── rrl-matrix.md             # the analysis: role of each source, gap, RQ mapping
├── sources/R01…R05.md        # one note per source: method, numbers, limits, citing sentence
├── pdf/                      # publisher PDFs, open access only
├── fulltext/                 # complete JATS XML where the publisher blocks PDF
└── snapshots/                # frozen text of the page as retrieved, for auditing quotes
```

Sibling clusters: [`../proposal/`](../proposal/) holds what the study claims, and
[`../interoperability/`](../interoperability/) holds the FHIR and PH Core layer.

## Sources

| ID | Citation | Venue / type | Access | Artifact |
|----|----------|--------------|--------|----------|
| R01 | Aryani F, Destiani DP, Satibi S, Harsanto B, Pradipta IS (2026). Determinants, models, performances, and strategies of supply chain to address medicine stockouts in primary health care: a scoping review | *J Pharm Policy Pract* 19(1):2659077 · review (PRISMA-ScR) | Open access, CC BY-NC | `fulltext/R01-…jats.xml` (complete) |
| R02 | Saha E, Rathore P (2024). A smart inventory management system with medication demand dependencies in a hospital supply chain: a multi-agent reinforcement learning approach | *Computers & Industrial Engineering* 191:110165 · journal | Paywalled | `snapshots/R02-…md` |
| R03 | Chen J, Xu Z, Zhu B (2026). Prescriptive analytics for hospital drug inventory: a context-aware multi-channel neural network for integrated forecasting and optimization | *Omega* 143:103557 · journal | Paywalled | `snapshots/R03-…md` |
| R04 | Johnson LL, Ebakivie O (2026). Triple A: how analytics, AI, and algorithms are improving inventory management in healthcare | *Logistics* 10(5):103 · systematic review | Open access, CC BY | `pdf/logistics-10-00103-johnson-2026.pdf` (24 pp.) |
| R05 | Singh G, Aggarwal N (2025). Integrating federated learning and deep Q-networks for resilient healthcare supply chain optimization amidst uncertain demand (FedDQN-SC) | *ICAIIHI 2025*, Raipur · conference | Paywalled | `snapshots/R05-…md` |

DOIs: R01 `10.1080/20523211.2026.2659077` · R02 `10.1016/j.cie.2024.110165` ·
R03 `10.1016/j.omega.2026.103557` · R04 `10.3390/logistics10050103` ·
R05 `10.1109/ICAIIHI67124.2025.11403491`

## What could not be downloaded, and why

Recorded so nobody re-litigates it later and so no one assumes a PDF exists.

| ID | Blocker | Detail |
|----|---------|--------|
| R01 | NCBI proof-of-work challenge | Every `/articles/PMC13123085/pdf/*` path returns an 1817-byte stub running `pow-*.js` before issuing the file. Publisher route (Taylor & Francis, `doi/pdf/…`) returns 403 to non-browser clients. The complete JATS XML is stored instead — strictly better for quoting and page-free. Manual download: open <https://pmc.ncbi.nlm.nih.gov/articles/PMC13123085/pdf/> in a browser. |
| R02 | Paywall | Unpaywall reports no OA copy. Landing page served through `doi.org` gives abstract, introduction, literature review, and conclusions; the middle (model formulation, Table 1, case-study tables) is behind the paywall. |
| R03 | Paywall | Unpaywall: closed. Highlights, introduction, method overview, experimental setup, conclusion captured. Numerical results tables not available. |
| R05 | Paywall | Unpaywall: closed. Abstract and the opening of §I captured; references block returns "not available". |

Paywalled sources are cited from abstract + landing page only. No number in the notes is
attributed to a section that was not actually read — where a figure comes from the authors'
own literature review rather than their experiment, the note says so.

## Refresh

```bash
# R01 full text (JATS, complete)
curl -s "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13123085/fullTextXML"

# R02 / R03 landing pages — route through doi.org; the bare sciencedirect.com URL
# intermittently returns an "outdated browser" interstitial to non-browser clients
curl -sL "https://doi.org/10.1016/j.cie.2024.110165"
curl -sL "https://doi.org/10.1016/j.omega.2026.103557"

# R04 PDF (the /pdf path on mdpi.com 403s; the asset host does not)
curl -sL "https://mdpi-res.com/d_attachment/logistics/logistics-10-00103/article_deploy/logistics-10-00103.pdf"

# OA status for any DOI, before assuming a PDF is obtainable
curl -s "https://api.unpaywall.org/v2/<DOI>?email=<address>"
```

## Licensing

`pdf/` holds one CC BY article (R04). R01's JATS XML is CC BY-NC. Both may be kept locally and
quoted with attribution; neither may be redistributed commercially. Paywalled sources are
represented by metadata and short quoted passages only — do not add pirated PDFs to this
directory, and do not commit a paywalled PDF obtained from a shadow library.
