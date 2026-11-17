#!/usr/bin/env python3
"""Fail when a committed notebook still carries outputs or execution counts.

This is the remote-side backstop for collaborators who never ran
``scripts/setup_notebook_filters.py``: the clean filter strips notebooks on the way into
their commit, but nothing forces them to install it. CI cannot rewrite what they pushed,
so this job's real job is to refuse the change until it is clean — a workflow that
silently rewrote history on their behalf would be worse.

Standard library only, so it runs on a bare runner with no environment setup.

    python scripts/check_notebook_outputs.py                 # every tracked *.ipynb
    python scripts/check_notebook_outputs.py notebooks/a.ipynb
    python scripts/check_notebook_outputs.py --github-output # also set dirty=true|false

Exit status: 0 when every notebook is stored stripped, 1 when any is not (and on an
unparsable notebook, which is a defect of its own).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

OUTPUT_KEY = "dirty"


def tracked_notebooks() -> list[Path]:
    """Return the git-tracked notebooks, or every .ipynb when git is unavailable."""
    try:
        completed = subprocess.run(
            ["git", "ls-files", "*.ipynb"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        completed = None

    if completed is not None and completed.returncode == 0:
        return [Path(line) for line in completed.stdout.splitlines() if line.strip()]
    return sorted(Path.cwd().rglob("*.ipynb"))


def inspect(path: Path) -> list[str]:
    """Return the problems found in one notebook, as human-readable lines."""
    try:
        notebook = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{path}: cannot parse ({exc})"]

    problems = []
    code_cells = 0
    with_outputs = 0
    with_counts = 0
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        code_cells += 1
        if cell.get("outputs"):
            with_outputs += 1
        if cell.get("execution_count") is not None:
            with_counts += 1

    if with_outputs:
        problems.append(f"{path}: {with_outputs} of {code_cells} code cells carry outputs")
    if with_counts:
        problems.append(f"{path}: {with_counts} of {code_cells} code cells carry execution counts")
    return problems


def write_github_output(dirty: bool) -> None:
    """Publish the result to the workflow when running under GitHub Actions."""
    target = os.environ.get("GITHUB_OUTPUT")
    if not target:
        return
    with open(target, "a", encoding="utf-8") as handle:
        handle.write(f"{OUTPUT_KEY}={'true' if dirty else 'false'}\n")


def main(argv: list[str] | None = None) -> int:
    """Check every requested notebook and return the exit status."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="notebooks to check; defaults to every git-tracked *.ipynb",
    )
    parser.add_argument(
        "--github-output",
        action="store_true",
        help="also write dirty=true|false to $GITHUB_OUTPUT",
    )
    args = parser.parse_args(argv)

    notebooks = args.paths if args.paths else tracked_notebooks()
    if not notebooks:
        print("no notebooks found")
        if args.github_output:
            write_github_output(False)
        return 0

    problems: list[str] = []
    for path in notebooks:
        problems.extend(inspect(path))

    if problems:
        print("Notebooks are stored with execution state:", file=sys.stderr)
        for line in problems:
            print(f"  {line}", file=sys.stderr)
        print(
            "\nFix them, then commit again:\n"
            "  uv run python scripts/setup_notebook_filters.py   # once per clone\n"
            "  or strip the files directly: uvx nbstripout <files>",
            file=sys.stderr,
        )
        if args.github_output:
            write_github_output(True)
        return 1

    print(f"{len(notebooks)} notebook(s) checked: all stored stripped")
    if args.github_output:
        write_github_output(False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
