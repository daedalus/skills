# Effective AGENTS.md Patterns

Source: AuggieBench empirical study (Augment Code, Apr 2026).

---

## 1. Progressive Disclosure

Structure the file as a thin entry point with on-demand reference files.

```
module/
├── AGENTS.md          ← 100–150 lines max; entry point only
└── refs/
    ├── state.md       ← React Query vs Zustand decision rules
    ├── deploy.md      ← deployment workflow steps
    └── gotchas.md     ← domain-specific "don't/do" pairs
```

- Keep `AGENTS.md` under 150 lines. Gains reverse beyond that.
- Reference files are loaded in 90%+ of sessions when clearly pointed to.
- State *exactly* what each reference file contains so the agent knows when to open it.
- Mid-size modules (~100 core files) with 100–150 line entry + 2–5 refs showed 10–15% cross-metric gains.

---

## 2. Procedural Workflows (strongest single pattern)

Numbered multi-step workflows move agents from failing to finishing on the first attempt.
One 6-step deployment workflow: missing-wiring rate 40% → 10%, +25% correctness, +20% completeness.

```markdown
## Deploy a new integration

1. Run `./scripts/check-env.sh` — verify credentials and region.
2. Add service config to `config/integrations/<name>.yaml` (template: refs/deploy.md).
3. Register handler in `src/registry.ts` (search `// ADD NEW INTEGRATIONS HERE`).
4. Add wiring in `src/wiring/index.ts` — see pattern in refs/wiring.md.
5. Write integration test: `tests/integrations/<name>.test.ts`.
6. Run `npm run test:integrations` and confirm green.
```

Keep complex branching logic in a reference file, not inline.

---

## 3. Decision Tables

Force pattern/library choice before the agent writes code. +25% `best_practices` score
on ambiguous state-management tasks.

```markdown
## State management: React Query vs Zustand

| Condition                                 | React Query | Zustand |
|-------------------------------------------|:-----------:|:-------:|
| Server is the only data source            | ✅          |         |
| Multiple code paths mutate this state     |             | ✅      |
| Optimistic updates mixed with local state |             | ✅      |
| Cache invalidation / background refetch   | ✅          |         |
```

---

## 4. Real Codebase Examples (3–10 lines)

Short snippets from actual production code — not invented pseudocode.
+20% `code_reuse` from Redux Toolkit templates (createSlice, createAsyncThunk, typed useAppSelector).

- 3–5 examples max per topic
- Use copy-paste templates for high-frequency primitives
- More examples → agent pattern-matches on the wrong one

---

## 5. Pair Every "Don't" with a "Do"

```markdown
❌ Don't instantiate HTTP clients directly.
✅ Use `apiClient` from `lib/http` — retry middleware and auth headers included.
```

"Don't" alone → agent verifies each warning against the codebase before proceeding.
Files with 15+ sequential prohibitions and no alternatives consistently degrade output.

---

## 6. Domain-Specific Rules (specific and enforceable only)

```markdown
Use `Decimal` instead of `float` for all financial calculations.
```

Works when: rule is directly relevant, specific, and immediately actionable.
Fails when: stacked with dozens of others → see failure-modes.md.
