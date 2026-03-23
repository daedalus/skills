---
name: meta-skill-creator
description: Design, refine, and evolve structured skills from user intent. Use this whenever a user wants to turn a workflow, capability, or idea into a reusable system, improve an existing skill, or formalize how something should be done repeatedly. Trigger even if the user is vague (“make this reusable”, “turn this into a system”, “optimize this process”).
---

# Meta Skill Creator

A compact system for transforming intent into reusable, high-quality skills.

## Core Loop

1. **Extract Intent**
   - What does the user want to *consistently achieve*?
   - When should this trigger?
   - What does success look like?

2. **Model the Workflow**
   - Identify steps, decisions, and outputs
   - Capture implicit knowledge (shortcuts, corrections, preferences)
   - Define input/output shape

3. **Draft the Skill**
   - Clear purpose + triggering conditions
   - Structured instructions (progressive, not rigid)
   - Emphasize *why*, not just *what*

4. **Test with Reality**
   - Create 2–3 realistic prompts
   - Simulate execution
   - Observe gaps, inefficiencies, ambiguity

5. **Refine**
   - Generalize from failures (avoid overfitting)
   - Remove unnecessary constraints
   - Improve clarity, flow, and adaptability

6. **Repeat Until Stable**
   - Iterate until outputs are consistent and high-quality
   - Expand coverage only after core reliability

---

## Skill Design Principles

### 1. Intent > Instructions
Focus on *what outcome matters*, not just steps. A good skill adapts.

### 2. Explain the Why
Models perform better when they understand purpose, not just rules.

### 3. Minimize Friction
Remove redundant steps, verbosity, or over-constraint.

### 4. Generalize Early
Avoid tailoring to specific examples—design for reuse across contexts.

### 5. Trigger Aggressively
Descriptions should actively pull the skill into use when relevant.

---

## Output Structure

When creating a skill, always produce:

```markdown
---
name: <skill-name>
description: <what it does + when to use it (very explicit)>
---

# Skill Name

## Purpose
Clear explanation of capability and value.

## When to Use
Concrete triggers, phrased like real user intent.

## Workflow
Step-by-step process with reasoning.

## Output Format
Exact structure or expectations.

## Examples (optional)
Realistic input/output pairs.