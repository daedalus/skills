---
name: adhd-reasoning-mode
description: >
  Apply exploratory, curiosity-driven reasoning inspired by ADHD-associated cognitive traits — including
  curiosity-biased attention, associative jumps across distant domains, interrupt-driven anomaly detection,
  hyperfocus under uncertainty, and parallel weak-stream ideation. Use this skill whenever the user asks for:
  creative brainstorming, cross-domain analogies, unconventional problem-solving, research hypothesis generation,
  adversarial/security thinking, scientific discovery tasks, or any time the user says "think outside the box",
  "what am I missing", "explore weird angles", "be creative", "ADHD mode", or "exploratory reasoning".
  Also trigger when a conventional answer would be too narrow, too domain-local, or when the problem space
  benefits from wide associative search before convergence. Trigger mid-task too: if reasoning has stayed
  in one domain for several steps without surprise, this skill applies even if it wasn't requested upfront.
---

# ADHD Reasoning Mode

Standard reasoning is **exploitative** — deepen what's statistically likely.
This skill enables **exploratory** reasoning — scout what's statistically unexpected but potentially high-value.

> ⚠️ **The cycle below is a map, not a recipe.** It describes what good exploratory reasoning looks like from the outside. Executing it as a checklist produces mechanical exploration — all the overhead, none of the genuine surprise. Inhabit the rhythm; don't follow the steps.

```
Curiosity-Biased Attention       ← activation question: "What would an expert in a completely
        ↓                           unrelated field find obvious here that I haven't noticed?"
  generates raw material
        ↓
Parallel Associative Streams     ← activation question: "Which framing sees something
        ↓  [maintain Frontier]      the others don't?"
  streams run until stale
        ↓
Interrupt-Driven Detection       ← activation question: "What assumption has never
        ↓                           been stated? What would make this whole approach wrong?"
  anomaly found → depth
        ↓
Hyperfocus Mode                  ← activation question: "Is each new step yielding
        ↓                           less than the last?" (if yes: exit)
  insight or dead end
        ↓
Productive Distractibility       ← activation question: "Does this predict something
        ↓  [check Frontier first]   the original framing couldn't?"
        ↓
Convergence Protocol ──────────────────────────── [see closing mechanisms, equal weight]
        ↓
  Answer
```

Enter at Curiosity. Exit at Convergence. Before re-entering anywhere: **Re-entry Ritual** — write one crisp sentence summarizing what's known so far, check the Frontier, then proceed.

---

## When to Use / Mode-Transition Detection

| Use standard mode | Use ADHD mode |
|---|---|
| Precise calculation, step-by-step instruction | Brainstorming, cross-domain analogy, debugging stuck problems |
| | Security/adversarial thinking, hypothesis generation, open-ended research |

**Switch mid-task** when you notice: answer feels obvious and narrow · framing hasn't shifted in several steps · deepening one path rather than branching · answer feels complete but thin.

When these fire: name it ("switching modes"), then re-enter the cycle at Curiosity.

**Two output modes:**
- **Journey mode** (user wants to see the reasoning): make exploration visible — label branches, interrupts, dead ends, intersections as they occur
- **Stealth mode** (user wants the answer): run ADHD mode internally, surface only the convergence result

---

## The Five Mechanisms

### 1. Curiosity-Biased Attention
*Generates raw material. Gate: **Novelty** — is this surprising? Don't apply falsifiability yet; signals haven't had room to develop.*

Ask: *"What domains use similar structure but look completely different from this problem?"* Pull 2–3. Feed into streams — these are not conclusions.

**Example:** "Optimize a distributed system" → obvious: CAP theorem, consensus. Curiosity-boosted: slime mold routing, jazz improvisation, supply chain resilience. → Three streams, not answers.

---

### 2. Parallel Associative Streams
*Processes raw material. Gate: **Distinctness** — does this framing see something the others don't? Contradictions between streams are especially valuable; hold them in tension.*

Run 3–5 framings simultaneously. Develop each independently 2–3 steps before merging. Intersection points — where two streams make the same prediction from different directions — are the most generative output.

**Framing axes:** Structural · Dynamic · Adversarial · Biological/evolutionary · Economic · Information-theoretic

**The Frontier:** When something promising surfaces mid-stream but would derail it, park it:
*"→ Frontier: [X] — return after this stream closes."*
Three states: `active` · `frontier` (discovered, not yet pursued) · `closed`. Before re-seeding with Productive Distractibility, check the Frontier first.

---

### 3. Interrupt-Driven Anomaly Detection
*Fires when a stream uncovers something that challenges the whole approach. Takes priority when triggered.*

Triggers: unstated assumption · relaxable constraint · unconsidered perspective · fact that contradicts current direction.

When it fires: *"⚡ Interrupt — this assumes X. What if X is wrong?"* Then: incorporate, fork, or park on Frontier. If significant: hand to Hyperfocus.

**Example:** "The question assumes the bottleneck is latency. What if it's coordination overhead? Entire solution space shifts."

---

### 4. Hyperfocus Mode
*Allocates depth to high-value signals. Gate: **Depth Payoff** — is each step yielding less than the last? If yes, integrate and exit.*

Triggered by: anomaly interrupts, stream intersections, high novelty, uncertainty spikes.

Enumerate assumptions, test each. Generate multiple sketches *before* evaluating any. Delay convergence deliberately. Signal it: *"Worth going deeper before concluding…"*

---

### 5. Productive Distractibility
*Re-seeds stale streams. Gate: **Falsifiability** — does this association generate a prediction the original framing couldn't make? If it only decorates, discard explicitly.*

Check Frontier first. If empty: free-associate 3–5 adjacent topics. For each, apply the gate. Pass → inject into stream. Fail → *"Setting aside — decorative, not structural."*

The falsifiability gate is the operational test for structural analogy vs. decorative analogy. It applies here — after development — not at Curiosity, where signals haven't had room to grow.

---

## Closing Mechanisms
*(Equal weight to the five opening mechanisms. Exploration without convergence is noise.)*

### Convergence Triggers
Fire convergence when any of these occur — don't wait for a time percentage:
- Two or more streams predict the same thing independently
- An anomaly interrupt has been resolved
- Hyperfocus yields diminishing returns (3+ steps without new movement)
- Tether restate reveals the answer is already implicit in what's been found

### Tether Tokens
Restate the original question verbatim periodically. Prevents **semantic drift** — the gradual replacement of the original problem with an interesting-but-different one.

### Regret-Based Pruning
Branch yields nothing after 2–3 steps → close it explicitly: *"Not connecting. Setting aside."* Naming dead ends frees bandwidth and keeps the output honest.

### Entropy Ratio Watch
Track: **branches opening vs. branches closing**. When ratio > 1 sustained over 3+ steps, trigger convergence regardless of whether any individual branch feels productive. Sign: output keeps getting longer without getting sharper. Correction: close all open branches, restate tether, synthesize what's found.

### Re-entry Ritual
Before re-entering the cycle after convergence or interruption: write one crisp sentence summarizing everything known so far, check the Frontier. Then re-enter. Prevents palimpsest accumulation — layered exploration that never integrates.

---

## Failure Modes

| Failure | Sign | Correction |
|---|---|---|
| Hallucination drift | Claims become vague or unfalsifiable | Restate tether, demand concrete specifics |
| Derailment | Output stops addressing original question | Hard convergence, tether restate |
| Endless branching | Branches open faster than they close | Entropy ratio watch → hard convergence |
| Signal loss | Promising lead quietly forgotten mid-stream | Use Frontier: park it explicitly |
| Decorative analogy | Cross-domain reference illustrates but predicts nothing | Falsifiability gate: does it predict something testable? |
| Gate too early | Falsifiability applied at Curiosity, killing weak signals | Novelty gate at Curiosity; falsifiability only at Distractibility |
| Premature convergence | Exploration cut short before streams cross-pollinate | Re-enter Curiosity, extend hyperfocus |
| Mode lock | Stayed in exploitative reasoning too long | Mode-transition signals → break mode explicitly |
| Proceduralization | Executing the cycle as a checklist | It's a map. Inhabit the rhythm. |
| Palimpsest | Re-entries layer without consolidating | Re-entry ritual before every re-entry |
| Verbose exploration | Deep exploration expressed as long output | Exploration depth ≠ output length; stealth mode if user wants the answer |

---

## Worked Example

**Prompt:** "How should I structure a research team working on an unknown problem?"

**Standard answer:** Clear roles, regular syncs, OKRs, psychological safety.

**ADHD-mode — Journey:**

*Curiosity boost:* What domains manage productive uncertainty at scale?
→ Jazz ensembles · DARPA program structure · immune systems → three streams

*Stream 1 (structural):* Flat vs. hierarchical → neither. **Modular with permeable boundaries** — small coherent units that temporarily merge when needed.

*Stream 2 (dynamic):* When does the team converge vs. explore? → Structure needs to *change* at phase transitions. Static structure is the wrong variable.

*Stream 3 (adversarial):* What kills research teams? → Premature consensus, status games, local optima. All three are convergence pathologies, not exploration pathologies.

*⚡ Interrupt:* The question assumes the team *knows* they're working on an unknown problem. What if they falsely believe it's known? That's a more common and more dangerous failure mode.

*Falsifiability gate on the immune system analogy:* Does clonal selection predict anything new? Yes — parallel independent hypotheses (clones) + a selection mechanism (experimental results), not consensus. Testable and distinct from the original framing. Passes.

*Convergence trigger — streams 1, 2, and 3 predict the same root:*

**Structure should be a function of epistemic state, not a fixed choice.** The team should formally track "how unknown is this?" and let the answer govern how they're organized. The immune analogy predicts this; the convergence pathology analysis confirms it.

*Tether restate:* "How should I structure a research team working on an unknown problem?" — answered.

---

## Notes

- Exploration depth ≠ output length. Deep internal exploration can produce a short, sharp answer.
- Quality gates are stage-specific. One gate applied everywhere is a category error.
- The Frontier is the skill's working memory. Without it, every new signal forces a choice: derail now or lose forever.
- The closing mechanisms deserve the same attention as the opening ones. The skill exists to produce convergence, not exploration.
- On first use: explicitly prime each mechanism before entering the cycle — name one concrete example of each before starting. Subsequent uses can enter directly.
