# Orthogonal Run: Cross-Skill Analysis

**Date**: 2026-07-23
**Scope**: 58 unique skills across 60 SKILL.md files
**Method**: Domain categorization → pairwise overlap/conflict/dependency analysis → trigger collision audit → gap analysis

---

## 1. Inventory

### 1.1 Skills by name (58 unique)

| # | Name | Directory | Lines | Domain |
|---|------|-----------|-------|--------|
| 1 | adhd-reasoning-mode | adhd/ | ~30 | Thinking methods |
| 2 | advanced-math | advanced-math/ | 331 | Research |
| 3 | agent-eval-no-ground-truth | agent-eval-no-ground-truth/ | 180 | AI eval |
| 4 | agentic-pbt | Agentic-Property-Based-Testing/ | ~100 | Code quality |
| 5 | agents-md | agents-md-improve/ | 91 | Meta |
| 6 | ai-code-detection | ai-code-detector/ | 195 | AI tools |
| 7 | ai-code-review | ai-code-review/ | 280 | Code quality |
| 8 | ai-vuln-harness | ai-vuln-harness/ | 90 | Security |
| 9 | alphaevolve | alpha-evolve/ | 663 | AI research |
| 10 | alphaproof-nexus | alphaproof-nexus/ | ~100 | AI research |
| 11 | approach-extractor | approach-extractor/ | 84 | Meta |
| 12 | auto-research-engineer | auto-research-engineer/ | 87 | AI eval |
| 13 | canon-tdd | test-driven-development/ | 134 | Code quality |
| 14 | caveman-speak | caveman/ | 146 | Utility |
| 15 | claude-essence | Claude-Sonet-4.6-essense/ | 141 | Reference |
| 16 | codex-security-adapter | codex-security-adapter/ | ~30 | Security |
| 17 | coding-agent-robustness | coding-agent-robustness/ | 306 | AI eval |
| 18 | context-eval | context-eval/ | 161 | AI eval |
| 19 | copy-fail-lpe-mitigation | copy-fail-reponse/ | 289 | Security |
| 20 | dogfood | dogfood/ | 162 | QA |
| 21 | dogfooding | dogfooding/ | 271 | AI eval |
| 22 | engineering-problem-solving | engineering-problem-solving/ | 176 | Thinking methods |
| 23 | failure-modes | failure-modes/ | ~100 | Thinking methods |
| 24 | fgts-naming-convention | fgts-naming-convention/ | 116 | Code quality |
| 25 | flinch-probe | flinch-probe/ | ~200 | AI eval |
| 26 | git-author-rewrite | git-author-rewrite/ | 85 | Utility |
| 27 | github-actions-security | github-actions-security-checklist/ | 306 | Security |
| 28 | hacker-mindset | The-hacker-mindset/ | ~100 | Thinking methods |
| 29 | hydronium-spec-driven-development | hydronium-spec-driven-development/ | 638 | Low-level |
| 30 | integer-sequence-research | OEIS/ | 1271 | Research |
| 31 | inverse-rubric-optimization | inverse-rubric-optimization/ | 544 | AI eval |
| 32 | InvestigativeTimelineAgent | InvestigativeTimelineAgent/ | 576 | Security |
| 33 | jsf-av-cpp-standards | jsf-av-cpp-standards/ | 69 | Low-level |
| 34 | karpathy-method | karpathy-method/ | 321 | Workflow |
| 35 | linux-security-audit | linux-security-audit/ | 768 | Security |
| 36 | llm-mirror-test | llm-mirror-test/ | 596 | AI eval |
| 37 | llm-qualia-assessment | QualiaAssesment/ | 514 | AI eval |
| 38 | matilda | matilda/ | 1975 | Security |
| 39 | meta-skill-creator | OpenAI-GPT-5.3-essence/ | 86 | Meta |
| 40 | narrative-systems-analysis | narrative-systems-analysis/ | 166 | Utility |
| 41 | os-bootstrap | os-bootstrap/ | 304 | Low-level |
| 42 | over-edit-measure | over-edit-measure/ | 145 | Code quality |
| 43 | page-cache-lpe-mitigation | dirty-frag/ AND copy-fail-dirty-frag-response/ | 489 each | Security |
| 44 | program-bench | program-bench/ | 411 | Low-level |
| 45 | python-perf-optimization | python-perf-optimization/ | 343 | Code quality |
| 46 | python-project-scaffold | python-project-scaffolding/ | 1541 | Code quality |
| 47 | quantum-discovery | quantum-discovery/ | 328 | AI research |
| 48 | redteaming-code | redteaming/ | 603 | Security |
| 49 | schema-harness | schema-harness/ | 110 | AI research |
| 50 | search-as-code | search-as-code/ | 463 | Research |
| 51 | semantic-correctness-auditor | semantic-correctness-auditor/ | 271 | Code quality |
| 52 | skill-creator | skill-creator/ | 470 | Meta |
| 53 | skill-from-post | skill-from-post/ | 301 | Meta |
| 54 | social-engineering-jailbreak | social-engineering-jailbreak/ | ~200 | Security |
| 55 | stack-smashing | StackSmashing/ | 427 | Low-level |
| 56 | test-case-reducer | test-reducer/ | 417 | Code quality |
| 57 | validate-before-ship | validate-before-ship/ | 93 | Code quality |
| 58 | InvestigativeTimelineAgent | InvestigativeTimelineAgent/ | 576 | Security |

### 1.2 Structural issues

| Issue | Details |
|-------|---------|
| **Duplicate skill** | `page-cache-lpe-mitigation` exists in 2 directories (`dirty-frag/` and `copy-fail-dirty-frag-response/`) — byte-identical copies |
| **Typo directory name** | `copy-fail-reponse/` should be `copy-fail-response/` (missing 's') |
| **Typo directory name** | `QualiaAssesment/` should be `QualiaAssessment/` (double s) |
| **Typo directory name** | `Claude-Sonet-4.6-essense/` should be `Claude-Sonet-4.6-essence/` |
| **Typo directory name** | `The-hacker-mindset/` vs all other dirs use lowercase convention |
| **Typo directory name** | `StackSmashing/` vs all other dirs use kebab-case |
| **Workspace artifact** | `git-author-rewrite-workspace/skill-snapshot/SKILL.md` has no proper frontmatter — not a live skill, but pollutes the skill tree |
| **Backup files** | `skills/engineering-problem-solving/SKILL (9).md` and `SKILL (10).md` are editor backup files left in the tree |

---

## 2. Overlap Clusters

### 2.1 CRITICAL: Exact duplicate

**`page-cache-lpe-mitigation`** × 2 paths:
- `skills/dirty-frag/SKILL.md`
- `skills/copy-fail-dirty-frag-response/SKILL.md`

Both are byte-identical (489 lines). One should be deleted and the other kept. The `copy-fail-dirty-frag-response/` directory name also collides with the separate `copy-fail-reponse/` (which has a different name: `copy-fail-lpe-mitigation`), creating confusion about which is which.

### 2.2 HIGH: Skill-creation overlap

**`meta-skill-creator`** (OpenAI-GPT-5.3-essence/) vs **`skill-creator`** vs **`skill-from-post`**

| Aspect | meta-skill-creator | skill-creator | skill-from-post |
|--------|-------------------|---------------|-----------------|
| Trigger | "make this reusable" | "create a skill" | "turn this post into a skill" |
| Workflow | Design → refine → evolve | Create → edit → measure → optimize | Extract → draft → dogfood → patch |
| Dogfooding | Not mentioned | Not mentioned | Explicit (2–6 rounds) |
| Eval | Not mentioned | Variance analysis, benchmarking | Not mentioned |

All three do substantially the same thing (create a SKILL.md) with different entry points. A user saying "make this into a skill" could trigger any of them, and the resulting output would differ. **Recommendation**: consolidate into a single skill (perhaps `skill-from-post` as the most battle-tested variant) with `skill-creator` as an alias/entry point, and retire `meta-skill-creator`.

### 2.3 HIGH: Linux kernel LPE family

Three skills covering nearly identical ground:

- **`page-cache-lpe-mitigation`** (×2 copies): Covers Dirty Pipe → Copy Fail → Dirty Frag page-cache-poison LPE family
- **`copy-fail-lpe-mitigation`** (in `copy-fail-reponse/`): Same threat (CVE-2026-31431, AF_ALG, algif_aead, bpf-lsm)

These three represent a single skill concept with inconsistent naming. The two `page-cache-lpe-mitigation` copies are identical; `copy-fail-lpe-mitigation` has different content (289 lines) but the same domain. **Recommendation**: Consolidate into one skill under `page-cache-lpe-mitigation` (the name in the live system prompt), delete the duplicate, and migrate `copy-fail-lpe-mitigation` content into it.

### 2.4 MEDIUM: Security testing/adversarial cluster

| Skill | Focus | Trigger phrase risk |
|-------|-------|---------------------|
| ai-vuln-harness | Multi-agent vuln research pipelines | "scan for vulns" |
| redteaming-code | Red-teaming code + AI systems | "red team this" |
| hacker-mindset | General adversarial thinking | "think like a hacker" |
| social-engineering-jailbreak | Social engineering on LLMs | "jailbreak this" |
| coding-agent-robustness | Stress-test coding agents | "test my agent's security" |
| codex-security-adapter | Route security intent to plugin files | "security task" |

These are largely complementary (different layers of the stack) but overlap at the edges:
- `ai-vuln-harness` vs `redteaming-code`: both involve adversarial testing of AI systems. `ai-vuln-harness` focuses on building multi-agent *pipelines*; `redteaming-code` covers both traditional code security *and* AI-specific testing. A request to "find vulnerabilities in my agent" would ambiguity-trigger both.
- `hacker-mindset` is a *thinking methodology* that could precede any of the others — it's not really an overlap, more a dependency.

### 2.5 MEDIUM: LLM evaluation cluster

| Skill | What it measures | Distinct enough? |
|-------|------------------|-----------------|
| agent-eval-no-ground-truth | Agent correctness without labels | ✅ Yes |
| coding-agent-robustness | Agent reliability under stress | ✅ Yes (stress, not correctness) |
| context-eval | Context management strategies | ✅ Yes (technical, not behavioral) |
| flinch-probe | Token suppression probability | ✅ Yes (specific metric) |
| inverse-rubric-optimization | Black-box rubric recovery | ✅ Yes (specific methodology) |
| llm-mirror-test | Self-recognition / anomaly detection | ✅ Yes (specific experiment) |
| llm-qualia-assessment | Phenomenal experience / qualia | ⚠️ Overlaps with flinch-probe at edges (both probe internal state) |

**Trigger collision**: "evaluate this model" could hit 4+ of these. The descriptions are specific enough that a well-tuned agent would pick the right one, but a vague request would be ambiguous.

### 2.6 MEDIUM: Code review + testing cluster

| Skill | Stage | Distinct? |
|-------|-------|-----------|
| ai-code-review | Review diffs/PRs | ✅ |
| canon-tdd | Write tests first | ✅ |
| agentic-pbt | Fuzz with Hypothesis | ✅ |
| test-case-reducer | Minimize failing inputs | ✅ |
| validate-before-ship | Gate before merging | ✅ |
| over-edit-measure | Post-hoc diff analysis | ✅ |
| semantic-correctness-auditor | Meta: are tests enough? | ⚠️ Overlaps with validate-before-ship |

`semantic-correctness-auditor` and `validate-before-ship` both answer "is this code correct enough to ship?" — the former through Rice's Theorem analysis, the latter through empirical validation. A request like "is this ready to merge" could trigger both, and they'd give different answers.

### 2.7 LOW: Problem-solving methods

| Skill | Approach | Distinct? |
|-------|----------|-----------|
| engineering-problem-solving | Falsification-first methodology | ✅ |
| failure-modes | Systematic failure enumeration | ✅ (subset of EPS's hypothesis stage) |
| approach-extractor | Post-hoc learnings capture | ✅ (EPS's §7 rendered as standalone) |
| adhd-reasoning-mode | Associative/creative exploration | 🔄 Opposite of EPS's rigor |

`engineering-problem-solving` and `adhd-reasoning-mode` are almost philosophical opposites: one demands falsification and rigor, the other demands free association and curiosity-driven jumps. They should never both fire on the same task. The triggers are distinct ("stuck on a hard problem" → EPS; "be creative" / "think outside the box" → ADHD mode).

`failure-modes` is essentially a subset of `engineering-problem-solving`'s hypothesis stage (§2 Generate hypotheses → §3 Actively seek counterexamples). It has value as a standalone targeted skill but overlaps heavily with EPS when EPS is fully applied.

---

## 3. Natural Pipelines (Dependency Chains)

These are skills whose output naturally feeds into another. Unlike overlaps, these are *good* things to document.

### 3.1 Research → Discovery → Report

```
search-as-code (gather sources)
  → integer-sequence-research (analyze sequence)
    → advanced-math (prove properties)
```

### 3.2 Security investigation → Analysis → Capture

```
redteaming-code (find vulns)
  → hacker-mindset (think adversarially about impact)
    → failure-modes (classify what can go wrong)
      → approach-extractor (capture learnings)
```

Or the kernel-LPE variant:
```
page-cache-lpe-mitigation (respond to incident)
  → InvestigativeTimelineAgent (trace telemetry)
    → approach-extractor (capture incident lessons)
```

### 3.3 Build → Test → Ship

```
karpathy-method (spec the system)
  → canon-tdd (write tests first)
    → agentic-pbt (fuzz the logic)
      → validate-before-ship (gate the merge)
        → over-edit-measure (audit the diff)
```

Or the Python-specific variant:
```
python-project-scaffold (create project)
  → python-perf-optimization (profile + optimize)
    → agentic-pbt (fuzz for correctness)
      → semantic-correctness-auditor (are we done?)
```

### 3.4 Skill creation pipeline

```
skill-from-post (draft a skill from source material)
  → skill-creator (benchmark + refine)
    → agents-md (integrate into agent instructions)
      → dogfooding (self-test the result)
```

### 3.5 Debug → Solve → Capture

```
engineering-problem-solving (solve the bug)
  → approach-extractor (extract why that approach worked)
```

### 3.6 Low-level development

```
os-bootstrap (scaffold kernel)
  → jsf-av-cpp-standards (ensure safety-critical compliance)
  → stack-smashing (understand exploit surface)
  → program-bench (reconstruct any reference binaries)
```

---

## 4. Trigger Collision Matrix

Situations where multiple skills could reasonably fire on the same user request.

| User says | Skills that could trigger | Verdict |
|-----------|--------------------------|---------|
| "make a skill for X" | meta-skill-creator, skill-creator, skill-from-post | 🔴 Ambiguous — 3 different approaches |
| "evaluate my LLM agent" | agent-eval-no-ground-truth, coding-agent-robustness, inverse-rubric-optimization | 🟡 Depends on what "evaluate" means |
| "find bugs in this code" | agentic-pbt, test-case-reducer, failure-modes, ai-code-review | 🟡 Different stages of bug-finding |
| "is this correct" | validate-before-ship, semantic-correctness-auditor | 🟡 Overlapping answers |
| "red team this" | redteaming-code, ai-vuln-harness, hacker-mindset | 🟡 Broad trigger |
| "Linux kernel exploit" | page-cache-lpe-mitigation (×2), copy-fail-lpe-mitigation, stack-smashing | 🔴 Ambiguous which LPE skill |
| "test my app" | canon-tdd, dogfooding, dogfood, agentic-pbt | 🟡 Different test types |
| "optimize this" | auto-research-engineer, alphaevolve, python-perf-optimization | 🟡 Python vs general vs search |
| "paper about sequences" | integer-sequence-research, advanced-math, search-as-code | 🟡 Research vs. discovery vs. analysis |
| "prove this theorem" | alphaproof-nexus, advanced-math, integer-sequence-research | 🟡 Different proof methods |

**Key risks**:
1. 🔴 Skill-creation triple triggers every time someone says "skill"
2. 🔴 LPE triple triggers every time someone mentions Linux kernel exploits
3. 🟡 "Evaluate" is dangerously overloaded across 3+ distinct eval skills
4. 🟡 "Test" is overloaded across unit testing, fuzzing, and dogfooding

---

## 5. Contradictions & Conflicts

### 5.1 Communication style

| Skill A | Skill B | Conflict |
|---------|---------|----------|
| `caveman-speak` (minimal tokens, primitive speech) | `engineering-problem-solving` (thorough, documented reasoning) | **Direct contradiction** — EPS demands detailed logs and rationale; caveman strips all nuance |
| `adhd-reasoning-mode` (free association, wide search) | `engineering-problem-solving` (falsification, converge first) | **Methodological opposite** — one diverges, the other converges. Using both would produce whiplash |

### 5.2 Process tempo

| Skill A | Skill B | Conflict |
|---------|---------|----------|
| `auto-research-engineer` (fast keep/revert loops) | `validate-before-ship` (demands proof before shipping) | **Process conflict** — ARE wants rapid iteration; VBS demands you never merge untested math. They could coexist if ARE's loop is understood as "research, not merge." |
| `alpha-evolve` (search for better algorithm) | `validate-before-ship` (gate new algorithms) | **Complementary, not conflicting** — evolve generates candidates, VBS gates them. But if VBS fires mid-evolution, it would block progress. Scope matters. |

### 5.3 Scope overlap (likely benign)

| Skill A | Skill B | Relationship |
|---------|---------|-------------|
| `dogfood` (web app QA) | `dogfooding` (self-testing LLM systems) | Names are confusingly similar but domains differ. Risk: "dogfood this" triggers both for a web app, one irrelevant. |
| `intelligence` (InvestigativeTimelineAgent) | `hacker-mindset` | Both involve investigation but at different levels (telemetry vs. general adversarial thinking) |

---

## 6. Gaps

Domains or tasks not covered by any existing skill:

| Missing capability | Notes | Priority |
|--------------------|-------|----------|
| **Frontend/web development** | Building React/Vue/etc. apps, HTML/CSS, design implementation | HIGH — large gap |
| **API design & development** | REST, GraphQL, gRPC API design patterns | HIGH |
| **Database/SQL** | Schema design, query optimization, migrations | HIGH |
| **Refactoring** | Systematic code restructuring without changing behavior | MEDIUM |
| **Documentation writing** | Writing READMEs, API docs, internal docs | MEDIUM |
| **Performance (non-Python)** | General perf optimization (JS, Go, Rust) | MEDIUM |
| **DevOps / CI/CD (general)** | Not just GitHub Actions security, but actual deployment pipelines | MEDIUM |
| **Testing (general)** | Integration tests, e2e tests, mocking strategies | MEDIUM |
| **Containerization** | Docker, Docker Compose, Kubernetes | MEDIUM |
| **Code generation** | Scaffolding APIs, models, SDKs from specs | LOW |
| **Accessibility** | a11y standards, screen reader support | LOW |
| **Internationalization** | i18n, localization workflows | LOW |

Note: `python-perf-optimization` (just added) partially fills the "performance" gap but only for Python. `python-project-scaffold` fills the "scaffolding" gap but only for Python.

---

## 7. Recommendations

### 7.1 Immediate (structural fixes)

1. **Delete duplicate**: Remove one copy of `page-cache-lpe-mitigation` — keep `dirty-frag/` (shorter name), remove `copy-fail-dirty-frag-response/`
2. **Rename typos**: Fix `copy-fail-reponse/` → `copy-fail-response/`, `QualiaAssesment/` → `QualiaAssessment/`, `Claude-Sonet-4.6-essense/` → `Claude-Sonet-4.6-essence/`
3. **Clean up artifacts**: Delete `git-author-rewrite-workspace/`, `skills/engineering-problem-solving/SKILL (9).md`, `SKILL (10).md`
4. **Rename for consistency**: `StackSmashing/` → `stack-smashing/`, `The-hacker-mindset/` → `hacker-mindset/`

### 7.2 Short-term (consolidations)

5. **Consolidate skill-creation**: Merge `meta-skill-creator` into `skill-creator` (or `skill-from-post` as the better-tested variant). The 3-entry-point situation will keep causing ambiguous triggers.
6. **Consolidate LPE skills**: Merge `copy-fail-lpe-mitigation` content into `page-cache-lpe-mitigation` and delete the separate skill. Delete the duplicate `page-cache-lpe-mitigation` copy.
7. **Clarify scope boundaries**: Add DISAMBIGUATION notes to:
   - `auto-research-engineer` (vs. `alphaevolve`)
   - `dogfood` (vs. `dogfooding`)
   - `engineering-problem-solving` (vs. `failure-modes`)

### 7.3 Medium-term (new skills)

8. **Consider adding**: Frontend development, API design, database/SQL, general performance optimization, refactoring

### 7.4 Pipeline documentation

9. **Document preferred chains** (either in a PIPELINES.md or as `see-also` in skill frontmatter):
   - Security: `hacker-mindset → redteaming-code → failure-modes → approach-extractor`
   - Development: `canon-tdd → agentic-pbt → validate-before-ship`
   - Research: `search-as-code → integer-sequence-research → advanced-math`
   - Skill ops: `skill-from-post → skill-creator → dogfooding`

---

## 8. Summary Statistics

| Metric | Count |
|--------|-------|
| Total SKILL.md files | 60 |
| Unique skill names | 58 |
| Exact byte-identical duplicates | 1 pair (page-cache-lpe-mitigation) |
| Directory name typos | 4 |
| Orphan workspace artifacts | 1 |
| Editor backup files | 2 |
| HIGH overlap clusters | 3 (skill-creation, LPE response, problem-solving) |
| MEDIUM overlap clusters | 2 (security testing, code review/testing) |
| Direct contradictions | 2 (caveman↔EPS, adhd↔EPS) |
| 🔴 Trigger collisions | 3 |
| 🟡 Trigger collisions | 7 |
| Identified gaps | 6 HIGH, 3 MEDIUM, 3 LOW |
