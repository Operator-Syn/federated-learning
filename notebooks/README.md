# Notebooks

Working space for the simulation study. The environment is managed by `uv` from the repository
root, so every notebook runs against the same pinned interpreter and libraries.

Linux, macOS and Windows are all supported: `uv` provisions the interpreter, the setup script is
Python rather than shell, and the git filter names the project interpreter explicitly — on Windows
that is `.venv\Scripts\python.exe`, elsewhere `.venv/bin/python`, and the script detects which exists.

## First run

```bash
uv sync                                   # create .venv from uv.lock
uv run python scripts/setup_notebook_filters.py   # once per clone
uv run python -m ipykernel install --prefix .venv \
  --name fl-thesis --display-name "Python (fl-thesis)"   # kernelspec inside .venv
uv run jupyter lab --notebook-dir=notebooks
```

Pick the **Python (fl-thesis)** kernel. The kernelspec is installed inside `.venv`, not in your
home directory, so it exists only while you are working in this checkout. `uv sync` provides only
ipykernel's own `python3` kernel, so the install line above is what registers `fl-thesis`; rerun it
after recreating `.venv`.

The repository tooling behind these commands — the notebook filter, the lint gate and the Zotero
export — is documented in [`scripts/README.md`](../scripts/README.md).

Notebooks resolve the repository root themselves (walking up to `pyproject.toml`), so `runs/` lands at
the repo root however Jupyter or `nbconvert` was launched.

## Check the environment

`00-workspace-check.ipynb` prints the interpreter path, Python version, host and library versions,
then writes one synthetic figure to `runs/`. If it runs clean, the workspace is wired correctly.

Run it headlessly from the repository root. The commands are identical across platforms; only the way
you set an environment variable differs:

```bash
# Linux / macOS
MPLBACKEND=Agg uv run --frozen jupyter nbconvert --to notebook --execute --stdout \
  notebooks/00-workspace-check.ipynb > /dev/null
```

```powershell
# Windows PowerShell
$env:MPLBACKEND="Agg"; uv run --frozen jupyter nbconvert --to notebook --execute --stdout `
  notebooks/00-workspace-check.ipynb > $null
```

## Git filter (one-time, per clone)

Notebooks are stored stripped: `.gitattributes` routes `*.ipynb` through a clean filter, so outputs
and execution counts are stripped on commit — once the filter is registered in your clone, which is
the next step. Diffs render as readable cells instead of raw JSON.

The attribute rules are committed; the filter *command* cannot be, because git keeps it in
`.git/config`. So after cloning:

```bash
uv sync                                          # provides nbstripout
uv run python scripts/setup_notebook_filters.py  # registers the filter in this clone
```

On Windows run the same command in PowerShell or Git Bash. The script prints the interpreter it
registered, so a wrong one is visible immediately.

Verify with `git check-attr -a -- notebooks/00-workspace-check.ipynb` — it should report
`filter: nbstripout` and `diff: ipynb`. Without the registration git commits unstripped notebooks
without complaining.

CI checks the same thing from the other side: `.github/workflows/notebooks.yml` fails any change that
still contains outputs, and strips-and-pushes a fix to same-repository pull request branches. The local
filter is still the one that matters — it keeps what git stores and the diffs it shows clean; the
workflow only catches what slipped through someone else's clone. A clean filter does not rewrite your
working file, so the notebook on disk keeps its outputs until something strips it.

## Conventions

- **One notebook per question**, numbered in the order you expect to run them (`01-…`, `02-…`).
  Later notebooks may assume the artifacts of earlier ones; say so in a markdown cell.
- **Cells hold configuration and calls, nothing else.** Imports, seeds, paths and knobs go in one
  config cell; everything after it is a call into `src/fl_thesis/`. A cell that computes is a source
  file that escaped — it cannot be imported, tested or diffed.
- **The package is organised by concern, not by convenience.** `workspace/` (paths, run layout),
  `runtime/` (interpreter and library introspection), `data/` (loaders, generators, splits),
  `viz/` (figures, tables). Add a subpackage when a new concern arrives rather than a tenth module to
  the top level, and give each subpackage an `__init__.py` that says what it owns.
- **No `%%writefile`.** Modules under `src/` are ordinary files and the source of truth. Generating
  them from notebook cells inverts that ownership and makes the notebook authoritative, which the
  Git workflow here does not support.
- **Outputs are ephemeral.** `nbstripout` clears every output on the way into Git, so a figure or
  table is only real if code wrote it into `runs/`. Display the saved file, not the live object.
- **Keep committed notebooks output-free.** Clear outputs before committing (`Cell → All Output →
  Clear`), so diffs show code changes rather than execution state.
- **Do not re-run a notebook that is mid-execution** from another process; the file and its outputs
  are not safe to touch while a kernel is writing them.

## Adding a notebook

```bash
uv run jupyter lab --notebook-dir=notebooks   # File → New → Notebook
```

New notebook needs the `fl-thesis` kernel selected; the choice is stored in the notebook's metadata,
so once set it is picked up automatically.
