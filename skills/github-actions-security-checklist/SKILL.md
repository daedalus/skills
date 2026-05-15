---
name: github-actions-security
description: >
  Apply a comprehensive GitHub Actions security checklist to audit, harden, and fix
  CI/CD workflows against supply chain attacks. Use this skill whenever the user mentions
  GitHub Actions security, workflow hardening, CI/CD supply chain risks, secret exposure
  in pipelines, pinning actions, OIDC vs static secrets, pull_request_target risks,
  script injection in workflows, self-hosted runner security, or artifact/cache poisoning.
  Also trigger when the user shares a workflow YAML file and wants it reviewed, audited,
  or improved for security. Even if the user only asks a narrow question like "is my
  workflow safe?" or "how do I pin actions?", use this skill to provide structured,
  checklist-backed guidance.
---

# GitHub Actions Security Skill

A practical skill for auditing and hardening GitHub Actions workflows against supply
chain attacks, secret theft, poisoned pipeline execution, and excessive token permissions.

## Source reference

Based on: https://corgea.com/learn/github-actions-security-checklist  
Also informed by: GitHub's 2026 Actions security roadmap, OpenSSF, OWASP CI/CD Top 10,
and GitHub Security Lab guidance on preventing pwn requests.

---

## When the user shares a workflow file

1. Read the YAML carefully.
2. Check it against all 10 checklist areas below.
3. Report findings grouped by risk area with severity (Critical / High / Medium / Low).
4. Provide concrete fixed snippets for every finding.
5. Summarize with a prioritized remediation list.

---

## The five controls to always check first

Before anything else, verify these five — they cover the highest-impact failures:

| # | Control | Why it matters |
|---|---------|---------------|
| 1 | `GITHUB_TOKEN` permissions set to read-only by default | Limits blast radius of any compromised job |
| 2 | Third-party actions pinned to full commit SHA | Tags are mutable and can be hijacked |
| 3 | No `pull_request_target` for public repos or fork PRs | Runs privileged context on untrusted code |
| 4 | All PR/issue/commit metadata treated as untrusted input | Branch names and PR titles can inject shell commands |
| 5 | OIDC used for cloud access instead of static secrets | Short-lived credentials sharply reduce secret theft value |

---

## Full checklist (10 areas)

### 1. Organization and repository defaults

- [ ] Workflow token permissions set to read-only by default
- [ ] "Allow GitHub Actions to create and approve pull requests" is disabled
- [ ] Fork PR workflow approval set to "Require approval for all outside collaborators" in Settings → Actions → Fork pull request workflows
- [ ] Allowed actions restricted to GitHub-owned, verified creators, or an explicit allowlist
- [ ] `.github/workflows/` covered by CODEOWNERS
- [ ] Branch protection / repository rulesets require PR review, block force pushes, require status checks, dismiss stale approvals

### 2. Explicit workflow permissions

- [ ] `permissions:` declared at workflow or job level (not relying on defaults)
- [ ] Write scopes granted only to jobs that need them
- [ ] `id-token: write` granted only to OIDC jobs, not globally
- [ ] Read-only validation separated from privileged publishing jobs

**Minimal safe pattern:**
```yaml
permissions: {}         # deny all at workflow level

jobs:
  build:
    permissions:
      contents: read    # grant only what this job needs
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@<full-commit-sha>
```

**Trusted-build / privileged-publish split pattern:**

Run untrusted code in a `pull_request` workflow (no secrets, read-only), then publish
only after CI passes via a `workflow_run` workflow that holds credentials:

```yaml
# workflow-ci.yml — triggered by pull_request, no secrets, read-only
on: [pull_request]
jobs:
  test:
    permissions:
      contents: read
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
      - run: npm test

# workflow-publish.yml — triggered only after CI passes on main
on:
  workflow_run:
    workflows: ["CI"]
    types: [completed]
    branches: [main]
jobs:
  publish:
    if: github.event.workflow_run.conclusion == 'success'
    permissions:
      contents: write
      id-token: write
    environment: production
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
      - run: npm publish
```

### 3. Dangerous triggers and untrusted execution paths

- [ ] `pull_request_target` avoided in public repos; if used, never checks out or executes PR head code without maintainer review
- [ ] `workflow_run` workflows check the upstream event before privileged actions
- [ ] `issue_comment`, `pull_request_review`, `pull_request_review_comment` triggers audited for privilege
- [ ] `pull_request` used for untrusted fork code (withholds secrets and write permissions by default)
- [ ] Stale PRs closed or rebased after fixing a vulnerable workflow

**`workflow_run` guard pattern:** A `workflow_run` job runs with the base repo's full
permissions even when the upstream workflow was triggered by a fork PR. Always check the
upstream trigger and repo before taking any privileged action:

```yaml
# ❌ Dangerous: privileged job runs regardless of what triggered upstream
on:
  workflow_run:
    workflows: ["CI"]
    types: [completed]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - run: ./deploy.sh  # runs even for fork PRs!

# ✅ Guard with explicit checks before privileged steps
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Abort if triggered by a fork PR
        if: |
          github.event.workflow_run.event == 'pull_request' &&
          github.event.workflow_run.head_repository.full_name != github.repository
        run: |
          echo "Refusing to run privileged job for fork PR"
          exit 1
      - run: ./deploy.sh  # only reached for internal PRs or push events
```

### 4. Script injection prevention

Untrusted values include: branch names, PR titles/bodies, issue titles/bodies, labels,
comments, commit messages, artifact contents from untrusted workflows.

**Never interpolate untrusted context directly into `run:` blocks:**
```yaml
# ❌ Unsafe
- run: echo "Branch is ${{ github.head_ref }}"

# ✅ Safe — pass through environment variable
- run: echo "Branch is $BRANCH"
  env:
    BRANCH: ${{ github.head_ref }}
```

Checklist:
- [ ] Untrusted context passed through environment variables, not inline `${{ }}`
- [ ] Shell variables quoted when used
- [ ] Purpose-built actions preferred over inline shell for parsing untrusted input
- [ ] No untrusted data written to `GITHUB_ENV` or `GITHUB_PATH`
- [ ] No untrusted data written to `GITHUB_OUTPUT` or `GITHUB_STEP_SUMMARY`
- [ ] Artifact contents from PR workflows treated as attacker-controlled

### 5. Third-party action pinning

- [ ] All third-party actions pinned to full commit SHA (not a tag or branch)
- [ ] SHA verified to belong to the original repo, not a fork
- [ ] Preference for GitHub-owned or verified creator actions
- [ ] Transitive action dependencies reviewed — a pinned top-level action can still call nested actions by mutable tag; review the action's own `action.yml` for `uses:` references in composite steps, or use `zizmor`/`actionlint` to detect transitive unpinned references
- [ ] Dependabot or Renovate configured to update SHAs through reviewed PRs
- [ ] Dependency graph and Dependabot alerts enabled for actions

**Example:**
```yaml
# ❌ Mutable tag — can be moved by attacker
- uses: actions/checkout@v4

# ✅ Immutable SHA
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
```

### 6. Secret hygiene

- [ ] Secrets scoped to environments with protection rules and required reviewers for production
- [ ] Secrets passed only to the specific step that needs them (not job-level `env:`)
- [ ] Secrets never passed as command-line arguments (use env vars)
- [ ] Secrets (including encoded or transformed forms) never echoed
- [ ] `secrets: inherit` avoided in reusable workflows; only named secrets passed
- [ ] Stale secrets rotated and removed

### 7. OIDC for cloud credentials

- [ ] Cloud trust policies configured with repo, branch, environment, and workflow constraints
- [ ] `id-token: write` granted only to the job that exchanges the token
- [ ] Cloud roles limited to the exact operation (deploy, publish, etc.)
- [ ] Environment approvals required for production OIDC jobs

**AWS IAM trust policy — scoped to a specific repo and environment:**
```json
{
  "Condition": {
    "StringEquals": {
      "token.actions.githubusercontent.com:sub":
        "repo:myorg/myrepo:environment:production",
      "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
    }
  }
}
```

> ⚠️ Avoid `StringLike` with wildcards unless you explicitly need flexibility.
> `repo:myorg/*` trusts every repository in the org — a compromised repo becomes a
> path to production credentials. Prefer exact `repo:org/repo:environment:name` claims.

### 8. Runner hardening

- [ ] Self-hosted runners not used for public repositories
- [ ] Ephemeral or just-in-time runners used for sensitive private workflows (destroyed after one job)
- [ ] Runner groups separated by trust level (public / private / release / production)
- [ ] Runner network egress restricted to required endpoints only
- [ ] Runner registrations and unexpected public repo creation monitored

### 9. Artifacts, caches, and release workflows

- [ ] Artifact uploads scoped to explicit paths (not `path: .`)
- [ ] `.env`, keys, credentials, and generated configs excluded from artifact uploads
- [ ] `persist-credentials: false` set on `actions/checkout` unless later steps need the token
- [ ] Untrusted artifacts extracted outside the workspace to a temporary directory
- [ ] Secrets and release credentials not cached
- [ ] Caches avoided in privileged release workflows
- [ ] Provenance and attestations used for package releases where supported

**Cache poisoning:** Cache keys are deterministic (e.g. based on `hashFiles('**/package-lock.json')`),
so a fork PR can compute the same key, write a poisoned cache entry first, and have it
restored by your privileged release workflow. Mitigate by scoping cache keys to protected
branches and never restoring caches in release jobs:

```yaml
# Scope cache key to the current branch — fork PRs write to a different key
- uses: actions/cache@<sha>
  with:
    path: ~/.npm
    key: ${{ runner.os }}-${{ github.ref }}-${{ hashFiles('**/package-lock.json') }}
```

### 10. Continuous detection

- [ ] Workflow linting in CI using both complementary tools:
  - **`actionlint`** — syntax validation, shellcheck integration, expression type checking; catches malformed workflows and shell errors
  - **`zizmor`** — security-focused; catches unsafe interpolation, dangerous triggers, unpinned actions
- [ ] OpenSSF Scorecard run to surface supply chain posture across the repo
- [ ] Code scanning enabled for workflow vulnerabilities (CodeQL supports common patterns)
- [ ] Action dependency changes reviewed in PRs like application dependency updates
- [ ] Alerts on failed attempts to use blocked actions or unpinned references
- [ ] Incident playbook documented: disable workflows → revoke tokens → rotate secrets → block actions → inspect runner activity

---

## Rollout order for hardening many repos

1. **Inventory** — workflows with write permissions, secrets, release jobs, self-hosted runners, public fork triggers
2. **Org defaults** — read-only token permissions, action restrictions, CODEOWNERS, PR approval protections
3. **High-risk patterns** — `pull_request_target`, `workflow_run`, untrusted interpolation, `GITHUB_ENV`, broad secret exposure
4. **Pin actions** — convert mutable references to full SHAs, add Dependabot/Renovate
5. **OIDC migration** — start with production deploy and package publish workflows
6. **Monitoring** — workflow linting, dependency alerts, audit logs, runner registration alerts

---

## Severity classification guide

| Severity | Examples |
|----------|---------|
| **Critical** | `pull_request_target` checking out fork head; secrets in `run:` args; unpinned third-party action on a release job |
| **High** | Script injection via `${{ github.head_ref }}` in `run:`; `write-all` permissions; self-hosted runner on public repo |
| **Medium** | Missing `permissions:` block; `secrets: inherit`; no CODEOWNERS on workflows |
| **Low** | Broad artifact upload; missing `persist-credentials: false`; stale secrets not rotated |

---

## Key external references

- [GitHub Actions security hardening guide](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions)
- [GitHub Security Lab: preventing pwn requests](https://securitylab.github.com/resources/github-actions-preventing-pwn-requests/)
- [OpenSSF: mitigating attack vectors in GitHub workflows](https://openssf.org/blog/2024/08/12/mitigating-attack-vectors-in-github-workflows/)
- [OWASP: Poisoned Pipeline Execution](https://owasp.org/www-project-top-10-ci-cd-security-risks/)
- [GitHub 2026 Actions security roadmap](https://github.blog/news-insights/product-news/whats-coming-to-our-github-actions-2026-security-roadmap/)
