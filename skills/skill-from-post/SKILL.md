---
name: skill-from-post
version: 2.0.0
description: >
  Converts any post, thread, article, paper, video transcript, technique, workflow,
  or methodology into a robust production-quality SKILL.md. Extracts the underlying
  insight, workflow, assumptions, and validation criteria; drafts a skill; then
  dogfoods and patches it through 2–6 rounds until behavior stabilizes. Use whenever
  the user says "turn this into a skill", "create a skill from this post/technique/paper",
  "make a skill for X I just read", "dogfood this", or pastes/links content and wants
  to operationalize it. Also trigger when the user describes a multi-step technique
  they've seen elsewhere and wants to capture it as a reusable capability.
source_type: unknown
dogfood_rounds: 0
stability_score: 0
---

# Skill-from-Post

Convert external knowledge into a reusable skill through a structured pipeline:

**Extraction → Distillation → Novelty Check → Draft → Dogfood → Patch → Package**

The objective is not to reproduce the source. The objective is to extract the reusable
capability inside the source and express it as a reliable, self-contained SKILL.md.

---

## Core Principles

**The skill is the specification.** During dogfooding, follow the written instructions
literally. If execution requires information not written in the skill, that is a defect.

**Stability over completeness.** A skill that reliably handles 3 scenarios beats one
that claims 10 and fumbles half.

**Surface ambiguity.** Do not silently resolve unclear instructions. Patch or record.

**Preserve the core insight.** Separate the technique from the author's examples and
preferences. Extract the underlying mechanism.

---

## Phase 0 — Ingest the Source

| Source type | Action |
|---|---|
| Pasted text / thread / article | Read directly from context |
| URL | `web_fetch` it; if paywalled, JS-rendered, or 4xx/5xx → tell the user, ask them to paste the key sections |
| Uploaded file | Read via file-reading skill |
| Video transcript | Read transcript from context or file |
| Research paper | Extract methodology section |
| Vague description | Interview the user (≤2 questions, see below) |

**If the source is vague**, ask at most two questions:
1. What is the technique trying to achieve?
2. What does a successful outcome look like?

Proceed with available information. Do not stall waiting for perfect input.

---

## Phase 1 — Extraction

Extract these fields from the source:

```
TECHNIQUE_NAME     : short identifier
CORE_WORKFLOW      : numbered steps the source actually describes
KEY_TERMS          : domain jargon or named concepts introduced

STRONG_TRIGGERS    : situations where this skill should almost certainly activate
WEAK_TRIGGERS      : situations where it may be relevant
ANTI_TRIGGERS      : situations where it should NOT activate

EXPECTED_OUTPUT    : what does success look like?

EDGE_CASES         : failure modes or caveats mentioned in the source
INVARIANTS         : properties that must remain true (e.g. output reproducible, reasoning explicit)
LATENT_ASSUMPTIONS : missing steps, hidden knowledge, implicit prerequisites
```

Surface the extraction as a brief summary. Ask: "Does this capture it?" — one exchange max.
If no reply, proceed.

---

## Phase 1.5 — Distillation

Separate the source into:

| Layer | What it is |
|---|---|
| **Core Insight** | What makes the technique work — one paragraph |
| **Workflow** | The actual repeatable process |
| **Heuristics** | Useful rules of thumb |
| **Assumptions** | Conditions required for success |
| **Examples** | Illustrations only — not the technique |

The distillation feeds directly into the draft. Examples do not become instructions.

---

## Phase 1.75 — Novelty Assessment

Classify the extracted technique:

- Novel workflow
- Combination of existing workflows
- Prompt template
- Checklist
- Variant of an existing installed skill

If the technique is not meaningfully distinct from something already available,
inform the user before proceeding. Do not silently create a redundant skill.

---

## Phase 2 — Draft SKILL.md

Write the initial skill using the distillation output:

```markdown
---
name: <slug>
description: >
  [What the skill does + when to trigger it. Be "pushy" — list trigger phrases
   explicitly. Include Strong/Weak triggers. Include Anti-triggers to prevent
   false activation.]
---

# Title

## Purpose
[One paragraph: what this is, why it matters, the core insight.]

## When to use this skill
[Bullet list — drawn from STRONG_TRIGGERS and WEAK_TRIGGERS]

## When NOT to use this skill
[Bullet list — drawn from ANTI_TRIGGERS and LATENT_ASSUMPTIONS]

## Workflow
[Numbered steps — concrete, imperative, no hand-waving.
 Each step: action + tool/method + observable output of that step.]

## Validation
[How to know each step succeeded. Observable criteria, not vibes.]

## Known Failure Modes
[From EDGE_CASES + anything anticipated]

## Example
[Minimal worked example — real input, step-by-step trace.
 For non-text outputs (binaries, terminals, plots), describe what you'd observe,
 not raw output.]
```

Keep SKILL.md under 300 lines. For large supporting material, use `references/`
and link from SKILL.md with guidance on when to read each file.

---

## Phase 3 — Dogfood Loop

Run 2–6 rounds. Each round uses a distinct scenario category.

### Scenario categories (use each at most once)

| # | Category | Description |
|---|---|---|
| 1 | Typical | Representative, well-formed input |
| 2 | Minimal | Sparse input, just enough to proceed |
| 3 | Ambiguous | Unclear intent or incomplete source |
| 4 | Adversarial | Input designed to expose edge cases |
| 5 | Large/complex | Multi-step source or dense content |
| 6 | Edge-case | Unusual format, domain, or scope |

### Round procedure

**Step 1** — Pick a test prompt from an unused category.

**Step 2** — Execute the skill exactly as written. No shortcuts. No unstated assumptions.
If you must fill a gap not in the skill, that gap is a finding.

**Step 3** — Audit. Identify:
- Ambiguities in instructions
- Gaps (information required but not specified)
- Failures (wrong output)
- Hidden assumptions (things you "knew" that aren't written)
- Validation weaknesses
- Trigger problems (would this have triggered? should it not have?)

**Step 4** — Patch. Apply targeted modifications. Annotate:
`<!-- patched round N: reason -->` — strip before final delivery.

**Step 5** — Record findings.

### Finding record

| Field | Values |
|---|---|
| Finding | Description |
| Cause | Root cause |
| Patch | What was changed |
| Severity | Critical / Major / Minor |

### Quality rubric (score each round)

| Metric | 1–5 |
|---|---|
| Correctness | Did the skill produce the right output? |
| Completeness | Did it cover the full workflow? |
| Consistency | Would it behave the same on a second run? |
| Ease of Use | Could a fresh Claude follow it without guessing? |
| Trigger Precision | Would it activate when it should and not when it shouldn't? |

### Stability score

```
stability_score = 100 - (10 × findings) - (5 × ambiguities) - (5 × undocumented assumptions)
clamp: 0 ≤ score ≤ 100
```

### Early stop rule

Stop when **both** are true:
- Two consecutive rounds with 0 findings
- stability_score ≥ 90

Otherwise continue until 6 rounds complete.

### Round accounting table

Show this table at the start of Phase 4, before asking for user feedback.

| Round | Category | Prompt summary | Findings | Patches | Rubric total | Stability | Stable? |
|---|---|---|---|---|---|---|---|
| 1 | Typical | ... | N | ... | /25 | N | no |
| ... | | | | | | | |

### Open issues

If 6 rounds complete without stability, document:
- Unresolved ambiguity
- Unresolved failure mode
- Required future work

Do not hide them.

---

## Phase 4 — Final Validation

Review the complete skill as a whole. Verify:

- Internal consistency across all sections
- Trigger correctness (strong/weak/anti)
- Workflow completeness (no gaps)
- Validation coverage (every step has a success criterion)
- Example correctness (trace matches the workflow as written)

Recompute `stability_score`. Update frontmatter.

---

## Phase 5 — Finalization

1. Strip all `<!-- patched round N ... -->` annotations.
2. Update frontmatter: `source_type`, `dogfood_rounds`, `stability_score`, `version`.
3. Ensure documentation matches actual behavior (not intended behavior).
4. Show the round accounting table to the user.
5. Ask: "Anything you'd change before I package it?"

---

## Packaging

```bash
mkdir -p /tmp/<slug>
cp SKILL.md /tmp/<slug>/
# If references/ exists:
cp -r references/ /tmp/<slug>/
cd /tmp && zip -r <slug>.skill <slug>/
cp /tmp/<slug>.skill /mnt/user-data/outputs/
```

Present the `.skill` file via `present_files`.

---

## Success Criteria

A successful skill:
- Activates when appropriate, not otherwise
- Requires no hidden knowledge to execute
- Survives adversarial testing
- Clearly defines validation for each step
- Documents all known assumptions
- Achieves stability_score ≥ 90
- Remains understandable by a first-time reader
