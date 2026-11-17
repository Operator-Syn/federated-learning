# scripts

Repository tooling. Everything here is plain Python and standard library only, so it runs in the
project environment without adding dependencies. Run scripts through `uv` so they see `.venv`:

```bash
uv run python scripts/<name>.py
```

| script | what it does | when you run it |
|---|---|---|
| `setup_notebook_filters.py` | registers the `nbstripout` git filter in this clone | once per clone, after `uv sync` |
| `setup_git_hooks.py` | points `core.hooksPath` at `scripts/git-hooks/` | once per clone, after `uv sync` |
| `git-hooks/pre-commit` | lint gate: ruff errors block, formatting drift warns | automatic, on every `git commit` |
| `nbstripout_safe.py` | the clean-filter/textconv wrapper itself | never by hand — git invokes it |
| `check_notebook_outputs.py` | fails when a committed notebook still holds outputs | CI, and before pushing if you skipped the filter |
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
uv run python scripts/check_notebook_outputs.py                # every tracked *.ipynb
uv run python scripts/check_notebook_outputs.py notebooks/x.ipynb
```

`--github-output` also writes `dirty=true|false` to `$GITHUB_OUTPUT`, which is how the workflow decides
whether the autofix job has anything to do.

Why the workflow has two jobs: **GitHub cannot rewrite what a contributor pushed.** The `check` job is
the guarantee — it works for fork pull requests too and blocks the merge. The `autofix` job is a
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
  export — a truncated `.bib` is only discovered months later.
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
