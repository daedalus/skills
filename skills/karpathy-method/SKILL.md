---
name: karpathy-method
description: >
  Apply the Karpathy 3-layer AI workflow method: Spec, Verifier, and Environment.
  Use this skill whenever a user wants to build something with AI and needs help
  structuring their approach, writing a spec, setting up verification, or creating
  an AI agent environment (agent config file, knowledge base, custom skills, guardrails).
  Also trigger when users say things like "help me use AI better", "I keep getting
  bad outputs", "how do I prompt more effectively", "set up my AI workspace",
  "write me a spec", "help me plan this project with AI", or ask about agentic
  workflows. Works with any AI coding agent (Claude Code, Cursor, Codex, Copilot, etc.).
  This skill covers the full loop from goal extraction to environment setup.
---

# Karpathy Method

A structured 3-layer framework for getting dramatically better results from AI agents.
Outputs vary by context: a filled-out **spec document**, a ready-to-use **agent config file**,
or an **interactive walkthrough** of all three layers.

Works with any AI coding agent: Claude Code, Cursor, Codex CLI, GitHub Copilot Workspace,
Gemini CLI, or any tool that reads a persistent markdown config from your repo.

---

## Core Mental Model

AI fails at context-driven tasks because it only has what you give it.
The framework bridges the gap between your understanding and AI's computational power.

> *"You can outsource your thinking, but you can't outsource your understanding."*
> — Andrej Karpathy

---

## How to Apply This Skill

Read the user's request and determine the entry point:

| User says… | Entry point |
|---|---|
| "Help me build X" / "I want to make Y" | Start at **Layer 1 — Spec** |
| "My outputs are bad / inconsistent" | Start at **Layer 2 — Verifier** |
| "Set up my AI workspace / agent config" | Start at **Layer 3 — Environment** |
| "Walk me through the Karpathy method" | Full walkthrough, all 3 layers |

When in doubt, start at Layer 1 — a good spec unlocks everything else.

---

## Layer 1: The Spec

The spec is how you deliver your understanding to the AI in a format it can act on.

### Step 1 — Uncover the goal

Don't accept the task at face value. Ask:
- *What decision does this output drive?*
- *What would make this a success?*
- *What context does only the user know?*

**Prompt template to use with the user:**

> "I'm going to interview you to uncover the real goal behind this project.
> Please answer as specifically as you can. After a few questions, I'll draft a spec.
>
> First: what is the outcome you're trying to achieve — not the task, but the
> conclusion or decision this work needs to drive?"

### Step 2 — Go agile, not waterfall

Break the work into small, reviewable chunks. Each spec should cover one slice.

Add this instruction when drafting specs:
> "Bias toward smaller, compartmentalized specs. Each spec covers one reviewable chunk."

### Step 3 — Be precise; force verification

Every assumption the AI makes is a chance to drift from what the user actually wants.

Add to the spec:
> "Make the user verify key decisions explicitly before proceeding. Flag any ambiguity
> rather than assuming."

### Spec Output Format

When writing a spec, produce a markdown document with these sections:

```markdown
## Goal
[The real goal — the decision or conclusion this drives]

## Context
[What only the user knows: constraints, preferences, existing systems, prior work]

## Scope
[Exactly what is in and out of scope for this slice]

## Success Criteria
[Precise, measurable definition of "done" — not "looks good" but specific checkpoints]

## Key Decisions to Verify
[List of assumptions the AI would otherwise make that the user must confirm first]
```

---

## Layer 2: The Verifier

AI is a robot librarian — brilliant when it has the book, confidently wrong when it doesn't.
Yelling or pleading doesn't help. The only real lever is verification.

### Step 1 — Set evaluation criteria up front

Before the AI touches anything, define what "good" looks like with precision.

❌ Vague: *"Make this report look good."*
✅ Precise: *"The report must have 3 sections, each ending with a concrete recommendation."*

Add to your spec or agent config:
> "Outline the evaluation criteria you will use to assess quality before starting.
> Be precise. Do not begin until criteria are confirmed."

### Step 2 — Use a second model as critic

Have a different model review the first model's output:
> "If this is a complex build, run the final output by a second model to check for
> agreement before considering it done."

Any two independent models work — the value is in the disagreement they surface.

### Step 3 — Pull external signal

Ground verification in real data, not self-assessment:

- **Technical**: Connect the agent to deployment logs, test runners, CI output — so
  "it worked" is verified, not guessed.
- **Non-technical**: Feed in historical examples (past reports, prior versions) as
  reference for the exact format expected.

**Prompt template:**

> "Identify what external data sources or reference examples I should provide to
> verify the output of this task. List them and explain what each one checks."

### Verification Prompt (reusable)

> "Before starting, outline: (1) your evaluation criteria for a high-quality result,
> (2) what external signal or reference you'll use to verify the output, and
> (3) a checkpoint where you'll pause and show me results before continuing."

---

## Layer 3: The Environment

The workshop where Layers 1 and 2 live. Built once, improving over time.
Most people start from scratch every session — this layer makes work compound.

### Step 1 — Agent config file

Most AI coding agents read a persistent markdown file from your repo root.
This file is auto-injected on every session and is the first thing the agent reads.

| Tool | Config file |
|---|---|
| Claude Code | `CLAUDE.md` |
| Cursor | `.cursorrules` or `cursor.md` |
| Codex CLI | `AGENTS.md` |
| GitHub Copilot | `.github/copilot-instructions.md` |
| Other agents | `AGENT.md` (common fallback) |

**Recommended structure (tool-agnostic):**

```markdown
# Workspace Overview
[What this repo/project is, how it's organized, key directories]

# Custom Skills / Workflows
[List of available runbooks and when to use each]

# Knowledge Architecture
[Where to find specific types of information in the codebase or knowledge base]

# Working Rules
- Before any multi-step build: create a verification plan
- Flag ambiguity rather than assuming
- Bias toward smaller, compartmentalized specs
- [Add project-specific rules here]
```

**Prompt to generate a config file:**

> "Based on what I've told you about my project, generate an agent config file
> (e.g. AGENT.md). Include: workspace overview, working rules that enforce the
> Karpathy method (spec-first, agile chunks, verification checkpoints), and
> placeholder sections for skills and knowledge architecture."

### Step 2 — LLM Knowledge Base

A structured folder of your own data — your moat.

```
knowledge/
├── README.md          ← tells the agent what's here and how to navigate it
├── domain/            ← context about your specific field/product
├── examples/          ← past outputs to use as reference/format benchmarks
├── decisions/         ← key decisions made and why (prevents re-litigating)
└── templates/         ← reusable formats for common outputs
```

Instruct the agent to consult the README before any task that might need domain context.

### Step 3 — Custom Skills / Runbooks

If you plan to do something repeatedly, encode it as a runbook (a handbook for that task).

Rule of thumb: **if you've corrected the AI on the same thing twice, write a runbook.**

Each runbook should contain:
- When to use it (trigger conditions)
- Step-by-step instructions
- Output format / template
- Common failure modes to avoid

Runbooks compound — the more you use them, the more you'll find where to improve them.

### Step 4 — Guardrails (Three Buckets)

Classify every action the AI might take into one of three buckets:

| Bucket | Meaning | Implementation |
|---|---|---|
| **Always do** | Autopilot — no confirmation needed | Note in agent config |
| **Ask first** | Needs a quick check before proceeding | Note in agent config |
| **Never do** | Critical — cannot be wrong | **Tool-level hook** |

> ⚠️ Agent config rules are guides, not hard rules — the AI can still ignore them.
> For things that are critical not to get wrong, use pre-tool-use hooks (supported
> by most agentic tools) that enforce the rule at the tool level, not the prompt level.

**Prompt to audit guardrails:**

> "Review my project and help me classify the AI agent's potential actions into three
> buckets: always do, ask first, never do. For 'never do' items, suggest what
> tool-level hook I should implement to enforce them."

---

## Full Walkthrough Flow

When the user wants the complete method applied to their project:

1. **Layer 1**: Interview → extract goal → draft spec → user verifies key decisions
2. **Layer 2**: Define evaluation criteria → identify external signals → add verification checkpoint to spec
3. **Layer 3**: Generate agent config → outline knowledge base structure → identify recurring tasks that need runbooks → classify guardrails

Produce outputs in this order:
1. Spec document (Layer 1 output)
2. Verification addendum to spec (Layer 2 output)
3. Agent config file (Layer 3 output)

Present each one for user review before proceeding to the next.
