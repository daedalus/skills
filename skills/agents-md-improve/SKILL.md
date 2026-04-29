---
name: agents-md
description: >
  Write, audit, or improve AGENTS.md files for agentic coding workflows. Use this skill
  whenever the user wants to create, review, or refactor an AGENTS.md (or CLAUDE.md,
  COPILOT.md, or any agent instruction file) for a codebase, module, or monorepo. Also
  trigger when the user asks why their agent keeps over-exploring, reading irrelevant docs,
  or producing incomplete PRs — those are symptoms this skill diagnoses. Trigger even for
  vague requests like "help me write docs for my agent" or "how should I structure my
  agent instructions".
---

# AGENTS.md Skill

Empirically-grounded guidance for writing agent instruction files (`AGENTS.md`, `CLAUDE.md`,
etc.). Based on AuggieBench eval results (Augment Code, Apr 2026).

**Core finding**: The same file can improve one task by 25% and tank another by 30%.
What you leave out matters as much as what you put in.

## Reference files

- `refs/patterns.md` — The six effective patterns with examples and data. Read when
  writing or improving an AGENTS.md.
- `refs/failure-modes.md` — Four failure modes with diagnosis and fixes. Read when
  auditing a broken or underperforming AGENTS.md.

---

## Workflow: Writing an AGENTS.md

1. **Identify the module scope.** Count core files. Check for surrounding doc sprawl
   (specs, architecture docs nearby). Sprawl is an environment problem — fix it before
   fixing the entry point.
2. **Pick the right size target.**

   | Module size       | AGENTS.md target       | Reference files |
   |-------------------|------------------------|-----------------|
   | Small (<30 files) | 50–80 lines            | 0–1             |
   | Mid (~100 files)  | 100–150 lines          | 2–5             |
   | Large (200+)      | 100–150 lines + refs   | 5–10, scoped    |

   Do not scale length with module size. Scale the reference structure instead.

3. **Identify which problems exist.** Use the decision table below to pick patterns.
4. **Write the entry point.** Apply patterns from `refs/patterns.md`. Keep architecture
   prose to 2–3 sentences max. Describe boundaries, not internals.
5. **Push depth into reference files.** Each ref needs a clear scope statement in
   `AGENTS.md` so the agent knows exactly when to open it. Max 10–15 refs total.
6. **Audit for failure modes.** Check against `refs/failure-modes.md` before shipping.

---

## Workflow: Auditing an existing AGENTS.md

1. **Check the environment first.** Does the module have large surrounding doc sprawl?
   If yes — that's likely the primary problem, not the file itself.
2. **Measure line count.** Over 150 lines → start splitting into reference files.
3. **Count "don'ts" without "dos".** More than 5 → warning overload risk.
4. **Look for architecture prose.** Descriptions of *why* things are structured a certain
   way → overexploration trigger. Cut or move to refs.
5. **Check for net-new patterns.** If the task requires a pattern not in the codebase,
   AGENTS.md will steer wrong. Needs a spec, not docs.

---

## Decision table: which pattern to apply

| Symptom / Goal                              | Pattern                                 | Details               |
|---------------------------------------------|-----------------------------------------|-----------------------|
| Agent reinvents existing abstractions       | Real codebase examples                  | refs/patterns.md §4   |
| Agent picks wrong library or approach       | Decision table                          | refs/patterns.md §3   |
| Agent ships features with missing wiring    | Procedural workflow                     | refs/patterns.md §2   |
| Agent ignores codebase conventions          | "Don't" + "Do" pairs                    | refs/patterns.md §5   |
| Agent over-explores before writing code     | Progressive disclosure; trim arch prose | refs/failure-modes.md §1 |
| Removing AGENTS.md barely changes behavior  | Audit surrounding doc sprawl            | refs/failure-modes.md §3 |
| Agent builds the wrong architecture         | Spec-driven development first           | refs/failure-modes.md §4 |

---

## Document discovery rates

| Location                               | Read rate |
|----------------------------------------|-----------|
| `AGENTS.md` (full hierarchy)           | 100%      |
| Files referenced from `AGENTS.md`      | ~90%      |
| `README.md` in working directory       | ~80%      |
| Nested READMEs in subdirectories       | ~40%      |
| Orphan docs in `_docs/` (unreferenced) | <10%      |

If it needs to be seen, it lives in `AGENTS.md` or is directly referenced from it.
