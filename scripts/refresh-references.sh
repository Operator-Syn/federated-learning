#!/usr/bin/env bash
#
# Regenerate docs/literature/references.bib from the Thesis_BJY Zotero group library.
#
# Why this exists: the Zotero library is the source of truth for references, and
# this file is the artefact the paper is actually cited from. Exporting on demand
# keeps both in step without hand-maintaining a .bib.
#
# Requires: Zotero desktop running with "Allow other applications on this computer
# to communicate with Zotero" enabled, and Better BibTeX installed (BBT supplies
# the citation keys and the BibTeX rendering behind the local API).
#
# Usage: scripts/refresh-references.sh
#
# Environment overrides:
#   ZOTERO_LOCAL_API  local API base  (default http://127.0.0.1:23119/api)
#   ZOTERO_GROUP_ID   group library id (default 6767052, the Thesis_BJY group)
#
# Algorithm:
#   1. Resolve the repository root from this script's own location, so the script
#      works from any working directory.
#   2. Enumerate the library through the plain JSON API, 100 items per page, and
#      keep only bibliographic items. Attachments and notes have no BibTeX form,
#      and they would otherwise occupy slots in the export requests below.
#   3. Export those items one at a time. The local API ignores ?itemKey=, and
#      ?format=bibtex silently caps at 50 items per request, so a bulk request
#      returns a partial bibliography that looks complete -- the trap this script
#      exists to avoid.
#   4. Fail loudly on any shortfall: a failed request, a zero-item library, or an
#      export that produced fewer entries than there are items. The existing .bib
#      is left untouched in every one of those cases, because a truncated
#      bibliography is only discovered months later, in the camera-ready.
#   5. Write to a temporary file beside the target and move it into place, so a
#      partial download can never replace a good bibliography.
#
set -euo pipefail

LOCAL_API="${ZOTERO_LOCAL_API:-http://127.0.0.1:23119/api}"
GROUP_ID="${ZOTERO_GROUP_ID:-6767052}"
PAGE_SIZE=100

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(dirname -- "$script_dir")"
target="$repo_root/docs/literature/references.bib"

fail() {
  echo "error: $*" >&2
  exit 1
}

tmp="$(mktemp "$target.XXXXXX")"
keys_file="$(mktemp)"
trap 'rm -f -- "$tmp" "$keys_file"' EXIT

echo "Fetching group $GROUP_ID from $LOCAL_API" >&2

# --- 1. collect bibliographic item keys, 100 per page -----------------------
start=0
while :; do
  # -f turns an HTTP error into a non-zero exit instead of feeding error text
  # into the key list.
  page="$(curl -fsS --max-time 30 \
    "$LOCAL_API/groups/$GROUP_ID/items/top?limit=$PAGE_SIZE&start=$start")" \
    || fail "request failed: items/top?start=$start (is Zotero running with the local API enabled?)"

  # first line is the raw page size, which drives pagination; the rest are keys
  parsed="$(printf '%s' "$page" | python3 -c '
import json, sys
items = json.load(sys.stdin)
print(len(items))
for item in items:
    if item["data"].get("itemType") not in ("attachment", "note"):
        print(item["key"])
')"

  item_count="$(printf '%s\n' "$parsed" | head -n1)"
  printf '%s\n' "$parsed" | tail -n +2 >>"$keys_file"

  (( item_count < PAGE_SIZE )) && break
  (( start += PAGE_SIZE ))
done

total_keys="$(wc -l <"$keys_file" | tr -d ' ')"
(( total_keys > 0 )) || fail "group $GROUP_ID returned no bibliographic items; leaving $target untouched"

# --- 2. export one item at a time -------------------------------------------
# The local API ignores ?itemKey= entirely: a request naming two keys returns the
# whole library. Per-item export is the only reliable shape, and 90 requests cost
# a few seconds.
exported=0
missing=0
while read -r key; do
  [[ -n "$key" ]] || continue
  entry="$(curl -fsS --max-time 30 "$LOCAL_API/groups/$GROUP_ID/items/$key?format=bibtex")" \
    || fail "export failed for item $key"

  if [[ "$entry" != *"@"* ]]; then
    # an item with no renderable form: report it, never silently drop it
    missing=$((missing + 1))
    echo "warning: item $key produced no BibTeX entry" >&2
    continue
  fi

  printf '%s\n\n' "$entry" >>"$tmp"
  exported=$((exported + $(grep -c '^@' <<<"$entry" || true)))
done <"$keys_file"

(( missing == 0 )) || echo "warning: $missing item(s) skipped for lack of metadata" >&2
(( exported > 0 )) || fail "export produced no entries; leaving $target untouched"

mv -f -- "$tmp" "$target"
echo "Wrote $exported entries from $total_keys items to ${target#"$repo_root"/}" >&2
