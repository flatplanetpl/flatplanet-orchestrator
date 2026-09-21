#!/usr/bin/env bash
# Install from this checkout. update.sh reuses the same guarded copy operation.
set -euo pipefail

usage() {
  cat <<'HELP'
Usage: bash scripts/install.sh [--update] [APPLICATION_REPOSITORY]

Copy the skill from this checkout into an application Git repository.
The target defaults to the current directory and is resolved to its Git root.

  --update  Back up an existing installation, then replace matching files.
  -h, --help  Show this help.

No network requests, Git staging, or commits are performed. Run git pull
--ff-only in the source checkout first to get the latest version.
HELP
}

die() { printf 'Error: %s\n' "$*" >&2; exit 1; }

mode=install
target=.
target_set=false
while (($#)); do
  case "$1" in
    --update) mode=update ;;
    -h|--help) usage; exit 0 ;;
    --) shift; (($# == 1)) || die 'Expected one repository path after --.'
        "$target_set" && die 'Only one target repository is allowed.'
        target=$1; target_set=true; shift; break ;;
    -*) die "Unknown option: $1" ;;
    *) "$target_set" && die 'Only one target repository is allowed.'
       target=$1; target_set=true ;;
  esac
  shift
done

for tool in git find cp mkdir mktemp rmdir realpath dirname; do
  command -v "$tool" >/dev/null || die "Required command is missing: $tool"
done

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
source_root=$(cd -- "$script_dir/.." && pwd -P)
skill_rel=.agents/skills/flatplanet-orchestrator
source_skill=$source_root/$skill_rel

# Refuse links and special files before traversing or copying either tree.
check_tree() {
  local root=$1 entry bad
  for entry in "$root/.agents" "$root/.agents/skills" "$root/$skill_rel"; do
    [[ ! -L "$entry" ]] || die "Symlinked skill path is unsupported: $entry"
    [[ ! -e "$entry" || -d "$entry" ]] || die "Expected a directory: $entry"
  done
  if [[ -d "$root/$skill_rel" ]]; then
    bad=$(find "$root/$skill_rel" ! -type d ! -type f -print -quit)
    [[ -z "$bad" ]] || die "Links or special files are unsupported: $bad"
  fi
}

check_tree "$source_root"
[[ -f "$source_skill/SKILL.md" && -s "$source_skill/SKILL.md" ]] ||
  die 'Source SKILL.md is missing or empty. Use a complete source checkout.'
source_commit=$(git -C "$source_root" rev-parse --verify HEAD 2>/dev/null) ||
  die 'Source checkout has no Git commit.'
source_changes=$(git -C "$source_root" status --porcelain -- "$skill_rel")

[[ -d "$target" ]] || die "Target directory does not exist: $target"
target_root=$(git -C "$target" rev-parse --show-toplevel 2>/dev/null) ||
  die 'Target must be inside an application Git working tree.'
target_root=$(cd -- "$target_root" && pwd -P)
[[ "$target_root" != "$source_root" ]] ||
  die 'Target must be an application repository, not this source checkout.'
destination=$target_root/$skill_rel

# Serialize these installers without placing a lock inside skill discovery paths.
git_dir=$(git -C "$target_root" rev-parse --absolute-git-dir)
lock_dir=$git_dir/flatplanet-orchestrator-install.lock
mkdir -- "$lock_dir" 2>/dev/null ||
  die "Install/update lock exists or cannot be created: $lock_dir. Check for another run before removing a stale lock."
trap 'rmdir -- "$lock_dir" 2>/dev/null || true' EXIT

check_tree "$target_root"
if [[ "$mode" == install ]]; then
  [[ ! -e "$destination" ]] || die 'Already installed. Use scripts/update.sh instead.'
else
  [[ -f "$destination/SKILL.md" ]] || die 'Skill not installed. Use scripts/install.sh first.'
  # Detect file/directory collisions before making a backup or changing files.
  while IFS= read -r -d '' entry; do
    relative=${entry#"$source_skill"/}
    existing=$destination/$relative
    if [[ -e "$existing" ]]; then
      if [[ -d "$entry" ]]; then
        [[ -d "$existing" ]] || die "File/directory conflict: $existing"
      else
        [[ -f "$existing" ]] || die "File/directory conflict: $existing"
      fi
    fi
  done < <(find "$source_skill" -mindepth 1 -print0)
fi

backup=
if [[ "$mode" == update ]]; then
  state_home=${XDG_STATE_HOME:-${HOME:?HOME must be set}/.local/state}
  [[ "$state_home" == /* ]] || die 'State directory must be an absolute path.'
  backup_root=$state_home/flatplanet-orchestrator/backups
  # Resolve existing symlinks/.. before enforcing the backup location boundary.
  backup_root=$(realpath -m -- "$backup_root")
  case "$backup_root/" in
    "$target_root/"*|"$source_root/"*) die 'Backups must be outside both repositories.' ;;
  esac
  mkdir -p -- "$backup_root"
  backup=$(mktemp -d "$backup_root/update.XXXXXXXX")
  cp -a -- "$destination" "$backup/flatplanet-orchestrator"
  printf 'Backup: %s\n' "$backup/flatplanet-orchestrator"
fi

mkdir -p -- "$target_root/.agents/skills"
# --remove-destination also avoids modifying unrelated hard-linked files in place.
# Updating overlays files: local-only files remain, matching files are replaced.
if [[ "$mode" == install ]]; then
  cp -R -- "$source_skill" "$destination"
else
  if ! cp -R --remove-destination -- "$source_skill/." "$destination/"; then
    die "Update copy failed; the installation may be partial. Full backup: $backup/flatplanet-orchestrator"
  fi
fi

printf '%s complete: %s\nSource commit: %s\n' "$mode" "$destination" "$source_commit"
if [[ -n "$source_changes" ]]; then
  printf 'Note: local skill changes in the source checkout were also copied.\n'
fi
printf 'Review the application repository diff before committing. Start a new Codex session after updating.\n'
