#!/usr/bin/env bash
set -euo pipefail

repo="${1:-5qln/hermes-5qln-plugin}"
branch="${2:-main}"
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
policy_file="${script_dir}/../.github/branch-protection.json"

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI is required: https://cli.github.com/" >&2
  exit 2
fi

gh auth status >/dev/null

gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "repos/${repo}/branches/${branch}/protection" \
  --input "${policy_file}"

echo
echo "Applied branch protection to ${repo}:${branch}."
echo "Verify at https://github.com/${repo}/settings/branches"

