#!/usr/bin/env bash
# Copied from unity-kit scripts/find-unity.sh (MIT (c) 2026 Benjamin Curlier) - see ATTRIBUTION.md. Unchanged except this header.
# Lists installed Unity editors as JSON: [{version, channel, exe}], newest first.
# macOS/Linux port of find-unity.ps1. Override the Hub root with --search-root <dir>.
set -euo pipefail

SEARCH_ROOT=""
if [[ "${1:-}" == "--search-root" && -n "${2:-}" ]]; then
  SEARCH_ROOT="$2"
elif [[ "$(uname -s)" == "Darwin" ]]; then
  SEARCH_ROOT="/Applications/Unity/Hub/Editor"
else
  SEARCH_ROOT="$HOME/Unity/Hub/Editor"
fi

if [[ ! -d "$SEARCH_ROOT" ]]; then
  echo "No Unity Hub editor directory at $SEARCH_ROOT (use --search-root for custom locations)" >&2
  exit 1
fi

entries=()
for dir in "$SEARCH_ROOT"/*/; do
  v="$(basename "$dir")"
  if [[ "$(uname -s)" == "Darwin" ]]; then
    exe="$dir/Unity.app/Contents/MacOS/Unity"
  else
    exe="$dir/Editor/Unity"
  fi
  [[ -x "$exe" ]] || continue
  case "$v" in
    *f*) channel="stable" ;;
    *b*) channel="beta" ;;
    *a*) channel="alpha" ;;
    *)   channel="unknown" ;;
  esac
  # Sort key, tab-separated ahead of the JSON: Unity versions are 6000.0.58f1 — dotted numbers with
  # the channel letter and its build fused to the last component, so a lexical sort puts 6000.0.9f1
  # ahead of 6000.0.58f1. Compare the numeric components, then the channel (stable > beta > alpha),
  # then the channel build. A version with no suffix keeps its whole name as the numeric core.
  core="${v%%[abf]*}"
  suffix="${v#"$core"}"
  case "${suffix:0:1}" in
    f) rank=3 ;;
    b) rank=2 ;;
    a) rank=1 ;;
    *) rank=0 ;;
  esac
  chbuild="${suffix:1}"
  IFS=. read -r maj min pat <<<"$core"
  entries+=("$(printf '%s\t%s\t%s\t%s\t%s\t{"version":"%s","channel":"%s","exe":"%s"}' \
    "${maj:-0}" "${min:-0}" "${pat:-0}" "$rank" "${chbuild:-0}" "$v" "$channel" "$exe")")
done

if [[ ${#entries[@]} -eq 0 ]]; then
  echo "No Unity editors found under $SEARCH_ROOT" >&2
  exit 1
fi

printf '%s\n' "${entries[@]}" |
  sort -t$'\t' -k1,1nr -k2,2nr -k3,3nr -k4,4nr -k5,5nr |
  cut -f6- | paste -sd',' - | sed 's/^/[/; s/$/]/'
