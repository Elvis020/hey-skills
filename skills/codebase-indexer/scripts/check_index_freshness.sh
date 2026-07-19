#!/usr/bin/env bash
set -euo pipefail

MODE="enforce"
BASE=""
HEAD="HEAD"

usage() {
  cat <<'USAGE'
Usage: check_index_freshness.sh [--base <rev>] [--head <rev>] [--mode <enforce|warn>]

Checks whether code-like changes also include updates inside .codebase-indexer/docs/.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --base)
      BASE="${2:-}"
      shift 2
      ;;
    --head)
      HEAD="${2:-}"
      shift 2
      ;;
    --mode)
      MODE="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 2
      ;;
  esac
done

if [[ "$MODE" != "enforce" && "$MODE" != "warn" ]]; then
  echo "Invalid mode: $MODE (expected enforce or warn)" >&2
  exit 2
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Not in a git repository; skipping index freshness check."
  exit 0
fi

if [[ ! -d ".codebase-indexer/docs" ]]; then
  echo ".codebase-indexer/docs not found; skipping index freshness check."
  exit 0
fi

if [[ -z "$BASE" ]]; then
  if git rev-parse "${HEAD}~1" >/dev/null 2>&1; then
    BASE="${HEAD}~1"
  else
    echo "No previous commit found for $HEAD; skipping index freshness check."
    exit 0
  fi
fi

if ! git rev-parse "$BASE" >/dev/null 2>&1; then
  echo "Base revision '$BASE' not found; skipping index freshness check."
  exit 0
fi
if ! git rev-parse "$HEAD" >/dev/null 2>&1; then
  echo "Head revision '$HEAD' not found; skipping index freshness check."
  exit 0
fi

changed_files="$(git diff --name-only "$BASE" "$HEAD")"
if [[ -z "$changed_files" ]]; then
  echo "No files changed between $BASE and $HEAD; index freshness check passed."
  exit 0
fi

docs_changed=0
code_like_changed=0
code_like_list=""

is_code_like_path() {
  local p="$1"

  case "$p" in
    .codebase-indexer/docs/*|.codebase-indexer/reports/*|.codebase-indexer/savings.jsonl)
      return 1
      ;;
  esac

  case "$p" in
    *.c|*.cc|*.cpp|*.cs|*.go|*.h|*.hpp|*.java|*.js|*.jsx|*.kt|*.kts|*.m|*.mm|*.php|*.py|*.rb|*.rs|*.scala|*.sh|*.sql|*.swift|*.ts|*.tsx|*.yaml|*.yml|*.json|*.toml|Dockerfile|Dockerfile.*)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

while IFS= read -r path; do
  [[ -z "$path" ]] && continue

  if [[ "$path" == .codebase-indexer/docs/* ]]; then
    docs_changed=1
    continue
  fi

  if is_code_like_path "$path"; then
    code_like_changed=1
    code_like_list+=" - $path"$'\n'
  fi
done <<< "$changed_files"

if [[ "$code_like_changed" -eq 0 ]]; then
  echo "No code-like files changed; index freshness check passed."
  exit 0
fi

if [[ "$docs_changed" -eq 1 ]]; then
  echo "Index docs were updated alongside code changes; check passed."
  exit 0
fi

cat <<EOFMSG
Index freshness check failed.

Code-like files changed between $BASE and $HEAD, but no file under .codebase-indexer/docs/ was updated.
Changed code-like files:
$code_like_list
Run update mode and commit the doc updates before merging.
EOFMSG

if [[ "$MODE" == "warn" ]]; then
  exit 0
fi

exit 1
