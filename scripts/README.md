# scripts

Repository tooling. Standard library for the most part; `check_glossary.py` also needs PyYAML (a
transitive dependency in `uv.lock`, not yet declared in `pyproject.toml`) and `nbstripout_safe.py`
needs nbstripout (declared). Run scripts through `uv` so they see `.venv`:

```bash
uv run python scripts/check_spec.py
```

The `Makefile` is *not* here: it lives at the repository root, because `make` reads `./Makefile` from
the directory you are standing in, and its targets use root-relative paths. Its eleven targets:

```bash
make help      # list every target, generated from the Makefile's own comments
```

| target | what it does | when you run it |
|---|---|---|
| `make help` | lists targets from the `##` comments beside each rule | when you forget a target |
| `make sync` | `uv sync` from `uv.lock` | after cloning, or after changing dependencies |
| `make spec` | builds `docs/spec/technical-spec.pdf` | after editing a section under `docs/spec/sections/` |
| `make spec-check` | glossary names vs the implementation's policy registry | after adding, renaming or removing a policy |
| `make spec-audit` | builds the PDF and audits it: the symbol each display equation defines must appear in the notation table, and a fixed list of repository-only phrases must not appear in the PDF. Page fill, stranded headings and overfull lines are **reported as notes, never failures** — layout is the author's call | before sending the specification to anyone |
| `make selftest` | feeds each checker a fixture it must reject, so a gate that has stopped biting fails the build instead of passing everything | whenever a checker or a Makefile target changes |
| `make lint` | ruff errors only — the tier the pre-commit hook blocks on | before committing |
| `make format` | applies `ruff format` to `src` and `scripts` | when the hook warns about formatting drift |
| `make notebooks` | notebook storage check, judging the form git would commit | before committing a notebook |
| `make check` | `lint` + `spec-check` + `spec-audit` + `notebooks` | the pre-commit gate, by hand |
| `make clean` | removes the spec PDF, LaTeX auxiliaries, ruff/pytest caches and `__pycache__` | when the tree looks cluttered |

The target list is generated from the `##` comments in the root `Makefile`, so the comments *are* the
documentation: a new target without a `##` line is invisible in `make help`, and a stale comment is
worse than none.

| script | what it does | when you run it |
|---|---|---|
| `setup_notebook_filters.py` | registers the `nbstripout` git filter in this clone | once per clone, after `uv sync` |
| `setup_git_hooks.py` | points `core.hooksPath` at `scripts/git-hooks/` | once per clone, after `uv sync` |
| `git-hooks/pre-commit` | lint gate: ruff errors block, formatting drift warns | automatic, on every `git commit` |
| `nbstripout_safe.py` | the clean-filter/textconv wrapper itself | never by hand — git invokes it |
| `check_notebook_outputs.py` | fails when a committed notebook still holds outputs | CI, and before pushing if you skipped the filter |
| `check_glossary.py` | validates `glossary.yml`, then compares its four policy-family identifiers against the registry the implementation actually holds. The module is executed rather than parsed, because a `dict.fromkeys` registry or a key added at runtime is invisible to a literal read, and a module that raises is reported rather than falling back to its source text. Policy names only: entities are not compared. Reports **skipped** while `src/fl_thesis/federation/policies.py` does not exist, and **fails** if it exists but cannot be executed or holds no registry | after adding, renaming or removing a policy |
| `check_spec.py` | builds the specification and audits it. Fails on three defects: a symbol a display equation defines but the notation table omits, a phrase from a fixed list of repository-only wording inside a PDF meant to be handed out alone, and a PDF it cannot read at all — because an unreadable file must never pass as an empty one. It reads left-hand sides, not every symbol in the body. Page fill, stranded headings and overfull lines are printed as notes for the author's eye and never fail the run | before handing the PDF to a reader |
| `selftest_gates.py` | the tests for the gates themselves: a corrupt read, a runtime registry, a raising module, a bypassed extraction, an unknown stored form. Each test asserts the gate *fails* on a fixture it must reject, because a checker that cannot fail is a green light with no bulb. Runs in `make check` | whenever a checker changes |
| `refresh-references.py` | regenerates `docs/literature/references.bib` from Zotero | whenever the Zotero library changes |

## Fresh clone setup

```bash
uv sync                                        # environment, and the tools below
uv run python scripts/setup_notebook_filters.py
uv run python scripts/setup_git_hooks.py
uv run python scripts/refresh-references.py    # only if the bibliography is missing or stale
```

Both setup scripts are idempotent; rerun them after moving the checkout or changing interpreters.

## What lives where, and why

Git stores filter commands and hook paths in `.git/config`, which is **not** part of the repository.
That is the whole reason two registration scripts exist: the wrapper and the hook are committed files,
while the wiring that points at them has to be redone per clone. If you ever see a notebook commit
with outputs attached, or a commit sail past a lint error, the first thing to check is that these two
scripts have been run.

## `nbstripout_safe.py`

The committed half of the notebook filter: `git` runs it as the clean filter when you stage an
`.ipynb`, and as the textconv driver when you read a diff. It strips cell outputs and execution
counts, restores `SIGPIPE` where the platform has it (so a closed pager does not print a traceback),
and owns the `--quiet` flag, which nbstripout 0.9.x does not define.

Registered values, for reference:

```text
filter.nbstripout.clean   "<venv python>" "<repo>/scripts/nbstripout_safe.py"
filter.nbstripout.required true
diff.ipynb.textconv       "<venv python>" "<repo>/scripts/nbstripout_safe.py" --quiet -t
```

Maintenance: if you rename this file, update `setup_notebook_filters.py` — nothing else knows the
name. It must stay dependency-free apart from nbstripout, because git runs it outside the shell you
think you are in.

## `git-hooks/pre-commit`

Two tiers, deliberately unequal:

- `ruff check .` over the repository — **blocks** the commit and prints ruff's own output.
- `ruff format --check src scripts` — **warns** with the files and the fix command, then allows the
  commit. Blocking on formatting teaches people `--no-verify`, which disables the blocking tier too.
- If ruff cannot be found, the hook aborts: a linter that silently does not run is worse than none.

Formatting is scoped to `src` and `scripts` because `ruff format` rewrites notebook JSON, which churns
diffs and can race an open kernel.

Bypass with `git commit --no-verify` when a commit genuinely needs to go in dirty.

Maintenance: add a hook by dropping another executable in this directory and listing it in `HOOKS` in
`setup_git_hooks.py`. Keep hooks Python — git runs them through `sh` on Windows, and a Python file
with a shebang is the portable choice.

## `check_notebook_outputs.py`

The remote backstop for collaborators who never ran `setup_notebook_filters.py`: the clean filter
strips notebooks on the way into *their* commit, but nothing forces them to install it. This script
fails the change when a committed notebook still carries outputs or execution counts. Standard library
only, so `.github/workflows/notebooks.yml` runs it on a bare runner with no environment setup.

```bash
uv run python scripts/check_notebook_outputs.py                # CI: judges the checkout
uv run python scripts/check_notebook_outputs.py --stored-form  # local: judges what a commit stores
uv run python scripts/check_notebook_outputs.py notebooks/00-workspace-check.ipynb
```

Two modes, on purpose. CI checks the raw files because there a checkout *is* the committed
content. Locally, `--stored-form` asks git itself for the bytes it would store — `git hash-object`
applies whatever clean filter this clone has configured — so a clone with no filter, or with a
different one, is reported honestly rather than flattered. If git cannot produce those bytes at all
(a failing clean filter, an unreadable blob), the check says so instead of falling back to judging
the working copy. Without that split, `make check` would fail every time a kernel was open.

`--github-output` also writes `dirty=true|false` to `$GITHUB_OUTPUT`, which is how the workflow decides
whether the autofix job has anything to do.

Why the workflow has two jobs: **GitHub cannot rewrite what a contributor pushed.** The `check` job is
the guarantee — it works for fork pull requests too and fails the job. Whether a failed job blocks the
merge depends on the repository's branch-protection rules, which live in settings rather than in this
file. The `autofix` job is a
convenience that strips the notebooks and pushes a `chore: strip notebook outputs` commit back to the
pull request branch; it only runs for branches in this repository (a fork's branch is not writable with
`GITHUB_TOKEN`), only on `pull_request`, and never when the actor is the bot, which would loop. Nothing
writes to `main` directly, so a protected branch still needs a human merge.

## `refresh-references.py`

Exports the **Thesis_BJY** Zotero group (id `6767052`) into `docs/literature/references.bib`. Needs
Zotero running with its local API enabled (`Settings → Advanced`), and Better BibTeX installed,
because BBT supplies both the citation keys and the BibTeX rendering.

```bash
uv run python scripts/refresh-references.py
ZOTERO_GROUP_ID=1234567 uv run python scripts/refresh-references.py   # another library
```

Behaviour worth knowing before editing it:

- Entries are grouped by Zotero **collection**, in folder-path order, then by first author and year.
  Items filed in several collections appear once, under the first.
- Export is **one item per request**. The local API silently caps `?format=bibtex` at 50 items and
  ignores `?itemKey=`, so any batched version produces a partial bibliography that looks complete.
- It writes to a temporary file and moves it into place, and refuses to finish on a failed or empty
  export — a truncated `.bib` is only discovered months later. An individual item that yields no
  BibTeX (no citation key, an unsupported type) is reported and skipped; the rest still replace the
  file, so read the report, not just the exit code.
- The output is generated; never hand-edit it. Fix the Zotero item instead and rerun.

## Conventions for new scripts here

- Print progress and errors to **stderr**, machine-readable results to **stdout**.
- Fail loudly with a non-zero exit and a message naming the fix; never leave an artifact half-written.
- Resolve paths from the repository root (`git rev-parse --show-toplevel`), not from the caller's
  working directory — these scripts get run from all over.
- Handle both interpreter layouts (`.venv/bin/python` and `.venv/Scripts/python.exe`) instead of
  branching on the platform.
- Do not add dependencies. If a script needs one, it belongs in the `dev` group of `pyproject.toml`
  and should say so in its docstring.
