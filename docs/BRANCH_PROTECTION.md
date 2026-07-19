# Main-branch protection

## Intended ownership rule

No collaborator may update `main` without review by `@5qln`. The repository owner remains able to administer and recover the repository.

The repository declares `@5qln` as code owner for every path in `.github/CODEOWNERS`. The auditable target settings are stored in `.github/branch-protection.json`.

## Apply with GitHub CLI

From an authenticated checkout:

```bash
./scripts/apply-branch-protection.sh
```

Or specify another repository and branch:

```bash
./scripts/apply-branch-protection.sh OWNER/REPO BRANCH
```

Do not place a GitHub token in the script or repository. Authenticate locally with `gh auth login`.

## Resulting policy

- Changes from non-admin collaborators must enter through a pull request.
- At least one approval is required.
- Approval by the code owner `@5qln` is required.
- Stale approvals are dismissed when protected content changes.
- The person who pushed the latest revision cannot supply the final approval.
- Review conversations must be resolved.
- Linear history is required.
- Force pushes, deletion, and branch recreation are blocked.
- Repository administrators may bypass the pull-request rule so the owner can recover or maintain the repository.

On a personal-account repository, branch restrictions cannot name organization teams or users. Therefore, do not grant repository `admin` permission to anyone who should not be able to bypass the policy. The ownership guarantee assumes `@5qln` is the only administrator.

## Apply in GitHub's interface

Open [Settings → Branches](https://github.com/5qln/hermes-5qln-plugin/settings/branches), add a classic protection rule for `main`, and select:

1. Require a pull request before merging.
2. Require one approval.
3. Dismiss stale pull-request approvals when new commits are pushed.
4. Require review from Code Owners.
5. Require approval of the most recent reviewable push.
6. Require conversation resolution before merging.
7. Require linear history.
8. Do not allow force pushes.
9. Do not allow deletions.
10. Leave “Do not allow bypassing the above settings” off so the sole owner can administer the repository.

After saving, test with a non-admin collaborator or secondary account. `CODEOWNERS` has no enforcement effect until the protection rule requires Code Owner review.

