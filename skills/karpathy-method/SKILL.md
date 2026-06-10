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
Outputs vary by context: a filled-out **spec document**, a ready-to-use **agent config
file**, or an **interactive walkthrough** of all three layers.

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

Determine entry point from the user's request:

| User says… | Entry point |
|---|---|
| "Help me build X" / "I want to make Y" | **Layer 1 — Spec** |
| "My outputs are bad / inconsistent" | **Layer 2 — Verifier** |
| "Set up my AI workspace / agent config" | **Layer 3 — Environment** |
| "Walk me through the Karpathy method" | **Full walkthrough** |
| Unclear | Ask one question: "Are you trying to build something new, fix bad outputs, or set up your workspace?" then route accordingly |

When in doubt, start at Layer 1 — a good spec unlocks everything else.

Each layer produces a **concrete artifact**. Don't give advice without producing the artifact.

---

## Layer 1: The Spec

The spec is how you deliver your understanding to the AI in a format it can act on.

### Interview Protocol

Run a focused interview — **3 questions max**, then draft the spec. Don't wait for
perfect information. Draft, then let the user correct it.

Ask in this order, stopping as soon as you have enough to draft:

1. **Goal**: "What outcome are you trying to achieve — not the task itself, but the
   decision or conclusion this work needs to drive?"
2. **Context**: "What does only you know about this that an AI wouldn't? (Constraints,
   prior work, preferences, existing systems.)"
3. **Done**: "How will you know it worked? What does a successful result look like?"

After the third answer (or sooner if you have enough), say: *"Got it — drafting the
spec now. You can edit anything that's off."* Then produce the artifact immediately.

### Spec Artifact

```markdown
## Goal
[The real goal — the decision or conclusion this drives, not the task]

## Context
[What only the user knows: constraints, preferences, existing systems, prior work]

## Scope
[Exactly what is in and out of scope for this slice]

## Success Criteria
[Precise, measurable definition of "done" — specific checkpoints, not "looks good"]

## Key Decisions to Verify
[Assumptions the AI would otherwise make that the user must confirm before proceeding]
```

### Spec Rules

- **One slice at a time.** If the scope feels large, split it. Each spec covers one
  reviewable chunk of work.
- **Precision over completeness.** A short, precise spec beats a long vague one.
  Every assumption the AI makes is a chance to drift.
- **Flag, don't assume.** Instruct the AI: *"If anything is ambiguous, stop and ask
  rather than guessing."*

After presenting the spec, ask: *"Does this capture what you need, or should we adjust
the scope or success criteria before moving to verification?"*

---

## Layer 2: The Verifier

AI is a robot librarian — brilliant when it has the book, confidently wrong when it
doesn't. The only lever you have is verification. Yelling or vague feedback doesn't help.

### Step 1 — Define "done" precisely

Before the AI touches anything, turn the spec's success criteria into explicit
evaluation rules.

❌ Vague: *"Make this report look good."*
✅ Precise: *"The report must have exactly 3 sections. Each section ends with a
numbered recommendation. No section exceeds 300 words."*

Add to the spec or agent config:
> *"Before starting work, state the evaluation criteria you will use to judge the
> output. Be specific. Do not begin until I confirm these criteria are correct."*

### Step 2 — Use a second model as critic

Have a different AI model review the first model's output. The value is in the
disagreements they surface — two models with different training will catch different
failure modes.

Add to your prompt when quality is critical:
> *"When you have a complete draft, stop and critique it yourself from the perspective
> of a skeptical reviewer. List every assumption you made and every place the output
> could be wrong or incomplete. Then revise before showing me."*

Or route to a second model explicitly:
> *"Here is the output from [Model A]. You are a critical reviewer. List every flaw,
> gap, or assumption you see. Be specific — vague feedback like 'this could be
> improved' is not useful."*

### Step 3 — Pull external signal

Ground verification in real data, not the AI's self-assessment.

- **Technical tasks**: Connect the agent to deployment logs, test runners, linters,
  or CI output — so "it worked" is verified by the system, not claimed by the AI.
- **Non-technical tasks**: Provide historical examples (past reports, prior versions,
  reference documents) so the AI can check its output against a concrete standard.

**Prompt to identify what signal you need:**
> *"Before we start: what external data sources, reference examples, or automated
> checks should I provide so you can verify the output rather than just asserting
> it's correct?"*

### Verification Prompt (copy-paste ready)

> *"Before starting: (1) State the evaluation criteria you'll use to judge quality.
> (2) Identify any external reference or signal I should provide. (3) Tell me where
> you'll pause to show me a checkpoint before continuing. Do not proceed until I
> confirm all three."*

After applying the verifier, **append a Verification Plan section to the spec artifact**:

```markdown
## Verification Plan
- Evaluation criteria: [list]
- External signal / reference: [what to provide]
- Checkpoint: [where the AI pauses for review]
- Second-model review: [yes/no, and when]
```

---

## Layer 3: The Environment

The workshop where Layers 1 and 2 live. Built once, improving over time.
Most people start from scratch every session — this layer makes work compound.

### Step 1 — Agent config file

Most AI coding agents read a persistent markdown file injected automatically at the
start of every session. Find yours:

| Tool | Config file |
|---|---|
| Claude Code | `CLAUDE.md` |
| Cursor | `.cursor/rules` or `.cursorrules` |
| Codex CLI | `AGENTS.md` |
| GitHub Copilot | `.github/copilot-instructions.md` |
| Windsurf | `.windsurfrules` |
| Other agents | `AGENT.md` (common fallback) |

**Recommended structure:**

```markdown
# Workspace Overview
[What this repo/project is, how it's organized, key directories and their purpose]

# Runbooks
[List of available runbooks and exactly when to use each one]

# Knowledge Architecture
[Where to find specific types of information — domain context, examples, decisions]

# Working Rules
- Spec-first: before any multi-step task, draft a spec and get confirmation
- Agile chunks: break large tasks into small, reviewable slices
- Verification plan: before starting work, state evaluation criteria and checkpoints
- Flag ambiguity: if anything is unclear, stop and ask rather than assuming
- [Project-specific rules here]

# Guardrails
- Always do: [list]
- Ask first: [list]
- Never do: [list — these must also be enforced by tool-level hooks, not just listed here]
```

**Prompt to generate a config file from scratch:**
> *"Based on what I've described about my project, generate an agent config file.
> Use the Karpathy method structure: workspace overview, working rules (spec-first,
> agile chunks, verification checkpoints, flag ambiguity), runbooks section, knowledge
> architecture section, and guardrails classified into always-do / ask-first / never-do."*

**If the user has no existing project context**, generate a minimal starter config
with placeholder sections and explain what to fill in.

### Step 2 — Knowledge base

A structured folder of domain-specific data the AI can navigate — your moat.
Your data is what other people using the same base model don't have.

```
knowledge/
├── README.md          ← index: what's here and when the agent should read it
├── domain/            ← field/product context the AI won't have from training
├── examples/          ← past outputs used as format benchmarks
├── decisions/         ← key decisions made and why (prevents re-litigating them)
└── templates/         ← reusable output formats
```

The README is critical — without it, the AI doesn't know what to look for or when.
It should answer: *"Given task X, which files here are relevant?"*

If the user has no knowledge base yet, suggest starting with just two files:
`knowledge/README.md` and `knowledge/examples/` with one past output.

### Step 3 — Runbooks

A runbook is a reusable handbook for a specific repeated task. It encodes your
corrections so you don't have to make them again.

**Rule of thumb: if you've corrected the AI on the same thing twice, write a runbook.**

Runbook structure:

```markdown
# [Task Name] Runbook

## When to use this
[Trigger conditions — be specific so the AI knows when to apply it]

## Steps
[Numbered, concrete instructions]

## Output format
[Template or example of what the final output should look like]

## Common failure modes
[Things the AI gets wrong on this task and how to avoid them]
```

If the user says they have no repeated tasks yet, ask: *"What's one thing you've had
to re-explain or correct in the last week?"* That's the first runbook.

Runbooks compound — the more you use them, the more gaps you'll find to fix.

### Step 4 — Guardrails (Three Buckets)

Every action the AI might take falls into one of three buckets:

| Bucket | Meaning | How to enforce |
|---|---|---|
| **Always do** | Run on autopilot, no confirmation | List in agent config |
| **Ask first** | Pause and confirm before proceeding | List in agent config |
| **Never do** | Cannot be wrong — critical | **Tool-level hook** (not just config) |

> ⚠️ Agent config rules are instructions, not constraints. The AI can still ignore
> them under the right conditions. For anything in the **Never do** bucket, implement
> a pre-tool-use hook that blocks the action at the tool level — before the AI can
> execute it, regardless of what the prompt says.

**Prompt to audit and classify guardrails:**
> *"Review my project description and classify every action the AI agent might take
> into three buckets: always do, ask first, never do. For each 'never do' item,
> describe what tool-level hook would enforce it mechanically."*

---

## Full Walkthrough Flow

When the user wants the complete method applied end-to-end:

**Step 1 — Layer 1**: Run interview (3 questions max) → produce spec artifact → user confirms or corrects

**Step 2 — Layer 2**: Derive evaluation criteria from spec → append Verification Plan section → identify external signals → user confirms

**Step 3 — Layer 3**: Generate agent config file → outline knowledge base structure → identify first runbook from repeated corrections → classify guardrails into three buckets

**Artifacts to deliver, in order:**
1. `spec.md` — goal, context, scope, success criteria, key decisions
2. Verification Plan appended to spec
3. Agent config file (named for their tool)

Present each artifact before moving to the next. After each, ask:
*"Does this look right, or should we adjust anything before continuing?"*

**After all three are delivered**, close with:
> *"These three artifacts are your starting point. The environment compounds over
> time — add to the runbooks when you catch a repeated correction, extend the
> knowledge base when you find the AI missing domain context, and tighten the
> guardrails when something goes wrong. The system gets better every time you use it."*
