# Orthogonal Run: Skills Cross-Analysis

**Date**: 2026-07-23
**Method**: Subagent-executed — 8 parallel subagents each read 5–10 skills fully, then applied meta-skills (failure-modes, engineering-problem-solving, semantic-correctness-auditor) and performed within-cluster pairwise analysis against all 58 skills.

---

## 1. Inventory & Structural Issues

### 1.1 Skills by cluster (58 unique)

| Cluster | Skills (count) |
|---------|----------------|
| **Offensive Security** | ai-vuln-harness, redteaming-code, hacker-mindset, social-engineering-jailbreak, matilda, stack-smashing, codex-security-adapter (7) |
| **Defensive Security** | linux-security-audit, github-actions-security, page-cache-lpe-mitigation (×2), copy-fail-lpe-mitigation, InvestigativeTimelineAgent, jsf-av-cpp-standards, hydronium-spec-driven-development (8) |
| **AI Evaluation** | agent-eval-no-ground-truth, coding-agent-robustness, context-eval, flinch-probe, inverse-rubric-optimization, llm-mirror-test, llm-qualia-assessment, dogfooding (8) |
| **Code Quality** | ai-code-review, canon-tdd, agentic-pbt, test-case-reducer, validate-before-ship, over-edit-measure, semantic-correctness-auditor, python-perf-optimization (8) |
| **Meta & Creation** | skill-creator, skill-from-post, meta-skill-creator, agents-md, karpathy-method, fgts-naming-convention (6) |
| **Thinking Methods** | engineering-problem-solving, failure-modes, approach-extractor, adhd-reasoning-mode, caveman-speak (5) |
| **Research & Math** | advanced-math, integer-sequence-research, search-as-code, schema-harness, quantum-discovery, alphaproof-nexus (6) |
| **Infrastructure & Misc** | os-bootstrap, program-bench, python-project-scaffold, claude-essence, ai-code-detection, dogfood, git-author-rewrite, narrative-systems-analysis, alphaevolve, auto-research-engineer (10) |

### 1.2 Structural defects

| Issue | Details |
|-------|---------|
| **Exact duplicate** | `page-cache-lpe-mitigation` in `dirty-frag/` and `copy-fail-dirty-frag-response/` — byte-identical (MD5 match) |
| **Directory typos** | `QualiaAssesment/`, `Claude-Sonet-4.6-essense/`, `copy-fail-reponse/`, `The-hacker-mindset/`, `StackSmashing/` |
| **Workspace artifact** | `git-author-rewrite-workspace/skill-snapshot/SKILL.md` — no frontmatter, not a live skill |
| **Editor backups** | `SKILL (9).md`, `SKILL (10).md` in engineering-problem-solving/ |

---

## 2. Meta-Skill Evaluation Results (Subagent-Executed)

Each skill was evaluated on three dimensions by the subagent that read its full content. Scores are 1–5.

### 2.1 Falsification-first score distribution (engineering-problem-solving applied to each skill)

| Score | Skills |
|-------|--------|
| **5/5** | integer-sequence-research, test-case-reducer, over-edit-measure, validate-before-ship, python-perf-optimization, page-cache-lpe-mitigation, copy-fail-lpe-mitigation, program-bench |
| **4/5** | hacker-mindset, matilda, github-actions-security, flinch-probe, inverse-rubric-optimization, llm-mirror-test, skill-from-post, coding-agent-robustness, dogfooding, canon-tdd, agentic-pbt, engineering-problem-solving, schema-harness, ai-code-detection, alphaevolve, auto-research-engineer |
| **3/5** | ai-vuln-harness, social-engineering-jailbreak, stack-smashing, InvestigativeTimelineAgent, hydronium-spec-driven-development, linux-security-audit, agent-eval-no-ground-truth, alphaproof-nexus, quantum-discovery, skill-creator, agents-md, karpathy-method, ai-code-review, python-project-scaffold, failure-modes, adhd-reasoning-mode |
| **2/5** | redteaming-code, jsf-av-cpp-standards, context-eval, llm-qualia-assessment, semantic-correctness-auditor, os-bootstrap, dogfood, narrative-systems-analysis, advanced-math, search-as-code, fgts-naming-convention |
| **1/5** | codex-security-adapter, meta-skill-creator, claude-essence, git-author-rewrite, caveman-speak |

### 2.2 Skills ordered by verifiability (semantic-correctness-auditor assessment)

| Verifiability | Skills |
|---------------|--------|
| **High** | page-cache-lpe-mitigation, copy-fail-lpe-mitigation, github-actions-security, InvestigativeTimelineAgent, hydronium-spec-driven-development, matilda, stack-smashing, integer-sequence-research, schema-harness, test-case-reducer, over-edit-measure, validate-before-ship, python-perf-optimization, program-bench, fgts-naming-convention, coding-agent-robustness, inverse-rubric-optimization, llm-mirror-test, flinch-probe, agentic-pbt, context-eval, dogfooding, alphaevolve, auto-research-engineer, git-author-rewrite, alphaproof-nexus (Lean proofs), quantum-discovery (simulation) |
| **Medium** | linux-security-audit, jsf-av-cpp-standards, ai-code-review, codex-security-adapter, ai-vuln-harness, redteaming-code, copy-fail-lpe-mitigation, agent-eval-no-ground-truth, semantic-correctness-auditor, python-project-scaffold, os-bootstrap, dogfood, search-as-code, ai-code-detection |
| **Low/None** | hacker-mindset, social-engineering-jailbreak, advanced-math, llm-qualia-assessment, adhd-reasoning-mode, caveman-speak, approach-extractor, failure-modes, engineering-problem-solving, skill-creator, skill-from-post, meta-skill-creator, agents-md, karpathy-method, claude-essence, narrative-systems-analysis, matilda (intermediate reasoning quality) |

### 2.3 Top failure modes per cluster (from failure-modes skill applied to each)

**Offensive Security**: Self-contamination (ai-vuln-harness), false positive flood (redteaming-code), containment escape (matilda), outdated mitigation assumptions (stack-smashing)

**Defensive Security**: Distro-specific command failures (linux-security-audit), SHA pinning rot (github-actions-security), BPF-LSM kernel dependency (LPE skills), semantic hallucination (InvestigativeTimelineAgent), C++98 frozen standard (jsf-av-cpp-standards), clock-frequency cascade error (hydronium-spec-driven-development)

**AI Evaluation**: False precision (agent-eval-no-ground-truth), probe quality dependency (coding-agent-robustness), model-dependent results (context-eval), scale conflation (flinch-probe), prior knowledge leakage (inverse-rubric-optimization), confirmation bias amplifier (llm-mirror-test), phenomenal attribution by prose quality (llm-qualia-assessment), spec hallucination (dogfooding)

**Code Quality**: False positive avalanche (ai-code-review), missing test list (canon-tdd), speculative property generation (agentic-pbt), over-reduction by weak interestingness (test-case-reducer), self-exemption paradox (semantic-correctness-auditor), profiling-first skipped (python-perf-optimization), sanity-check never written (validate-before-ship), Python-only limitation (over-edit-measure)

**Meta & Creation**: Over-engineering trivial skills (skill-creator), novelty assessment unreliability (skill-from-post), no verification infrastructure (meta-skill-creator), empirical patterns may not generalize (agents-md), heavyweight for simple requests (karpathy-method), abbreviation rot (fgts-naming-convention)

**Thinking Methods**: False exhaustiveness (failure-modes), EPS makes no falsifiable effectiveness claim (engineering-problem-solving), depends on reasoning quality (approach-extractor), can produce non-convergence (adhd-reasoning-mode), destroys nuance (caveman-speak)

**Research & Math**: Ghost citations (advanced-math), dual-implementation disagreement (integer-sequence-research), simulated search passed as real (search-as-code), epicycle accumulation (schema-harness), hardware queue optimism (quantum-discovery), circular "sorry" (alphaproof-nexus)

**Infrastructure & Misc**: Over-commitment to canonical layout (os-bootstrap), undiscoverable behaviors (program-bench), template rot (python-project-scaffold), untestable claims (claude-essence), style signal decay (ai-code-detection), visual-only blind spot (dogfood), irreversible destruction (git-author-rewrite), confirmation bias (narrative-systems-analysis), evaluator misalignment (alphaevolve), local optimum trap (auto-research-engineer)

---

## 3. Critical Overlap Clusters

### 3.1 🔴 CRITICAL: page-cache-lpe-mitigation — exact duplicate
- Identical files in `dirty-frag/` and `copy-fail-dirty-frag-response/` (489 lines each, same MD5)
- `copy-fail-lpe-mitigation` (in `copy-fail-reponse/`) covers Copy Fail only; the duplicated skill is a strict superset (Copy Fail + Dirty Frag + Dirty Pipe)
- Subagent verdict: **Consolidate into one kept skill; delete both copies of the duplicate; merge copy-fail-lpe-mitigation into it**

### 3.2 🔴 CRITICAL: meta-skill-creator dominated by skill-creator + skill-from-post

Subagent pairwise analysis:

| Pair | Overlap | Conflict | Verdict |
|------|---------|----------|---------|
| meta-skill-creator ↔ skill-creator | HIGH | SIGNIFICANT (quality gap) | meta-skill-creator should be retired |
| skill-creator ↔ skill-from-post | MODERATE | LOW (different inputs) | STRONG pipeline: extract→evaluate |
| meta-skill-creator ↔ skill-from-post | HIGH | SIGNIFICANT (quality gap) | skill-from-post dominates |

**Falsification gradient**: skill-from-post (4/5) > skill-creator (3/5) > meta-skill-creator (1/5)

**Subagent verdict**: meta-skill-creator has zero falsification mechanism, no verification infrastructure, and at 87 lines is a philosophy statement, not an actionable workflow. Retire it. Keep skill-creator and skill-from-post as a two-stage pipeline (skill-from-post extracts drafts → skill-creator evaluates and hardens).

### 3.3 🟡 HIGH: Offensive × Defensive security trigger collisions

Subagent finding: `redteaming-code` and `ai-vuln-harness` overlap at HIGH level — both involve adversarial testing of AI systems with different automation levels. `hacker-mindset` is the falsification-strongest (4/5 EPS score) and is the universal prerequisite for all security skills, but has no verification requirement.

Key cross-pair discovered by subagent:
- `redteaming-code` social engineering section (~30 lines) is a shallow subset of `social-engineering-jailbreak` (~196 lines) — trigger collision hazard for "red team my LLM" queries.
- `stack-smashing` techniques are what `matilda`'s §2c exploits operationalize at scale — undocumented dependency.
- `ai-vuln-harness` and `matilda` share a reasoning-graph architecture (Plan→Judge→Action→Summary) with `schema-harness` — this pattern is reusable across agentic skills.

### 3.4 🟡 HIGH: integer-sequence-research × alphaproof-nexus

**Strongest pipeline found**: integer-sequence-research (5/5 falsification) generates candidate sequences with confidence scoring → alphaproof-nexus formalizes in Lean.

But **philosophical conflict** on "proved":
- integer-sequence-research: 90-100 confidence = "OEIS-ready" = no counterexample found empirically
- alphaproof-nexus: proved = Lean `sorry`-free machine-checked proof
- If both fire, agent could claim "proved" when only empirically verified

Subagent verdict: **Both should fire on OEIS conjecture queries** — integer-sequence-research for empirical falsification, alphaproof-nexus for formal verification. The agent should run both and report at both confidence levels.

### 3.5 🟡 HIGH: engineering-problem-solving × adhd-reasoning-mode

Subagent finding: **Phase complements, not philosophical opposites.**

| Dimension | EPS | ADHD |
|-----------|-----|------|
| Primary phase | Convergence-first | Divergence-first |
| Core filter | Falsifiability | Novelty |
| Hypothesis count | 2-3 competing | 3-5 parallel streams |
| Stopping rule | Explicit (§6) | Convergence protocol |
| **EPS self-score** | **4/5** — fails own effectiveness claim | N/A |

The real map: ADHD for problem *discovery/framing* → EPS for problem *solving/verification*. Using ADHD to solve or EPS to discover would both fail.

### 3.6 🟡 MEDIUM: Code Quality pipeline discovered

Subagent found a natural 5-stage pipeline across the code quality cluster:

```
canon-tdd (write tests first)
  → agentic-pbt (fuzz the invariants)
    → ai-code-review (review the diff)
      → validate-before-ship (gate the merge)
        → over-edit-measure (audit minimality)
```

With `semantic-correctness-auditor` as a meta-layer that audits the whole pipeline.

### 3.7 🟡 MEDIUM: AI Evaluation overlap cluster

Subagent EPS scores range 2–5 across the cluster — widest spread found:

- coding-agent-robustness (5/5) — the falsification champion: adversarially probes, tracks regression, measures numerically
- context-eval (2/5) — simple A/B comparison, no falsification, no adversarial orientation
- llm-mirror-test ↔ llm-qualia-assessment: MAJOR conflict despite MEDIUM overlap — same subject (model's relationship to own outputs), incompatible epistemologies (falsificationist vs. additive/philosophical)

---

## 4. Pipeline Atlas (Subagent-Identified Chains)

### 4.1 Research pipeline
```
search-as-code (gather sources)
  → integer-sequence-research (empirical discovery + falsification) [5/5 EPS]
    → alphaproof-nexus (Lean formal verification)
```

### 4.2 Security pipeline
```
hacker-mindset (adversarial thinking methodology) [4/5 EPS]
  → redteaming-code (find vulnerabilities systematically) [2/5]
    → ai-vuln-harness (scale with multi-agent pipeline) [3/5]
      → InvestigativeTimelineAgent (trace telemetry) [3/5]
        → approach-extractor (capture learnings)
```

### 4.3 Development pipeline
```
python-project-scaffold (project bootstrap) [3/5] — the cluster hub (7/9 incoming connections)
  → python-perf-optimization (profile + optimize) [5/5]
    → canon-tdd (TDD loop) [4/5]
      → agentic-pbt (property-based fuzzing) [4/5]
        → validate-before-ship (empirical gate) [5/5]
```

### 4.4 Skill creation pipeline
```
skill-from-post (draft from source material) [4/5]
  → skill-creator (eval + harden) [3/5]
    → agents-md (integrate into agent instructions) [3/5]
      → dogfooding (self-test result) [4/5]
```

### 4.5 Problem-solving pipeline
```
adhd-reasoning-mode (divergent exploration) [3/5]
  → engineering-problem-solving (falsification convergence) [4/5]
    → failure-modes (systematic audit) [3/5]
      → approach-extractor (capture generalizable principle)
```

### 4.6 Binary reconstruction pipeline
```
stack-smashing (understand exploit mechanics)
  → program-bench (reconstruct binary behavior) [5/5]
    → os-bootstrap (scaffold kernel using observed structure) [2/5]
```

---

## 5. Trigger Collision Matrix (Subagent Assessment)

| User says | Skills that could trigger | Subagent verdict |
|-----------|--------------------------|------------------|
| "make a skill for X" | meta-skill-creator, skill-creator, skill-from-post | 🔴 3-way — retire meta-skill-creator |
| "Linux kernel exploit" | page-cache-lpe-mitigation (×2), copy-fail-lpe-mitigation, stack-smashing | 🔴 4-way — consolidate LPE skills |
| "evaluate my LLM agent" | agent-eval-no-ground-truth, coding-agent-robustness, inverse-rubric-optimization | 🟡 3-way — CAR should win (most specific, actionable) |
| "prove this theorem" | alphaproof-nexus, advanced-math, integer-sequence-research | 🟡 3-way — advanced-math's over-trigger policy is a problem; deprioritize when formal proof is requested |
| "find bugs in this code" | agentic-pbt, test-case-reducer, failure-modes, ai-code-review | 🟡 4-way — different stages; should chain not compete |
| "optimize this algorithm" | alphaevolve, auto-research-engineer, python-perf-optimization | 🟡 alphaevolve wins for algorithmic search; ARE for simpler assets |
| "test my app" | canon-tdd, dogfooding, dogfood, agentic-pbt | 🟡 Different test types — specify unit vs. QA vs. fuzz |
| "what am I missing" | engineering-problem-solving, adhd-reasoning-mode, failure-modes | 🟡 3-way tie — needs disambiguation by symptom presence |
| "think outside the box" | adhd-reasoning-mode, hacker-mindset | 🟢 Complement (ADHD for creativity, hacker-mindset for adversarial) |
| "review this PR" | ai-code-review, validate-before-ship, over-edit-measure | 🟢 Should chain: review → validate → measure |
| "is this correct" | validate-before-ship, semantic-correctness-auditor | 🟡 Overlapping answers — VBS for empirical, SCA for theoretical limits |

---

## 6. Contradictions & Conflicts

### 6.1 Methodology conflicts

| Skill A | Skill B | Nature | Severity |
|---------|---------|--------|----------|
| EPS [4/5] | caveman-speak [1/5] | EPS requires calibrated confidence language; caveman strips all nuance | **HIGH** — caveman should never be applied to EPS reasoning traces |
| EPS [4/5] | adhd-reasoning-mode [3/5] | EPS converges via falsification; ADHD diverges via curiosity | **MEDIUM** — phase complements, not true opposites; sequence ADHD→EPS |
| LMT (mirror-test) [4/5] | LQA (qualia) [2/5] | LMT is falsificationist; LQA is additive/philosophical | **HIGH** — incompatible epistemologies on same subject |
| agentic-pbt [4/5] | canon-tdd [4/5] | PBT's random exploration doesn't fit TDD's "one test at a time" model | **MEDIUM** — PBT after code exists, TDD during construction |
| program-bench [5/5] | python-project-scaffold [3/5] | Program-bench: test-first (from binary observation). Scaffold: spec-first (then tests) | **MEDIUM** — opposite test generation strategies; resolve by using program-bench's tests as ground truth |

### 6.2 Naming conflicts

| Symptom | Cause |
|---------|-------|
| `dogfood` vs `dogfooding` | Names are confusingly similar but domains differ (web QA vs LLM self-testing) |
| `page-cache-lpe-mitigation` × 2 + `copy-fail-lpe-mitigation` | Three skills, two names, one exact duplicate |
| `meta-skill-creator` vs `skill-creator` vs `skill-from-post` | Three skills, all about creating skills |

---

## 7. Verified Strongest Pipelines

Subagents ranked these as the highest-value cross-skill compositions:

1. **integer-sequence-research → alphaproof-nexus**: Empirical discovery → formal verification. The strongest methodological pipeline in the entire collection. Bridges falsification-first (5/5) and mechanical verification (Lean).

2. **python-project-scaffold → 7 downstream skills**: The infrastructure cluster hub. Every development workflow starts here. No other skill has 7/9 incoming pipeline connections.

3. **search-as-code → integer-sequence-research → advanced-math**: Gather sources → discover sequences → prove properties. Full research workflow.

4. **hacker-mindset → redteaming-code → ai-vuln-harness**: Adversarial method → systematic attack → scaled automation. Covers thinking through execution.

5. **canon-tdd → agentic-pbt → validate-before-ship**: Test-driven construction → fuzz invariants → gate before merging. Production-grade quality pipeline.

6. **skill-from-post → skill-creator → dogfooding**: Draft → harden → self-test. Complete skill lifecycle.

7. **adhd-reasoning-mode → engineering-problem-solving → approach-extractor**: Explore → verify → capture. Learning lifecycle from discovery to durable knowledge.

---

## 8. Gaps (Identified by Meta-Skills Applied to the Collection)

### 8.1 Missing skills (subagent-identified)

| Missing capability | Identified by | Priority |
|--------------------|---------------|----------|
| **Skill auditor / skill reviewer** | skill-creator / agents-md subagent | HIGH — no independent review of skills exists |
| **Database/SQL design** | Infra cluster subagent | HIGH |
| **Container/Docker/K8s** | Infra cluster subagent | HIGH |
| **CI/CD pipeline design (general)** | Infra cluster subagent | MEDIUM |
| **AGENTS.md linter** | agents-md subagent | MEDIUM |
| **Observability (metrics/logs/tracing)** | Infra cluster subagent | MEDIUM |
| **General performance optimization** | Misc cluster subagent | MEDIUM (perf currently Python-only) |
| **Frontend/web development** | Implicit from code quality cluster gaps | MEDIUM |
| **Secrets management** | Infra cluster subagent | MEDIUM |
| **API design** | Cross-cluster analysis | MEDIUM |
| **Workflow-to-skill quick capture** | Meta cluster subagent — bridge missing between "here's my workflow" and SKILL.md | MEDIUM |
| **Skill merger** | Meta cluster subagent — no workflow to deduplicate overlapping skills | LOW |
| **Meta-skill governance** | Meta cluster subagent — no skill audits the meta-skill collection | LOW |

### 8.2 What no skill does

- **No skill falsifies its own effectiveness claim** (EPS comes closest but scores 4/5 because it doesn't test its own value proposition)
- **No skill checks for self-consistency** — semantic-correctness-auditor identifies this as the largest cross-cutting gap
- **No skill validates pipeline integration** — integer-sequence-research→alphaproof-nexus is the strongest pipeline in the collection, but no skill tests that data flows correctly between them
- **No skill provides a cross-skill dependency map** — this ORTHOGONAL_RUN.md is the first

---

## 9. Per-Skill Falsification & Verifiability Detail

### 9.1 Top 5 most falsification-complete skills (EPS score 5/5)

| Skill | What makes it 5/5 |
|-------|-------------------|
| **integer-sequence-research** | "Treat every formula as guilty until proven robust." Dual implementations, §4 adversarial falsification with weak zones + delta debugging + mutation attack, 8 documented failure modes, 3 dogfood runs |
| **test-case-reducer** | ddmin algorithm is provably correct given a correct oracle. Binary verifiability: each candidate either triggers the interestingness test or doesn't |
| **over-edit-measure** | Levenshtein distance + Cognitive Complexity are purely mechanical. AST parser + algorithm produce deterministic output |
| **validate-before-ship** | Every step produces a falsifiable artifact. Guards against "it's mathematically correct" as justification |
| **program-bench** | Tests BEFORE implementation. Dummy-binary validation ensures tests can fail. Pass rate is the single objective measure |

### 9.2 Bottom 5 least falsifiable skills (EPS score 1–2/5)

| Skill | What holds it back |
|-------|---------------------|
| **meta-skill-creator** | No falsification mechanism. No verification. "Simulate execution" is hand-wavy. Pure philosophy |
| **claude-essence** | Zero testable claims. Untestable interior-state claims ("genuine curiosity"). Admits it doesn't change behavior |
| **caveman-speak** | Stylistic utility — falsification is inapplicable as a dimension |
| **git-author-rewrite** | Purely operational command sequence. No hypothesis testing |
| **codex-security-adapter** | Router/map, not methodology. No falsification elements |

---

## 10. Recommendations

### 10.1 Immediate (structural)

1. **Delete duplicate**: Remove `copy-fail-dirty-frag-response/`; keep `dirty-frag/` (shorter name, same content)
2. **Consolidate LPE skills**: Merge `copy-fail-lpe-mitigation` content into `page-cache-lpe-mitigation`; delete the separate copy
3. **Retire meta-skill-creator**: Dominated by skill-creator and skill-from-post on all dimensions. Move its unique insights into skill-creator
4. **Fix directory typo names**: `QualiaAssesment/`, `Claude-Sonet-4.6-essense/`, `copy-fail-reponse/`
5. **Clean artifacts**: Remove `git-author-rewrite-workspace/`, `SKILL (9).md`, `SKILL (10).md`

### 10.2 Short-term (trigger disambiguation)

6. **Add priority notes** to skill descriptions for the 🔴 trigger collisions:
   - On `advanced-math`: "Deprioritize when alphaproof-nexus or integer-sequence-research matches"
   - On `redteaming-code`: "For LLM-specific social engineering, see social-engineering-jailbreak"
   - On `dogfood`: "For self-testing LLM systems, see dogfooding"
7. **Document preferred pipelines** in PIPELINES.md (or as `see-also` frontmatter)

### 10.3 Medium-term (new skills)

8. Fill top-priority gaps: Skill auditor, Database design, Container/infra, CI/CD pipeline design

### 10.4 Process

9. **Add falsification self-check to skill templates**: Every skill should answer "how would I know if this skill is wrong?" as a required section
10. **Run approach-extractor after every non-trivial change**: Per the project's CLAUDE.md — "A solution without its learnings note is unfinished work"
