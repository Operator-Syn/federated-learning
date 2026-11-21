# Technical specification

The reference document for the system's vocabulary, entities, metrics and conformance
requirements. **This is not the thesis paper.** The paper argues; this specifies. The paper
cites section numbers from here instead of restating definitions, so the two cannot drift.

| file | purpose |
|---|---|
| `technical-spec.tex` | standalone document; builds to a PDF you can hand to the City Health Office as a technical annex |
| `sections/` | the shared definitions, `\input` by this document and by the paper's appendix |
| `glossary.yml` | the canonical machine-readable names the implementation keys its plug-ins and entities by |
| `Makefile` | `make -C docs/spec` builds the PDF, `make -C docs/spec check` runs the name-drift check |

## Build

```bash
make -C docs/spec          # PDF, via latexmk
make -C docs/spec check    # glossary vs implementation
make -C docs/spec clean    # remove build artifacts
```

The PDF is a build artifact and is not committed. The build needs `latexmk`; `make -C docs/spec`
drives it from the repository root, so no LaTeX step has to be run by hand.

## How the paper uses it

The paper's appendix includes the same files rather than copying them. The paper draft is not in
this repository yet; the paths below are relative to a main file one directory below the repository
root:

```latex
\appendix
\section{Technical specification}
\input{../docs/spec/sections/02-entities-domain}
\input{../docs/spec/sections/05-policies}
\input{../docs/spec/sections/06-metrics}
```

Those files expect four things in the host preamble, all of them defined in
`technical-spec.tex`:

| name | what it is |
|---|---|
| `\core` | filled square marking entities the first build implements (drawn, not a text glyph) |
| `L{width}` | ragged-right paragraph column type |
| `spectab{spec}` | the table environment: grid, header fill, zebra rows |
| `rule`, `headcell`, `rowshade` | the three colours that environment uses |

Copy that block, or `\usepackage` a shared preamble file, and the sections compile in the paper
exactly as they do here. They also need the packages those definitions rest on — `longtable`,
`xcolor` with the `table` option, `array`, `amsmath`, `geometry` and `hyperref` — and every
`\ref`/`\eqref` in a section needs its target label defined in the host document, or the citation
prints as `??`. Without `spectab` the first table stops the build with an undefined environment —
which is a clear failure rather than a silently restyled table.

Change a definition once, in `sections/`, and both documents change together. Restating a
definition in a thesis chapter is how the code, the annex and the paper end up disagreeing.

## The glossary is the contract

Entity, policy and parameter names are what drift first — `adaptive sampling` in the paper,
`availability_aware` in code, `availability-aware` in the review. `glossary.yml` is the
single list of identifiers; `scripts/check_glossary.py` parses both it and the
implementation's policy registry, and fails when either has a name the other lacks. It
skips the comparison with a clear message while the implementation does not yet exist.

Add a name in both places, in the same change. That is the whole discipline.

## Status

Version 0.1. Domain and system entities are agreed; governance entities are agreed as conformance
requirements the design must meet, not as software to build. Section 9 lists the decisions still
open — they are recorded rather than guessed, and the text that depends on them cites the section
rather than assuming a default.

Nothing in this document is a result. Until a data-sharing agreement and ethics clearance
exist, every value the system processes is synthetic and labelled as such.
