---
name: ai-code-detection
description: >
  Detect whether a piece of code or an entire software project was written by a human,
  AI, or some hybrid thereof. Use this skill whenever the user wants to audit a file,
  snippet, repo, or commit history for AI authorship signals; phrases like "is this
  AI-generated", "was this written by ChatGPT", "detect LLM code", "human or AI?",
  "check for AI authorship", "is this vibe-coded", or any request to judge, score, or
  explain the provenance of code. Also trigger when the user pastes code and asks
  "did a human write this?" or "does this look AI-generated?" — even casually phrased.
---

# AI Code Detection

Weight-of-evidence methodology. No single signal is conclusive; build a case across
multiple axes. **Prioritize evolutionary/temporal signals over aesthetic ones** —
style is increasingly gameable; history is not.

> **Core insight**: The strongest signal of human authorship is *historical
> inconsistency*. Humans forget, pivot, leave scars, partially refactor, and change
> opinions mid-project. LLMs optimize toward coherence. A sufficiently coherent large
> codebase is itself suspicious.

---

## Step 0 — Classify the target

Before collecting evidence, determine category. The rubric produces one of:

| Category | Description |
|----------|-------------|
| **Human** | No meaningful AI assistance |
| **Human + AI-assisted** | Human architecture/thought, AI drafting/refactoring |
| **AI-generated + human-edited** | AI produced bulk, human polished |
| **AI-generated** | Mostly machine-originated |
| **Indeterminate** | Insufficient evidence |

A senior engineer using Claude for boilerplate can look "AI-ish" while remaining
fundamentally human-driven. Collapsing these into a binary verdict loses information.

---

## Axis 1 — Evolutionary signals (highest confidence)

Only applicable to repos with history. Weight this axis above all others.

**Human indicators** (history encodes process):
- Bug-introducing commits followed by fixes
- Refactors that *partially* migrate patterns — old and new coexist
- Inconsistent architecture that reflects changing opinions over time
- Deprecated code surviving longer than expected
- Temporary instrumentation later removed (`print`, metrics, flags)
- Performance hacks added *after* profiling (not speculatively)
- Emotional or frustrated commit messages
- Localized competence: one subsystem brilliant, another messy
- Migration scars: evidence of abandoned approaches

**AI indicators** (history is synthetic):
- Entire architecture appears fully formed in early commits
- Uniform code quality across all modules from day one
- Large feature landings with minimal iteration
- No migration scars, no dead abstractions
- No abandoned experiments
- Perfectly synchronized style across contributors and files
- Commit cadence aligned with prompting cycles (bursts, then silence)
- Sudden competence jumps inconsistent with prior work in the repo

---

## Axis 2 — Variance / entropy signals (strong)

Humans are *uneven*. AI tends toward statistical smoothness.

Measure (qualitatively or with tooling):
- **Function length variance**: human repos have fat tails; AI clusters tightly
- **Comment density variance**: humans have files with zero comments and files
  with excessive ones; AI is uniformly moderate
- **Cyclomatic complexity distribution**: human hot spots vs. AI uniform medium
- **Abstraction depth**: humans overengineer one thing and underengineer another;
  AI maintains consistent depth throughout
- **Naming quality**: uniformly medium-good naming across a large repo is suspicious;
  humans have naming that reflects when they wrote something and how tired they were

Low variance across a large repo is a red flag, not a verdict.

---

## Axis 3 — Operational scar signals (strong for production code)

LLMs are strongest at greenfield code and clean abstractions. They are weaker at
encoding the trauma of production systems.

**Human indicators** (systems encode history):
- Comments referencing incidents: `# race condition seen in prod 2023-08`
- Compatibility hacks: `if sys.version_info < (3, 8):`
- Weird retry logic that doesn't match textbook backoff
- `# don't touch this` with no explanation
- Vendor-specific workarounds
- Magic constants from production failures with no comment
- Defensive paranoia around specific race conditions
- `# TODO: remove after $vendor fixes their shit`

**AI indicators** (systems are idealized):
- Textbook retry/timeout patterns
- Clean abstractions where reality is usually ugly
- No vendor-specific ugliness
- Error handling that covers the happy path failures but not the weird ones

---

## Axis 4 — Style signals (weakest; treat as corroborating only)

**Deprecated / decaying signals** — increasingly describe good engineers using
Copilot, not AI authorship per se:
- Type hints everywhere
- Docstrings everywhere
- `set -euo pipefail`
- Proper error handling
- Exhaustive happy-path tests

**Still useful style signals** (weight lightly):
- Comments explain *what* not *why*
- Uniform naming: `process_data`, `handle_request`, `validate_input` everywhere
- Symmetric structure: every `if` has `else`, every `try` has `finally`
- Error messages that read like documentation
- Over-parameterized abstractions: `config=None`, `verbose=False`, `timeout=30`
  on everything, never varied by callers

---

## Axis 5 — Adversarial awareness

If evasion is suspected, look for:

**Humans trying to look human (synthetic mess)**:
- Intentionally added TODOs that don't correspond to real gaps
- Fake debug statements
- Synthetic "wip" commits with no actual incremental progress
- Artificially varied comment density

**Humans accidentally exposing AI use**:
- Stylistic phase shifts mid-repo (before/after Copilot adoption)
- Commit bursts aligned with prompting cycles
- Architecture sophistication inconsistent with prior work
- Two subsystems that look like they were written by different people — because
  one was prompted differently

**Future trajectory**: AI systems will increasingly reduce detectability via
repo-conditioned generation, personalized fine-tuning, and simulated iterative
development. Temporal/variance signals will outlast style signals.

---

## Workflow

### Step 1 — Determine scope
- **Snippet / single file**: axes 4 only; flag low confidence explicitly.
- **File + neighbors**: axes 2 and 4.
- **Full repo with history**: all axes; weight 1 and 3 heavily.

### Step 2 — Collect evidence
For each applicable axis, list concrete observations tagged **[H]** (human signal)
or **[AI]** (AI signal). Note "not applicable" for axes requiring history when
only a snippet is provided.

### Step 3 — Verdict

```
Scope: <snippet | file | repo>

Evidence:
  Evolutionary:   [H: ...] / [AI: ...] / [N/A]
  Variance:       [H: ...] / [AI: ...]
  Operational:    [H: ...] / [AI: ...] / [N/A]
  Style:          [H: ...] / [AI: ...]
  Adversarial:    [signals if present]

Category: <Human | Human+AI-assisted | AI-generated+human-edited | AI-generated | Indeterminate>
Confidence: <Low | Medium | High>

Key tells: <top 2–3 observations that drove the verdict>
What would change it: <additional evidence that would shift the assessment>
```

---

## Uncertainty Handling

"Indeterminate" is a valid and often correct verdict. State what additional evidence
would resolve it:
- Git blame / timestamps / commit graph
- Author's other known work for comparison
- Diff between stated and actual author competence level
- Specialized tooling (GPTZero Code, DetectGPT variants) — treat as one signal,
  not ground truth
