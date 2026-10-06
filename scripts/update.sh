#!/usr/bin/env bash
# Refresh an existing installation using the current source checkout.
set -euo pipefail
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
if [[ "${1:-}" == -h || "${1:-}" == --help ]]; then
  printf 'Usage: bash scripts/update.sh [APPLICATION_REPOSITORY]\n\n'
  printf 'Run git pull --ff-only in the source checkout first.\n'
  printf 'Matching skill files are replaced after a full backup; local-only files remain.\n'
  exit 0
fi
exec bash "$script_dir/install.sh" --update "$@"
