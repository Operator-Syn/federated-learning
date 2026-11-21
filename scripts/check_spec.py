#!/usr/bin/env python3
"""Audit the built technical specification against the failures that slipped through review.

Every check here exists because a human had to catch that defect by eye:
  * a notation table missing symbols that the equations use (`r*`, `T*`, `R_p`)
  * a heading stranded at the foot of a page with its text overleaf
  * repository paths (`docs/spec/glossary.yml`) leaking into a document handed out alone
  * a section drifting onto a page of its own with almost nothing on it
  * overfull lines pushing text past the margin

The point is not to replace reading. It is to stop shipping defects that a machine can see, so
that human attention goes to argument and wording instead.

    uv run python scripts/check_spec.py            # builds, then audits
    uv run python scripts/check_spec.py --no-build # audit the existing PDF

Exit 1 when a hard check fails; 0 otherwise. Warnings are printed but do not fail the run.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SPEC_DIR = REPO_ROOT / "docs" / "spec"
MAIN_TEX = SPEC_DIR / "technical-spec.tex"
PDF = SPEC_DIR / "technical-spec.pdf"
LOG = SPEC_DIR / "technical-spec.log"
SECTIONS = sorted((SPEC_DIR / "sections").glob("*.tex"))

# Paths and internal jargon that make no sense to a reader holding only the PDF.
STANDALONE_FORBIDDEN = [
    "glossary.yml", "docs/spec", "scripts/", "plug-in", "harness", "repository",
    "the code", "build fails",
]


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    """Run a command and return the completed process without raising on failure."""
    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)


def extract(cmd: list[str]) -> str:
    """Run an extraction command and return its stdout, failing loudly on any error.

    A corrupt or unreadable PDF must not look like a PDF with no content. `pdftotext` exits
    non-zero and prints nothing in that case, and every check downstream would then compare
    against empty text and report success: the audit would pass precisely when it cannot see
    the document it is auditing.
    """
    result = run(cmd)
    if result.returncode != 0 or not result.stdout.strip():
        command = " ".join(cmd)
        print(f"error: extraction failed (exit {result.returncode}): {command}", file=sys.stderr)
        if result.stderr.strip():
            print(result.stderr.strip()[:800], file=sys.stderr)
        raise SystemExit(2)
    return result.stdout


def build() -> bool:
    """Build the PDF with latexmk from the specification directory."""
    result = run(["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", MAIN_TEX.name],
                 cwd=SPEC_DIR)
    if result.returncode != 0:
        print("error: the document does not build", file=sys.stderr)
        print(result.stdout[-2000:], file=sys.stderr)
        return False
    return True


def page_count() -> int:
    """Return the PDF's page count, failing loudly when the PDF cannot be read."""
    out = extract(["pdfinfo", str(PDF)])
    match = re.search(r"Pages:\s+(\d+)", out)
    if not match:
        print("error: pdfinfo gave no page count; the PDF is unreadable", file=sys.stderr)
        raise SystemExit(2)
    return int(match.group(1))


def page_lines(number: int) -> list[str]:
    """Return the non-empty text lines of one PDF page."""
    out = extract(["pdftotext", "-f", str(number), "-l", str(number), str(PDF), "-"])
    return [line.strip() for line in out.splitlines() if line.strip()]


def section_titles() -> list[str]:
    """Return the top-level section titles from the sources, in document order."""
    titles: list[str] = []
    for path in SECTIONS:
        for line in path.read_text(encoding="utf-8").splitlines():
            match = re.match(r"\s*\\section\{([^}]*)\}", line)
            if match:
                titles.append(match.group(1).strip())
    return titles


def section_pages(pages: int) -> dict[int, int]:
    """Map each top-level section number to the page it opens on.

    Titles come from the sources rather than from a numeric pattern. Table cells start with
    numbers too — "16 GB", "512 kbps", "600 VA" — and any pattern loose enough to accept
    "10 Open decisions" also accepts those, which invents sections. Matching the known title
    after the number cannot.
    """
    titles = section_titles()
    found: dict[int, int] = {}
    for page in range(1, pages + 1):
        lines = page_lines(page)
        if not lines or lines[0].startswith("Contents"):
            continue
        for line in lines:
            for number, title in enumerate(titles, start=1):
                if number not in found and line.startswith(f"{number} {title}"):
                    found[number] = page
    return found


def note_section_fill(start: dict[int, int], pages: int) -> list[str]:
    """Report how full each section's final page is, without judgement.

    Page fill is a preference, not a rule: a section may end three lines down a page and stay
    that way because the author prefers the break there. The tool's job is to make the number
    visible so the decision can be made by eye, not to decide it.
    """
    notes: list[str] = []
    if not start:
        return ["no section headings found in the PDF — is it being built?"]

    order = sorted(start)
    for index, number in enumerate(order):
        first = start[number]
        last = start[order[index + 1]] - 1 if index + 1 < len(order) else pages
        if last > first:
            fill = last_line_position(last)
            notes.append(f"section {number} ends on page {last}, {fill:.0f}% of the text block")
    return notes


def last_line_position(page: int) -> float:
    """Return how far down the text block the last body line sits, as a percentage.

    Words below the text block are the footer (page number) and words above it are the running
    header; counting either would report a nearly empty page as full.
    """
    bbox = extract(["pdftotext", "-f", str(page), "-l", str(page), "-bbox", str(PDF), "-"])
    bottoms = []
    for match in re.finditer(r'xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)"',
                             bbox):
        x_min, y_min, _x_max, y_max = (float(value) for value in match.groups())
        if 60 < x_min < 760 and y_max < 768:  # inside the text block
            bottoms.append(y_max)
    if not bottoms:
        return 0.0
    return min(max(bottoms) / 768 * 100, 100)


def headings() -> list[str]:
    """Return the text of every section and subsection heading in the source, in order."""
    titles: list[str] = []
    for path in SECTIONS:
        for line in path.read_text(encoding="utf-8").splitlines():
            match = re.match(r"\s*\\(?:sub)?section\{([^}]*)\}", line)
            if match:
                titles.append(match.group(1).strip())
    return titles


def note_orphan_headings(titles: list[str], pages: int) -> list[str]:
    """Report a heading that is the last thing on its page, without failing the audit.

    Also a matter of eye: some authors accept a heading at the foot and hate an orphaned line,
    others the reverse. Reported, not enforced.
    """
    notes: list[str] = []
    for page in range(1, pages + 1):
        lines = page_lines(page)
        body = lines[1:-1] if len(lines) > 2 else []
        if not body:
            continue
        tail = body[-1]
        # Headings are extracted with their section number in front ("6.2 Round duration"),
        # so compare against the title with any leading number stripped.
        tail_text = re.sub(r"^\d+(?:\.\d+)*\s+", "", tail)
        for title in titles:
            if tail_text.startswith(title) and len(tail_text) < len(title) + 30:
                notes.append(f"heading {title!r} is the last line of page {page}")
    return notes


def _normalise(token: str) -> str:
    """Reduce a LaTeX symbol to comparable letters: Q_r and $Q_{r}$ both become 'qr'."""
    return re.sub(r"[^a-z0-9*]", "", token.lower())


def defined_symbols() -> list[str]:
    """Return the symbol each display equation defines, taken from its left-hand side.

    Checking left-hand sides rather than every token is deliberate. An equation defines one
    symbol; that is the symbol a reader has to look up, and the one that went missing from the
    notation table in review. Scanning the whole body instead catches bound indices and
    function names, which produces noise and, worse, teaches people to ignore the check.
    """
    used: list[str] = []
    for path in SECTIONS:
        text = path.read_text(encoding="utf-8")
        for body in re.findall(r"\\begin\{equation\}(.*?)\\end\{equation\}", text, re.S):
            stripped = body.split("=", 1)[0].strip()
            match = re.search(r"([A-Za-z])(?:_\{?([^}$^\\\s=]+)\}?)?(?:\^\{?([^}$\\\s=]+)\}?)?\s*$",
                              stripped)
            if not match:
                continue
            # A letter that ends a LaTeX command is not a symbol. `\alpha = 1` would otherwise
            # be read as an equation defining `a`, because the regex takes the last letter.
            # Walk back over the alphabetic run: only a backslash before the whole run marks it
            # as a command rather than a symbol.
            run_start = match.start(1)
            while run_start > 0 and stripped[run_start - 1].isalpha():
                run_start -= 1
            if run_start > 0 and stripped[run_start - 1] == "\\":
                continue
            base, sub, sup = match.group(1), match.group(2) or "", match.group(3) or ""
            used.append(_normalise(base + sub + sup))
    return list(dict.fromkeys(used))


def notation_symbols() -> set[str]:
    """Return the set of symbols the section-6 notation table defines, taken from column one.

    Cells are compared exactly rather than by substring: `r*` is a substring of the `t_{r*}`
    inside another row's meaning, so substring matching would report a symbol as defined when
    its own row is missing. That is precisely the defect this check exists to catch.
    """
    path = SPEC_DIR / "sections" / "06-metrics.tex"
    if not path.is_file():
        return set()
    text = path.read_text(encoding="utf-8")
    match = re.search(r"\\subsection\{Notation\}(.*?)\\subsection", text, re.S)
    if not match:
        return set()

    symbols: set[str] = set()
    for first_cell in re.findall(r"^\s*(.*?)\s*&", match.group(1), re.M):
        # Rows open with \rowcolor{...}; left in, it turns "$d_r$" into "rowcolorrowshadedr"
        # and every zebra row stops matching its own symbol.
        cleaned = re.sub(r"\\rowcolor\{[^}]*\}", "", first_cell)
        cleaned = re.sub(r"\\(?:textbf|texttt|label|text|mathrm)", "", cleaned)
        token = _normalise(cleaned)
        if token and token != "symbol":
            symbols.add(token)
    return symbols


def check_notation() -> list[str]:
    """Flag symbols an equation defines that the notation table never defines."""
    table = notation_symbols()
    if not table:
        return ["section 6 has no notation table"]
    return [
        f"equation defines {symbol!r}, which the notation table does not"
        for symbol in defined_symbols()
        if symbol not in table
    ]


def check_standalone() -> list[str]:
    """Flag text that assumes the reader has the repository."""
    out = extract(["pdftotext", str(PDF), "-"]).lower()
    return [f"the PDF refers to {phrase!r}, which a reader of the printed document cannot use"
            for phrase in STANDALONE_FORBIDDEN if phrase in out]


def note_overfull() -> list[str]:
    """Report overfull lines and how far they run past the margin, without failing.

    A few points of overhang is invisible in print; forty is a line through the margin. The
    amount is what makes it a judgement, so the amount is what gets reported.
    """
    if not LOG.is_file():
        return []
    matches = re.findall(r"Overfull \\hbox \(([\d.]+)pt too wide\)", LOG.read_text(errors="ignore"))
    if not matches:
        return []
    worst = max(float(value) for value in matches)
    return [f"{len(matches)} overfull line(s), worst {worst:.1f}pt past the margin"]


def main(argv: list[str] | None = None) -> int:
    """Run every check and print a report."""
    parser = argparse.ArgumentParser(description="Audit the built specification.")
    parser.add_argument("--no-build", action="store_true", help="audit the existing PDF")
    args = parser.parse_args(argv)

    if not args.no_build and not build():
        return 1
    if not PDF.is_file():
        print(f"error: {PDF} does not exist", file=sys.stderr)
        return 1

    pages = page_count()
    start = section_pages(pages)
    titles = headings()

    hard: list[str] = []
    hard += check_notation()
    hard += check_standalone()

    notes: list[str] = []
    notes += note_section_fill(start, pages)
    notes += note_orphan_headings(titles, pages)
    notes += note_overfull()

    print(f"spec audit: {pages} pages, {len(start)} sections, {len(titles)} headings")
    if start:
        order = sorted(start)
        spans = []
        for index, number in enumerate(order):
            end = start[order[index + 1]] - 1 if index + 1 < len(order) else pages
            spans.append(f"s{number}:{end - start[number] + 1}p")
        print("  spans: " + ", ".join(spans))

    for problem in hard:
        print(f"  FAIL {problem}")
    for note in notes:
        print(f"  note {note}")

    if hard:
        return 1
    if notes:
        print("  layout notes are for your eye: they never fail this audit")
    print("  content checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
