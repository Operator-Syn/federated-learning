#!/usr/bin/env python3
"""Check that the specification and the implementation agree on names.

The glossary is the contract between three things that drift apart first: the document's
prose, the code's identifiers, and whichever name the review of related literature decides
to use. This script is the mechanical half of that contract.

What it verifies:

1. ``glossary.yml`` parses and carries the required sections with unique ids.
2. Entity ids are kebab/snake identifiers, names are non-empty, and ``core`` is a boolean.
3. There are exactly four policy families, one of which is marked as the baseline.
4. If the implementation exists, every policy id in the glossary appears in
   ``src/fl_thesis/federation/policies.py`` and nothing extra appears there.

Exit status 0 when everything agrees, 1 otherwise. Standard library plus PyYAML, both
already available in the project environment.

    uv run python scripts/check_glossary.py
    uv run python scripts/check_glossary.py --glossary path/to/glossary.yml
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_GLOSSARY = REPO_ROOT / "docs" / "spec" / "glossary.yml"
POLICY_MODULE = REPO_ROOT / "src" / "fl_thesis" / "federation" / "policies.py"

IDENTIFIER = re.compile(r"^[a-z][a-z0-9_]*$")
REQUIRED_ENTITY_TIERS = ("domain", "system", "governance")
REQUIRED_SECTIONS = ("entities", "policies", "metrics", "parameters", "open_decisions")
EXPECTED_POLICIES = 4


def load(path: Path) -> dict:
    """Parse the glossary.

    Args:
        path: YAML file to read.

    Returns:
        The parsed mapping.

    Raises:
        SystemExit: when the file is missing or unparsable.
    """
    import yaml

    if not path.is_file():
        raise SystemExit(f"error: glossary not found at {path}")
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise SystemExit(f"error: glossary does not parse: {exc}") from exc


def check_structure(glossary: dict, problems: list[str]) -> None:
    """Verify required sections, identifiers and flags."""
    for section in REQUIRED_SECTIONS:
        if section not in glossary:
            problems.append(f"missing section: {section}")
    if problems:
        return

    for tier in REQUIRED_ENTITY_TIERS:
        entries = glossary["entities"].get(tier)
        if not entries:
            problems.append(f"entities.{tier} is missing or empty")
            continue
        for entry in entries:
            for field in ("id", "name", "core"):
                if field not in entry:
                    problems.append(f"entities.{tier}: {entry.get('id', '?')} has no {field}")
            if not IDENTIFIER.match(str(entry.get("id", ""))):
                problems.append(
                    f"entities.{tier}: id {entry.get('id')!r} is not a snake_case identifier"
                )
            if not isinstance(entry.get("core"), bool):
                problems.append(f"entities.{tier}: {entry.get('id')} core must be a boolean")

    seen: set[str] = set()
    for tier in REQUIRED_ENTITY_TIERS:
        for entry in glossary["entities"].get(tier, []):
            identifier = entry.get("id")
            if identifier in seen:
                problems.append(f"duplicate id across tiers: {identifier}")
            seen.add(identifier)


def check_policies(glossary: dict, problems: list[str]) -> None:
    """Verify the policy family set, including the deliberate baseline."""
    policies = glossary.get("policies") or []
    if len(policies) != EXPECTED_POLICIES:
        problems.append(
            f"expected {EXPECTED_POLICIES} policy families, found {len(policies)}; "
            "add or remove one in both the document and the glossary"
        )
    baselines = [entry for entry in policies if entry.get("baseline")]
    if len(baselines) != 1:
        problems.append(f"expected exactly one baseline policy, found {len(baselines)}")
    for entry in policies:
        if not IDENTIFIER.match(str(entry.get("id", ""))):
            problems.append(f"policy id {entry.get('id')!r} is not a snake_case identifier")
        if not isinstance(entry.get("baseline"), bool):
            problems.append(f"policy {entry.get('id')}: baseline must be a boolean")


def _runtime_registry(path: Path) -> set[str] | None:
    """Execute the module and return the registry keys it actually holds.

    Reading the literal dict is not enough: `dict.fromkeys`, a comprehension, or a key added
    after the literal all register policies that a static read cannot see. The registry that
    runs is the one that matters, so it is read after execution.
    """
    namespace: dict[str, object] = {"__name__": "_policy_registry_probe", "__file__": str(path)}
    try:
        exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), namespace)
    except Exception as error:
        # A module that raises has not registered what it would have registered had it run to
        # the end, so its literal dictionary is not a safe substitute: a key added before the
        # failure would be silently dropped and the drift check would pass. Report the failure
        # instead and let the caller treat it as unreadable.
        raise RuntimeError(f"{type(error).__name__}: {error}") from error
    registry = namespace.get("POLICIES")
    if isinstance(registry, dict):
        return {str(key) for key in registry}
    return None


def implemented_policies(path: Path) -> set[str] | None:
    """Read the policy registry keys from the implementation, if it exists.

    Executed, for the reason given in `_runtime_registry`. There is deliberately no static
    fallback: a literal dictionary that happens to parse is not the registry, and treating it
    as one made the check pass precisely when the module could not be trusted.

    Args:
        path: the policies module.

    Returns:
        The set of registry keys, or ``None`` when the module is absent or holds no registry.

    Raises:
        RuntimeError: the module exists but raised while being executed.
    """
    if not path.is_file():
        return None
    runtime = _runtime_registry(path)
    if runtime is not None:
        return runtime
    return None


def check_drift(glossary: dict, problems: list[str]) -> str:
    """Compare the glossary against the implementation when the latter exists."""
    if not POLICY_MODULE.is_file():
        return "skipped: no implementation yet (src/fl_thesis/federation/policies.py absent)"

    try:
        registered = implemented_policies(POLICY_MODULE)
    except RuntimeError as error:
        problems.append(f"the policy registry exists but could not be executed: {error}")
        return "failed: registry unreadable"
    if registered is None:
        # The file is there but holds no registry this check can see. That is not the same as
        # having nothing to compare: report it, because a silent pass here is a green light on
        # code nobody checked.
        problems.append("the policy registry exists but holds no POLICIES dict")
        return "failed: no registry found"

    documented = {entry["id"] for entry in glossary["policies"]}
    missing = documented - registered
    extra = registered - documented
    if missing:
        problems.append(f"documented but not implemented: {sorted(missing)}")
    if extra:
        problems.append(f"implemented but not documented: {sorted(extra)}")
    return f"compared {len(documented)} documented families with {len(registered)} registered"


def main(argv: list[str] | None = None) -> int:
    """Run the checks and report the outcome."""
    parser = argparse.ArgumentParser(
        description="Check that the specification and the implementation agree on names."
    )
    parser.add_argument("--glossary", type=Path, default=DEFAULT_GLOSSARY)
    args = parser.parse_args(argv)

    glossary = load(args.glossary)
    problems: list[str] = []
    check_structure(glossary, problems)
    if not problems:
        check_policies(glossary, problems)
    drift = check_drift(glossary, problems) if not problems else "not attempted"

    if problems:
        print("glossary check failed:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1

    counts = {tier: len(glossary["entities"][tier]) for tier in REQUIRED_ENTITY_TIERS}
    print(
        "glossary ok: "
        + ", ".join(f"{tier} entities {count}" for tier, count in counts.items())
        + f", policy families {len(glossary['policies'])}"
    )
    print(f"  drift check: {drift}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
