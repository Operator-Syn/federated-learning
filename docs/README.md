---
title: "Knowledge base index"
type: index
status: active
created: 2026-11-11
---

# Knowledge base

Everything the study needs to defend itself, organised by the question each document answers
rather than by file type. A reader looking for "what does the standard actually cover" and a
reader looking for "what has already been published" should land in different directories.

Three clusters, one per kind of question:

| Directory | Answers | Read first |
|---|---|---|
| [`proposal/`](proposal/) | What this study claims, and how it is bounded | [`topic-2-proposal.md`](proposal/topic-2-proposal.md) |
| [`interoperability/`](interoperability/) | What schema the data contract targets, and what the standard leaves out | [`ph-core-brief.md`](interoperability/ph-core-brief.md) |
| [`literature/`](literature/) | What has been established elsewhere, and what it leaves open | [`literature/README.md`](literature/README.md) |

## proposal/

The approved research plan and the positioning that constrains the opening chapter.

| Document | What it is |
|---|---|
| [`topic-2-proposal.md`](proposal/topic-2-proposal.md) | CSC198 Topic 2 proposal: problem, contributions C1 and C2, research questions RQ1–RQ4, strategy table, experiment matrix, threats to validity |
| [`novelty-and-usecase.md`](proposal/novelty-and-usecase.md) | The working proposition, falsifiable hypotheses H1–H4, the barangay vignette, and the friction list the design must answer for |

## interoperability/

The FHIR layer. Both documents describe a *design artefact* the study specifies, not an
implementation it has validated.

| Document | What it is |
|---|---|
| [`ph-core-brief.md`](interoperability/ph-core-brief.md) | What draft PH Core IG v0.2.0 profiles, the inventory and unmet-demand gap it does not cover, and the claims the paper may and may not make |
| [`fhir-literature-map.md`](interoperability/fhir-literature-map.md) | FHIR and FHIR-plus-FL literature, iClinicSys versus CODA as different layers, and the design obligations that follow |

## literature/

The evidence base. Every source carries a stable `R-ID` so a claim in the proposal or a chapter
draft can be traced back to text.

| Document | What it is |
|---|---|
| [`README.md`](literature/README.md) | Source index: citation, venue, access status, retrieved artifact, and the routes that failed |
| [`rrl-matrix.md`](literature/rrl-matrix.md) | Analysis: the role of each source, what it cannot support, and the gap they jointly leave |
| `sources/R01…R05.md` | One note per source: method, reported numbers, limits, and the sentence it can support |
| `snapshots/`, `fulltext/`, `pdf/` | Retrieved artifacts, kept so a quotation can be audited later |

## Conventions

- **Frontmatter on every document** — `title`, `type`, `status`, `created`/`updated`, `source`.
  `source` records where the content came from, including access dates for anything retrieved.
- **Literature claims cite an `R-ID`.** Prose without one is asserting something the repo cannot
  source.
- **Pin external standards by version.** PH Core is cited as the draft `0.2.0` build with an
  access date, never as a current requirement.
- **Documents disagree on purpose only when they are dated.** Two files written weeks apart will
  contradict each other; the newer one wins and the older one is corrected or marked
  `status: superseded`. Nothing is silently overwritten.
- **Drafts stay labelled.** A `status: draft` document is not evidence that the work described
  has been done.

## Adding a document

Put it in the cluster whose question it answers. If it answers two, file it where a reader would
look for it, and link to it from the other. Then add a row to the table above — an index nobody
updates is worse than no index.
