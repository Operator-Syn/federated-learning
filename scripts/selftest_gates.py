"""Self-tests for the repository's gates.

Every gate here exists to reject something. A gate that cannot reject is worse than no gate: it
turns "I could not check this" into a green light, which is how this repository ended up passing a
corrupt PDF and a notebook git would have committed with its outputs.

The only proof that a gate still bites is a fixture it must refuse. These tests feed each gate the
input it is supposed to fail on and assert that it fails. They run in milliseconds, touch nothing
outside a temporary directory, and are part of `make check`.

Run directly:

    uv run python scripts/selftest_gates.py
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

import check_glossary  # noqa: E402  (must follow the sys.path change)
import check_notebook_outputs  # noqa: E402
import check_spec  # noqa: E402

CHECKS: list[tuple[str, Callable[[], None]]] = []


def register(name: str) -> Callable[[Callable[[], None]], Callable[[], None]]:
    """Register a test function under a readable name."""

    def wrapper(function: Callable[[], None]) -> Callable[[], None]:
        CHECKS.append((name, function))
        return function

    return wrapper


def expect_exit(function, *args, **kwargs) -> bool:
    """Return True when the call raises SystemExit; the gate refusing is the point."""
    try:
        function(*args, **kwargs)
    except SystemExit:
        return True
    return False


@register("spec: extraction failure is loud, not empty")
def spec_extraction_failure() -> None:
    """A command that exits non-zero must raise, never return ''."""
    assert expect_exit(check_spec.extract, ["false"]), "non-zero exit was treated as empty output"
    assert expect_exit(check_spec.extract, ["true"]), "empty output was treated as a clean read"


@register("spec: a LaTeX command's last letter is not a symbol")
def spec_command_not_symbol() -> None:
    """`\\alpha = 1` once made the audit demand a notation row for `a`."""
    original = check_spec.SECTIONS
    with tempfile.TemporaryDirectory() as directory:
        source = Path(directory) / "fixture.tex"
        source.write_text(
            "\\begin{equation}\n\\alpha = 1\n\\end{equation}\n"
            "\\begin{equation}\nQ_r = \\frac{1}{n}\n\\end{equation}\n",
            encoding="utf-8",
        )
        try:
            check_spec.SECTIONS = [source]
            found = check_spec.defined_symbols()
        finally:
            check_spec.SECTIONS = original
    assert found == ["qr"], f"expected only 'qr', got {found}"


@register("spec: a numbered heading at the page foot is reported")
def spec_numbered_orphan() -> None:
    """Headings extract with their section number in front; the check must strip it."""
    original_lines, original_headings = check_spec.page_lines, check_spec.headings

    def fake_page_lines(_page: int) -> list[str]:
        return ["Technical Specification", "6.2 Round duration", "12"]

    def fake_headings() -> list[str]:
        return ["Round duration"]

    try:
        check_spec.page_lines = fake_page_lines
        check_spec.headings = fake_headings
        notes = check_spec.note_orphan_headings(["Round duration"], 1)
    finally:
        check_spec.page_lines, check_spec.headings = original_lines, original_headings
    assert notes, "a heading stranded at the foot of a page was not reported"


@register("spec: every extraction call site fails loudly when its command fails")
def spec_call_sites_fail_loudly() -> None:
    """Testing `extract` alone is not enough — a call site can bypass it.

    Each of these functions reads the PDF through `extract`. If one of them is ever rewritten to
    use `run(...).stdout` again, a failing command yields '' and the check silently passes, which
    is the defect this whole file exists to prevent. So the call sites are tested, not the helper.
    """
    original_run = check_spec.run

    def failing(cmd, **kwargs):
        return subprocess.CompletedProcess(cmd, 23, "", "boom")

    try:
        check_spec.run = failing
        for name, call in (
            ("page_count", check_spec.page_count),
            ("page_lines", lambda: check_spec.page_lines(1)),
            ("last_line_position", lambda: check_spec.last_line_position(1)),
            ("check_standalone", check_spec.check_standalone),
        ):
            assert expect_exit(call), f"{name} accepted a failed extraction"
    finally:
        check_spec.run = original_run


@register("spec: no extraction bypasses extract()")
def spec_no_raw_stdout() -> None:
    """A call site that reads `run(...).stdout` reintroduces the silent-empty bug by hand.

    `page_count` still raised when regressed because it carries its own guard; `check_standalone`
    did not, and quietly analysed an empty string. A guard per function is a promise to remember;
    this test makes the bypass impossible to add without failing the build.
    """
    source = Path(check_spec.__file__).read_text(encoding="utf-8")
    offenders = [
        line.strip()
        for line in source.splitlines()
        if ".stdout" in line and "result.stdout" not in line
    ]
    assert not offenders, f"raw stdout used outside extract(): {offenders}"


@register("glossary: a registry built at runtime is read")
def glossary_dynamic_registry() -> None:
    """`dict.fromkeys` is a registry; a static literal read cannot see it."""
    with tempfile.TemporaryDirectory() as directory:
        module = Path(directory) / "policies.py"
        module.write_text(
            'POLICIES = dict.fromkeys(["a", "b", "c", "d"])\nPOLICIES["e"] = None\n',
            encoding="utf-8",
        )
        keys = check_glossary.implemented_policies(module)
    assert keys == {"a", "b", "c", "d", "e"}, f"runtime registry misread as {keys}"


@register("glossary: a module that raises is reported, not guessed")
def glossary_raising_module() -> None:
    """Falling back to the source text after a failure once hid a registered key."""
    with tempfile.TemporaryDirectory() as directory:
        module = Path(directory) / "policies.py"
        module.write_text('POLICIES = {"a": None}\nraise RuntimeError("boom")\n', encoding="utf-8")
        try:
            check_glossary.implemented_policies(module)
        except RuntimeError as error:
            assert "boom" in str(error), f"the reason was lost: {error}"
            return
    raise AssertionError("a module that raised was accepted as a readable registry")


@register("glossary: a module with no registry is reported as absent")
def glossary_no_registry() -> None:
    """A file with no POLICIES dict is not the same as a matching registry."""
    with tempfile.TemporaryDirectory() as directory:
        module = Path(directory) / "policies.py"
        module.write_text("X = 1\n", encoding="utf-8")
        assert check_glossary.implemented_policies(module) is None


def run_main(
    entry_args: list[str] | None = None,
    stubs: dict[str, Callable[..., object]] | None = None,
) -> tuple[int, str]:
    """Run `main()` with every external dependency stubbed, returning (exit code, printed text).

    A stub that returns nothing cannot detect a wiring change: moving a check between the hard
    and note lists is invisible when that check produces no findings either way. So each test
    below overrides exactly one source with a sentinel and leaves the rest empty.

    `entry_args` defaults to `--no-build`; pass `[]` to exercise the build branch.
    """
    defaults: dict[str, Callable[..., object]] = {
        "check_notation": lambda: [],
        "check_standalone": lambda: [],
        "page_count": lambda: 3,
        "section_pages": lambda _pages: {1: 1},
        "note_section_fill": lambda *_args: [],
        "note_orphan_headings": lambda *_args: [],
        "note_overfull": lambda *_args: [],
        "headings": lambda: [],
        "build": lambda: True,
    }
    if stubs:
        defaults.update(stubs)
    originals = {name: getattr(check_spec, name) for name in defaults}
    printed = io.StringIO()
    try:
        for name, stub in defaults.items():
            setattr(check_spec, name, stub)
        with contextlib.redirect_stdout(printed):
            code = check_spec.main(["--no-build"] if entry_args is None else entry_args)
    finally:
        for name, original in originals.items():
            setattr(check_spec, name, original)
    return code, printed.getvalue()


def sentinel_source(text: str) -> Callable[..., list[str]]:
    """Return a stub that ignores its arguments and reports exactly `text`.

    Written as a factory rather than `lambda s=sentinel, *_: [s]`: a default parameter binds the
    first positional argument, so a stub for a two-argument function silently returns its own
    input instead of the sentinel and the assertion passes for the wrong reason.
    """

    def stub(*_args: object, **_kwargs: object) -> list[str]:
        return [text]

    return stub


def valid_glossary() -> dict:
    """Return the smallest glossary that passes `check_structure` and `check_policies`.

    Built in code rather than read from `docs/spec/glossary.yml`: a test that depends on the real
    document starts failing when the document grows, which trains people to edit the test.
    """
    entry = {"id": "thing", "name": "Thing", "core": True}
    tiers = {
        tier: [dict(entry, id=f"{tier}_thing")]
        for tier in ("domain", "system", "governance")
    }
    return {
        "entities": tiers,
        "policies": [
            {"id": "adaptive_sampling", "name": "Adaptive", "baseline": False},
            {"id": "resource_aware", "name": "Resource", "baseline": False},
            {"id": "fair_sampling", "name": "Fair", "baseline": False},
            {"id": "baseline_uniform", "name": "Uniform", "baseline": True},
        ],
        "metrics": {},
        "parameters": {},
        "open_decisions": [],
    }


@register("glossary: a valid glossary passes both checks")
def glossary_valid_passes() -> None:
    """The control: without this, every failure test below could pass for the wrong reason."""
    problems: list[str] = []
    sample = valid_glossary()
    check_glossary.check_structure(sample, problems)
    check_glossary.check_policies(sample, problems)
    assert not problems, problems


@register("glossary: structure rejects a missing section, empty tier, duplicate id")
def glossary_structure_rejects() -> None:
    """Three ways a glossary can be wrong while every entity still looks well formed."""
    problems: list[str] = []
    check_glossary.check_structure({"policies": []}, problems)
    assert any("missing section" in problem for problem in problems), problems

    sample = valid_glossary()
    sample["entities"]["governance"] = []
    problems = []
    check_glossary.check_structure(sample, problems)
    assert any("missing or empty" in problem for problem in problems), problems

    sample = valid_glossary()
    sample["entities"]["system"] = list(sample["entities"]["domain"])
    problems = []
    check_glossary.check_structure(sample, problems)
    assert any("duplicate id" in problem for problem in problems), problems


@register("glossary: policies reject a wrong count and a missing baseline")
def glossary_policies_reject() -> None:
    """The family count and the single deliberate baseline are both contracts."""
    problems: list[str] = []
    sample = valid_glossary()
    sample["policies"] = sample["policies"][:3]
    check_glossary.check_policies(sample, problems)
    assert any("policy families" in problem for problem in problems), problems

    problems = []
    sample = valid_glossary()
    for entry in sample["policies"]:
        entry["baseline"] = False
    check_glossary.check_policies(sample, problems)
    assert any("baseline" in problem for problem in problems), problems


@register("notebooks: a failed git read yields no stored form")
def notebooks_git_read_failures() -> None:
    """Both git steps must return None on failure: hash-object and cat-file.

    `stored_form` treats None as "cannot determine", so a failure here is a refusal. Returning a
    partial value instead would let the caller judge bytes git never produced.
    """
    path = Path("notebooks/00-workspace-check.ipynb")
    original = check_notebook_outputs.subprocess

    def shim(outcomes: list[tuple[int, bytes, bytes]]) -> object:
        remaining = list(outcomes)

        class Shim:
            CompletedProcess = original.CompletedProcess

            @staticmethod
            def run(*_args, **_kwargs):
                code, out, err = remaining.pop(0)
                return original.CompletedProcess([], code, out, err)

        return Shim()

    try:
        check_notebook_outputs.subprocess = shim([(128, b"", b"boom")])
        assert check_notebook_outputs.git_stored_form(path) is None, "failed hash was accepted"

        check_notebook_outputs.subprocess = shim([(0, b"deadbeef", b""), (1, b"", b"boom")])
        assert check_notebook_outputs.git_stored_form(path) is None, "failed blob was accepted"
    finally:
        check_notebook_outputs.subprocess = original


@register("notebooks: no notebooks is reported, not silently passed")
def notebooks_none_found() -> None:
    """An empty run must say so; silence plus exit 0 reads like a clean repository."""
    original = check_notebook_outputs.tracked_notebooks
    printed = io.StringIO()
    try:
        check_notebook_outputs.tracked_notebooks = lambda: []
        with contextlib.redirect_stdout(printed):
            code = check_notebook_outputs.main([])
    finally:
        check_notebook_outputs.tracked_notebooks = original
    assert code == 0, "an empty run should not fail"
    assert "no notebooks found" in printed.getvalue(), "an empty run was silent"


@register("notebooks: the GitHub output is written only when asked")
def notebooks_github_output() -> None:
    """`--github-output` writes the flag; without the variable it must not crash."""
    with tempfile.TemporaryDirectory() as directory:
        target = Path(directory) / "output"
        original = os.environ.get("GITHUB_OUTPUT")
        os.environ["GITHUB_OUTPUT"] = str(target)
        try:
            check_notebook_outputs.write_github_output(True)
        finally:
            if original is None:
                del os.environ["GITHUB_OUTPUT"]
            else:
                os.environ["GITHUB_OUTPUT"] = original
        assert target.read_text(encoding="utf-8").strip() == "dirty=true", target.read_text()

    original = os.environ.pop("GITHUB_OUTPUT", None)
    try:
        check_notebook_outputs.write_github_output(False)  # must be a no-op, not a crash
    finally:
        if original is not None:
            os.environ["GITHUB_OUTPUT"] = original


@register("spec: two-digit section numbers are recognised")
def spec_two_digit_sections() -> None:
    """A one-digit pattern silently drops section 10 and counts nine sections forever."""
    original_lines, original_titles = check_spec.page_lines, check_spec.section_titles
    titles = [f"Title{n}" for n in range(1, 10)] + ["Open decisions"]

    def fake_page_lines(_page: int) -> list[str]:
        return ["10 Open decisions", "10.1 What is open"]

    try:
        check_spec.page_lines = fake_page_lines
        check_spec.section_titles = lambda: titles
        found = check_spec.section_pages(1)
    finally:
        check_spec.page_lines, check_spec.section_titles = original_lines, original_titles
    assert found == {10: 1}, f"section 10 was not detected: {found}"


@register("spec: table cells are not mistaken for section headings")
def spec_cells_are_not_sections() -> None:
    """`16 GB` starts with a number; a numeric-only match invents sections from cells."""
    original_lines, original_titles = check_spec.page_lines, check_spec.section_titles

    def fake_page_lines(_page: int) -> list[str]:
        return ["Table heading", "16 GB of memory", "512 kbps upload", "600 VA supply"]

    try:
        check_spec.page_lines = fake_page_lines
        check_spec.section_titles = lambda: ["Scope", "Entities"]
        found = check_spec.section_pages(1)
    finally:
        check_spec.page_lines, check_spec.section_titles = original_lines, original_titles
    assert found == {}, f"table cells were read as section openings: {found}"


@register("spec: contents pages are not mistaken for section openings")
def spec_contents_page_skipped() -> None:
    """The contents page prints section titles too; counting them moves every section's opening."""
    original_lines, original_titles = check_spec.page_lines, check_spec.section_titles

    def fake_page_lines(_page: int) -> list[str]:
        return ["Contents", "1 Scope", "2 Entities"]

    try:
        check_spec.page_lines = fake_page_lines
        check_spec.section_titles = lambda: ["Scope", "Entities"]
        found = check_spec.section_pages(1)
    finally:
        check_spec.page_lines, check_spec.section_titles = original_lines, original_titles
    assert found == {}, f"the contents page was parsed as body sections: {found}"


@register("spec: a document with no section headings is reported")
def spec_no_sections_reported() -> None:
    """Silence here would let a document audit as 'no sections, all fine'."""
    notes = check_spec.note_section_fill({}, 3)
    assert notes and "no section headings" in notes[0], notes


@register("glossary: a module with no registry fails the drift check")
def glossary_drift_no_registry() -> None:
    """A file with no POLICIES dict is an unreadable registry, not a matching one."""
    original = check_glossary.POLICY_MODULE
    with tempfile.TemporaryDirectory() as directory:
        module = Path(directory) / "policies.py"
        module.write_text("X = 1\n", encoding="utf-8")
        problems: list[str] = []
        try:
            check_glossary.POLICY_MODULE = module
            summary = check_glossary.check_drift(valid_glossary(), problems)
        finally:
            check_glossary.POLICY_MODULE = original
    assert problems, f"a registry-less module was accepted ({summary})"
    assert "no POLICIES" in problems[0], problems


@register("spec: a failed build stops the audit")
def spec_build_failure_stops() -> None:
    """If the document does not compile, nothing after it may report success."""
    code, printed = run_main(entry_args=[], stubs={"build": lambda: False})
    assert code == 1, "a failed build was followed by a passing audit"


@register("spec: no notation table is a failure, not a skip")
def spec_missing_notation_table() -> None:
    """An empty notation table must be reported, not silently treated as 'nothing to check'."""
    original = check_spec.notation_symbols
    try:
        check_spec.notation_symbols = lambda: set()
        findings = check_spec.check_notation()
    finally:
        check_spec.notation_symbols = original
    assert findings, "a document with no notation table passed the notation check"
    assert "no notation table" in findings[0], f"wrong reason reported: {findings[0]}"


@register("spec: missing build log is not a finding")
def spec_missing_log_is_silent() -> None:
    """No log means no overfull data; inventing a finding would fail every clean checkout."""
    original = check_spec.LOG
    try:
        check_spec.LOG = Path("/nonexistent/build.log")
        assert check_spec.note_overfull() == []
    finally:
        check_spec.LOG = original


@register("spec: every hard finding fails the audit")
def spec_every_hard_finding_fails() -> None:
    """Each thing that can put a finding into the hard list must reach the exit code.

    Two sources feed it today. Testing one of them leaves the other free to be deleted from
    `main()` without a single test noticing.
    """
    for name in ("check_notation", "check_standalone"):
        sentinel = f"{name} sentinel"
        code, printed = run_main(stubs={name: sentinel_source(sentinel)})
        assert code == 1, f"{name} finding did not fail the audit"
        assert sentinel in printed, f"{name} finding was not printed"


@register("spec: every note is printed and never fails")
def spec_every_note_printed() -> None:
    """Each note source must reach the report and must not touch the exit code.

    This is where a stub returning [] hides a defect: promoting a note into the hard list looks
    harmless until the note actually has something to say.
    """
    for name in ("note_section_fill", "note_orphan_headings", "note_overfull"):
        sentinel = f"{name} sentinel"
        code, printed = run_main(stubs={name: sentinel_source(sentinel)})
        assert code == 0, f"{name} failed the audit instead of being reported as a note"
        assert sentinel in printed, f"{name} was dropped instead of printed"


@register("glossary: drift reports a documented policy that is not implemented")
def glossary_drift_reports_missing() -> None:
    """The other half of drift: the glossary promises a family the code never registers."""
    original = check_glossary.POLICY_MODULE
    with tempfile.TemporaryDirectory() as directory:
        module = Path(directory) / "policies.py"
        module.write_text('POLICIES = {"a": None}\n', encoding="utf-8")
        problems: list[str] = []
        try:
            check_glossary.POLICY_MODULE = module
            summary = check_glossary.check_drift({"policies": [{"id": "a"}, {"id": "b"}]}, problems)
        finally:
            check_glossary.POLICY_MODULE = original
    assert problems, f"a documented policy missing from the code was accepted ({summary})"


@register("glossary: drift reports a registered policy that is undocumented")
def glossary_drift_reports_extra() -> None:
    """Reading a registry correctly is not the same as acting on it.

    The runtime-registry test proves the keys are read. It never noticed when the
    implemented-but-undocumented branch was silenced, which is the half of the drift check that
    catches code the glossary has forgotten.
    """
    original = check_glossary.POLICY_MODULE
    with tempfile.TemporaryDirectory() as directory:
        module = Path(directory) / "policies.py"
        module.write_text('POLICIES = {"a": None, "extra": None}\n', encoding="utf-8")
        problems: list[str] = []
        try:
            check_glossary.POLICY_MODULE = module
            summary = check_glossary.check_drift({"policies": [{"id": "a"}]}, problems)
        finally:
            check_glossary.POLICY_MODULE = original
    assert problems, f"an undocumented registered policy was accepted ({summary})"


@register("notebooks: outputs are reported on their own")
def notebooks_report_outputs() -> None:
    """A cell can carry outputs with no execution count; each finding needs its own fixture.

    The count test uses an output-free cell, so it never reaches the `with_outputs` branch. A
    branch with no fixture is a branch that can be deleted without anyone noticing.
    """
    with tempfile.TemporaryDirectory() as directory:
        notebook = Path(directory) / "outputs.ipynb"
        notebook.write_text(
            json.dumps({
                "cells": [
                    {
                        "cell_type": "code",
                        "source": "x",
                        "outputs": [{"output_type": "stream", "name": "stdout", "text": ["y"]}],
                        "execution_count": None,
                    }
                ]
            }),
            encoding="utf-8",
        )
        problems = check_notebook_outputs.inspect(notebook)
    assert problems, "a notebook with outputs and no counts was reported clean"
    assert any("carry outputs" in problem for problem in problems), problems


@register("notebooks: execution counts are reported on their own")
def notebooks_report_counts() -> None:
    """A cell can carry a count with no outputs; the two findings must not mask each other."""
    with tempfile.TemporaryDirectory() as directory:
        notebook = Path(directory) / "counts.ipynb"
        notebook.write_text(
            json.dumps({
                "cells": [
                    {"cell_type": "code", "source": "x", "outputs": [], "execution_count": 1}
                ]
            }),
            encoding="utf-8",
        )
        problems = check_notebook_outputs.inspect(notebook)
    assert problems, "a notebook with execution counts but no outputs was reported clean"
    assert any("execution count" in problem for problem in problems), problems


@register("notebooks: stored_form never substitutes an answer")
def notebooks_stored_form_never_substitutes() -> None:
    """The contract of `stored_form` is exactly git's bytes, or None.

    The sibling test patches `stored_form` itself, so it proves `inspect` handles None — not that
    `stored_form` returns None. A fallback added inside `stored_form` (read the working copy, run
    the wrapper) would let a dirty notebook pass while that test stayed green. This one patches
    the layer below, so any substitution shows up as a non-None result.
    """
    original = check_notebook_outputs.git_stored_form

    def unavailable(_path: Path) -> None:
        return None

    try:
        check_notebook_outputs.git_stored_form = unavailable
        result = check_notebook_outputs.stored_form(Path("notebooks/00-workspace-check.ipynb"))
    finally:
        check_notebook_outputs.git_stored_form = original
    assert result is None, "stored_form produced an answer when git could not supply the bytes"


@register("notebooks: an unknown stored form is a problem, not a pass")
def notebooks_unknown_stored_form() -> None:
    """When git cannot say what it would store, the gate must refuse to judge the working copy."""
    original = check_notebook_outputs.stored_form

    def unknown(_path: Path) -> None:
        return None

    try:
        check_notebook_outputs.stored_form = unknown
        problems = check_notebook_outputs.inspect(
            Path("notebooks/00-workspace-check.ipynb"), as_stored=True
        )
    finally:
        check_notebook_outputs.stored_form = original
    assert problems, "an undeterminable stored form was reported as clean"
    assert "cannot determine" in problems[0], f"unexpected message: {problems[0]}"


def main() -> int:
    """Run every registered test and report the ones that failed."""
    failures = 0
    for name, test in CHECKS:
        captured = io.StringIO()
        try:
            with contextlib.redirect_stdout(captured), contextlib.redirect_stderr(captured):
                test()
        except AssertionError as error:
            failures += 1
            print(f"FAILED  {name}\n        {error}", file=sys.stderr)
        except Exception as error:  # noqa: BLE001 - a crashing test is a failing test
            failures += 1
            print(f"ERROR   {name}\n        {type(error).__name__}: {error}", file=sys.stderr)
    print(f"{len(CHECKS) - failures} of {len(CHECKS)} gate self-tests passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
