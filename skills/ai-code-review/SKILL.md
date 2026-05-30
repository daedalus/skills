---
name: ai-code-review
description: >
  Orchestrate multi-agent AI code review on a git diff or merge request. Use this skill
  whenever the user wants to review code changes with AI, analyze a diff, audit a pull
  request or merge request, check for bugs/security issues/performance problems, or
  set up an automated code review pipeline. Trigger even for casual phrasing like
  "can you review this PR", "check my diff for issues", "look over these changes", or
  "what do you think of this code change". Always use this skill when code review,
  diff analysis, or MR/PR review is involved — do not attempt ad-hoc review without it.
  Do NOT trigger for reviewing prose, essays, documentation-only files, or non-code content.
---

# AI Code Review Skill

Orchestrate a structured, multi-agent AI code review over a git diff or merge request.
Instead of one generic prompt, this skill dispatches specialised reviewers in parallel,
then consolidates findings into a single structured report.

---

## Workflow Overview

1. **Ingest** – collect the diff and MR/PR metadata
2. **Triage** – classify risk tier and select the agent roster
3. **Filter** – strip noise (lock files, generated files, minified assets)
4. **Review** – run specialised agents concurrently
5. **Consolidate** – deduplicate, re-categorise, apply reasonableness filter
6. **Report** – post a structured comment with an approval decision

---

## Step 1 — Ingest the Diff

Ask the user for:
- The **diff** (paste, file upload, or `git diff` output)
- Optional: MR/PR title, description, linked issue, previous review comments

If the user provides a repo path, generate the diff with:
```bash
git diff main...HEAD          # all changes vs base branch
# or for a specific commit range:
git diff <base_sha>..<head_sha>
```

Parse the diff into per-file patch entries, recording:
- `path` (new path)
- `addedLines` / `removedLines`
- `isBinary`

---

## Step 2 — Risk Tier Classification

Classify the MR into one of three tiers:

| Tier    | Condition                                          | Agents | Coordinator model |
|---------|----------------------------------------------------|--------|-------------------|
| Trivial | ≤10 lines changed AND ≤20 files                    | 2      | Standard          |
| Lite    | ≤100 lines AND ≤20 files (and not security-sensitive) | 4   | Standard          |
| Full    | >100 lines OR >50 files OR any security-sensitive file | 7  | Top-tier          |

> **Why OR for Full but AND for Trivial?** Trivial requires *both* conditions to be small
> to safely downscale. Full triggers on *any* large dimension because either a huge diff
> or many files independently warrants thorough review. A 5-line change across 51 files
> (e.g. a global rename) needs full review just as much as a 500-line change in one file.

**Security-sensitive paths** (always → Full tier):
`auth/`, `crypto/`, `secrets/`, `token`, `password`, `oauth`, `jwt`, `cert`, `key`, `*.pem`, `*.env`

---

## Step 3 — Diff Filtering

Strip these from the diff before any agent sees it:

**Lock files:** `bun.lock`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`,
`Cargo.lock`, `go.sum`, `poetry.lock`, `Pipfile.lock`, `flake.lock`

**Noisy extensions:** `.min.js`, `.min.css`, `.bundle.js`, `.map`, `.snap`

**Generated files:** files whose first 5 lines contain `@generated`, `Code generated`,
`DO NOT EDIT`, `eslint-disable` (entire file), `prettier-ignore` (entire file)

**Exception:** always keep database migrations even if marked generated.

**Binary files:** skip entirely — images, compiled artifacts, and other binary files
cannot be meaningfully reviewed as text diffs. Note their presence in the report
("N binary files changed, skipped") but do not flag them as findings.

---

## Step 4 — Specialised Agents

Run agents appropriate to the risk tier. Each agent receives:
- Its focused prompt (see below)
- Only the patch files relevant to its domain
- A shared MR context block (title, description, linked issues)

**Tier escalation:** If any non-Full-tier agent produces a `critical` finding mid-review,
immediately spawn the Security and Performance agents and upgrade the decision to Full tier.
Don't wait for the coordinator pass — escalate as soon as the finding is confirmed.

### Agent Roster

| Agent | Tier | Focus |
|---|---|---|
| **Coordinator** | All | Consolidates all findings, makes approval decision |
| **Code Quality** | All | Logic errors, dead code, naming, complexity |
| **Security** | Full | Injections, auth bypasses, hardcoded secrets, crypto misuse |
| **Performance** | Full | N+1 queries, unbounded loops, memory leaks, blocking I/O |
| **Documentation** | Lite + Full | Missing/outdated docstrings, changelog entries, README gaps |
| **Release** | Full | Version bumps, migration steps, breaking API changes |
| **Compliance** | Full | Adherence to project conventions in AGENTS.md / CONTRIBUTING.md |

### Agent Prompt Principles

Each agent prompt MUST include both a **"What to Flag"** and a **"What NOT to Flag"** section.
The negative constraints are where the real signal-to-noise value lives.

**Code Quality**
```
What to Flag: logic errors, unreachable code, incorrect error handling, unsafe type
  coercions, overly complex functions (high cyclomatic complexity), misleading naming.
What NOT to Flag: style preferences with no correctness impact, refactors that aren't
  in scope of this MR, issues in unchanged code.
```

**Security**
```
What to Flag: injection vulnerabilities (SQL, XSS, command, path traversal),
  auth/authorisation bypasses in changed code, hardcoded secrets or API keys,
  insecure cryptographic usage, missing input validation at trust boundaries.
What NOT to Flag: theoretical risks requiring unlikely preconditions, defense-in-depth
  suggestions when primary defenses are adequate, issues in unchanged code,
  "consider using library X" style suggestions.
```

**Performance**
```
What to Flag: N+1 query patterns, unbounded loops over large datasets, synchronous
  blocking I/O on hot paths, obvious memory leaks (growing collections never cleared),
  missing indexes implied by new query patterns.
What NOT to Flag: micro-optimisations with no measurable impact, speculative future
  scale concerns, performance issues in unchanged code.
```

**Documentation**
```
What to Flag: public functions/methods added without docstrings, changed behaviour not
  reflected in existing docs, new CLI flags or env vars not mentioned in README,
  missing changelog entry for user-visible changes.
What NOT to Flag: internal/private function documentation, stylistic doc improvements,
  docs for unchanged behaviour.
```

**Release**
```
What to Flag: breaking API changes without a version bump, missing migration guide for
  schema changes, dependency upgrades that change transitive behaviour.
What NOT to Flag: internal refactors with no external surface change, patch-level fixes
  that don't require a changelog entry.
```

**Compliance**
```
What to Flag: violations of explicit conventions in AGENTS.md or CONTRIBUTING.md
  (test patterns, file structure, naming conventions), use of banned dependencies.
What NOT to Flag: conventions not documented anywhere, personal style preferences,
  deviations from conventions in unchanged legacy code.
```

### Finding Severity

Every finding must have one of three severities:

| Severity | Meaning |
|---|---|
| `critical` | Will cause an outage, data loss, or is directly exploitable |
| `warning` | Measurable regression or concrete risk under realistic conditions |
| `suggestion` | An improvement worth considering, no immediate risk |

---

## Step 5 — Coordinator Consolidation

After all agents complete, the coordinator performs:

1. **Deduplication** – same issue flagged by multiple agents → keep once, in the most relevant section
2. **Re-categorisation** – move findings to the correct domain if mis-filed
3. **Reasonableness filter** – drop speculative issues, false positives, findings contradicted by existing code
4. **Verification** – if uncertain, read the relevant source file before deciding

### Approval Decision Rubric

| Condition | Decision | Action |
|---|---|---|
| All LGTM, or only trivial suggestions | `approved` | Approve |
| Only `suggestion`-severity items | `approved_with_comments` | Approve + comment |
| Some `warning`s, no production risk | `approved_with_comments` | Approve + comment |
| Multiple warnings suggesting a risk pattern | `minor_issues` | Request changes |
| Any `critical`, or production safety risk | `significant_concerns` | Block + explain |

**Bias toward approval.** A single warning in an otherwise clean MR → `approved_with_comments`, not a block.

---

## Step 6 — Report Format

Output a single structured review comment:

```
## AI Code Review

**Decision:** approved_with_comments  
**Risk Tier:** lite  
**Reviewers:** Code Quality, Documentation

---

### 🔴 Critical
_None_

### 🟡 Warnings
- **[Code Quality]** `src/auth/login.ts:42` — Password comparison uses `==` instead of
  a constant-time function; susceptible to timing attacks under load.

### 🔵 Suggestions
- **[Documentation]** `README.md` — The new `--dry-run` flag added in this MR is not
  documented in the CLI reference section.

---

**Summary:** Logic looks solid. One warning worth addressing before merge; documentation
gap is minor but easy to fix.
```

Always include:
- Decision badge
- Risk tier and which agents ran
- Findings grouped by severity (omit empty sections or show "None")
- One-sentence summary

---

## Handling Re-Reviews

When re-reviewing after new commits:
- Receive the previous review findings and their resolution status
- **Fixed findings:** omit from new output
- **Unfixed findings:** re-emit so they stay visible
- **User-resolved findings:** respect unless the issue materially worsened (e.g. the
  same function now accepts untrusted external input where it previously only handled
  internal data, making a previously-theoretical risk concrete)
- **"Won't fix" replies:** treat as resolved; don't re-flag

---

## Cost & Token Tips

> These tips apply when implementing this skill in a CI pipeline with real subprocess
> orchestration. In a plain chat context, Claude simulates the agents inline — the
> principles still apply conceptually but there are no actual files or processes to manage.

- Write per-file patches to temp files; pass paths rather than embedding full diffs in prompts
- Extract a shared MR context block once; reference it across agents rather than duplicating it 7×
- Downgrade the coordinator to a standard model for Trivial-tier reviews
- Warn the user if the diff exceeds ~500 files — reviews at that scale are expensive and an incremental approach (reviewing logical chunks separately) is usually better

---

## Limitations to Communicate

Be upfront with the user that AI review does not catch:
- **Architectural fit** – whether the approach is right for the system
- **Cross-repo impact** – downstream consumers of a changed API contract
- **Subtle concurrency bugs** – timing-dependent race conditions
- **Business logic correctness** – only the team knows the intended behavior

Frame the review as a first-pass signal booster, not a replacement for human review.
