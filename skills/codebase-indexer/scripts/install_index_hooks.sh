#!/usr/bin/env bash
set -euo pipefail

FORCE=0

usage() {
  cat <<'USAGE'
Usage: install_index_hooks.sh [--force]

Installs post-commit and post-merge hooks that run:
  scripts/check_index_freshness.sh --mode warn

By default, existing non-indexer hooks are preserved and installation fails.
Use --force to back up existing hooks and replace them.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --force)
      FORCE=1
      shift
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

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Run this from inside a git repository."
  exit 1
fi

repo_root="$(git rev-parse --show-toplevel)"
hooks_dir="$repo_root/.git/hooks"
mkdir -p "$hooks_dir"

is_managed_hook() {
  local hook_file="$1"
  [[ -f "$hook_file" ]] && rg -q "codebase-indexer freshness hook" "$hook_file"
}

prepare_hook_path() {
  local hook_name="$1"
  local hook_file="$hooks_dir/$hook_name"

  if [[ ! -f "$hook_file" ]]; then
    return 0
  fi

  if is_managed_hook "$hook_file"; then
    return 0
  fi

  if [[ "$FORCE" -eq 0 ]]; then
    echo "Existing hook found at $hook_file."
    echo "Re-run with --force to back it up and replace it."
    exit 1
  fi

  local backup="$hook_file.pre-codebase-indexer.$(date +%Y%m%d%H%M%S).bak"
  mv "$hook_file" "$backup"
  echo "Backed up existing $hook_name hook to $(basename "$backup")."
}

prepare_hook_path "post-commit"
cat > "$hooks_dir/post-commit" <<'HOOK'
#!/usr/bin/env bash
set -euo pipefail
# codebase-indexer freshness hook
repo_root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
[[ -z "$repo_root" ]] && exit 0
"$repo_root/scripts/check_index_freshness.sh" --mode warn
HOOK
chmod +x "$hooks_dir/post-commit"

prepare_hook_path "post-merge"
cat > "$hooks_dir/post-merge" <<'HOOK'
#!/usr/bin/env bash
set -euo pipefail
# codebase-indexer freshness hook
repo_root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
[[ -z "$repo_root" ]] && exit 0

if git rev-parse ORIG_HEAD >/dev/null 2>&1; then
  "$repo_root/scripts/check_index_freshness.sh" --mode warn --base ORIG_HEAD --head HEAD
else
  "$repo_root/scripts/check_index_freshness.sh" --mode warn
fi
HOOK
chmod +x "$hooks_dir/post-merge"

echo "Installed post-commit and post-merge hooks."
echo "They run scripts/check_index_freshness.sh in warn mode."
