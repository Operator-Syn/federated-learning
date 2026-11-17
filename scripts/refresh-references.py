#!/usr/bin/env python3
"""Regenerate docs/literature/references.bib from the Thesis_BJY Zotero group.

The Zotero library is the source of truth for references; this file is the
artefact the paper is cited from. Exports are ordered by collection — the same
topic grouping as the docs/ folder tree — so the bibliography reads in the same
shape as the source library instead of in import order.

Requires Zotero desktop running with the local API enabled (Settings → Advanced →
"Allow other applications on this computer to communicate with Zotero") and
Better BibTeX installed, because BBT supplies both the citation keys and the
BibTeX rendering behind ?format=bibtex.

Usage:
    scripts/refresh-references.py

Environment overrides:
    ZOTERO_LOCAL_API   local API base (default http://127.0.0.1:23119/api)
    ZOTERO_GROUP_ID    group library id (default 6767052, the Thesis_BJY group)

Algorithm:
    1. Read the collection tree and compute each collection's full path
       ("federated-learning/clustering"), so sections can be ordered the way a
       reader expects rather than by collection key.
    2. Walk the collections in path order. For each, page through its top-level
       items and record the first bibliographic item seen for every key; an item
       filed in several collections is exported once, under the first one.
    3. Page through the whole library to catch items that sit in no collection,
       and append them as a final section so nothing is silently dropped.
    4. Sort within a section by first author, then year, then title.
    5. Export one item per request. The local API silently caps ?format=bibtex at
       50 items and ignores ?itemKey=, so batching produces a partial file that
       looks complete.
    6. Write to a temporary file beside the target and move it into place; a
       failed request, an empty library, or a short export leaves the existing
       bibliography untouched, because a truncated .bib is only noticed months
       later, in the camera-ready.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

LOCAL_API = os.environ.get("ZOTERO_LOCAL_API", "http://127.0.0.1:23119/api")
GROUP_ID = os.environ.get("ZOTERO_GROUP_ID", "6767052")
PAGE_SIZE = 100
UNFILED = "(unfiled)"

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET = REPO_ROOT / "docs" / "literature" / "references.bib"


def fetch(path: str) -> bytes:
    """GET a local-API path and return the raw body, failing loudly on error."""
    url = f"{LOCAL_API}/groups/{GROUP_ID}/{path}"
    try:
        with urllib.request.urlopen(url, timeout=60) as response:
            return response.read()
    except urllib.error.HTTPError as err:
        raise SystemExit(f"error: {url} returned HTTP {err.code}") from err
    except urllib.error.URLError as err:
        raise SystemExit(
            f"error: cannot reach {url} ({err.reason}); is Zotero running with the local API enabled?"
        ) from err


def fetch_json(path: str):
    return json.loads(fetch(path).decode("utf-8"))


def paginate(path: str):
    """Yield every item from a paginated listing, 100 per page.

    The page size the API actually returns drives the loop, not the number of
    entries in the page body: format=bibtex responses are shorter than the item
    count and would end pagination early.
    """
    start = 0
    while True:
        page = fetch_json(f"{path}{'&' if '?' in path else '?'}limit={PAGE_SIZE}&start={start}")
        if not page:
            return
        yield from page
        if len(page) < PAGE_SIZE:
            return
        start += PAGE_SIZE


def collection_paths() -> dict[str, str]:
    """Map collection key -> slash-joined path of collection names."""
    collections = fetch_json("/collections?limit=100")
    by_key = {c["key"]: c for c in collections}
    paths: dict[str, str] = {}

    def resolve(key: str, seen: frozenset[str] = frozenset()) -> str:
        if key in paths:
            return paths[key]
        if key in seen:  # defensive: a cycle would otherwise recurse forever
            return by_key[key]["data"]["name"]
        parent = by_key[key]["data"].get("parentCollection")
        prefix = resolve(parent, seen | {key}) if parent else ""
        paths[key] = f"{prefix}/{by_key[key]['data']['name']}" if prefix else by_key[key]["data"]["name"]
        return paths[key]

    for key in by_key:
        resolve(key)
    return paths


def is_bibliographic(item: dict) -> bool:
    return item["data"].get("itemType") not in ("attachment", "note")


def sort_key(item: dict) -> tuple[str, str, str]:
    """Author surname, then year, then title — the order a reader scans."""
    creators = item["data"].get("creators") or []
    first = creators[0] if creators else {}
    author = (first.get("lastName") or first.get("name") or "").lower()
    date = item["data"].get("date") or ""
    year = date[:4] if date[:4].isdigit() else ""
    return author, year, (item["data"].get("title") or "").lower()


def ordered_sections() -> list[tuple[str, list[str]]]:
    """Return [(section name, [item keys])] in path order, unfiled last."""
    paths = collection_paths()
    claimed: dict[str, str] = {}
    sections: dict[str, list[str]] = {}

    for key in sorted(paths, key=lambda k: paths[k].lower()):
        items = [i for i in paginate(f"/collections/{key}/items/top?") if is_bibliographic(i)]
        if not items:
            continue
        items.sort(key=sort_key)
        for item in items:
            # first collection wins: an item filed in two places is exported once
            if item["key"] not in claimed:
                claimed[item["key"]] = paths[key]
                sections.setdefault(paths[key], []).append(item["key"])

    leftovers = [i for i in paginate("/items/top?") if is_bibliographic(i) and i["key"] not in claimed]
    if leftovers:
        leftovers.sort(key=sort_key)
        sections[UNFILED] = [i["key"] for i in leftovers]

    return [(name, sections[name]) for name in sorted(sections, key=lambda n: (n == UNFILED, n.lower()))]


def bibtex_for(key: str) -> str:
    """Export a single item; empty output means BBT could not render it."""
    return fetch(f"/items/{key}?format=bibtex").decode("utf-8").strip()


def main() -> int:
    sections = ordered_sections()
    total = sum(len(keys) for _, keys in sections)
    if total == 0:
        raise SystemExit(f"error: group {GROUP_ID} has no bibliographic items; leaving {TARGET.name} untouched")

    lines: list[str] = []
    exported = 0
    missing: list[str] = []

    for name, keys in sections:
        rendered = []
        for key in keys:
            entry = bibtex_for(key)
            if "@" not in entry:
                missing.append(key)
                continue
            rendered.append(entry)
        if not rendered:
            continue
        lines.append(f"% ---- {name} ({len(rendered)}) ----")
        lines.extend(rendered)
        lines.append("")
        exported += len(rendered)
        print(f"  {name}: {len(rendered)}", file=sys.stderr)

    if exported == 0:
        raise SystemExit(f"error: export produced no entries; leaving {TARGET.name} untouched")

    payload = "\n".join(lines).rstrip() + "\n"
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", dir=TARGET.parent, prefix=TARGET.name + ".", suffix=".tmp", delete=False
    ) as tmp:
        tmp.write(payload)
        tmp_path = Path(tmp.name)
    tmp_path.replace(TARGET)

    for key in missing:
        print(f"warning: item {key} produced no BibTeX entry", file=sys.stderr)
    print(
        f"Wrote {exported} entries from {total} items to {TARGET.relative_to(REPO_ROOT)}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
