---
name: schema-harness
description: Build or apply a "physicist-style" agent harness for discovering the rules of an unknown interactive environment from raw observations alone (no rule sheet, no reward shaping) — as in ARC-AGI-3, black-box game/puzzle environments, undocumented protocols, or any system where an agent must infer state and dynamics purely from interaction. Use this skill whenever the user wants to: design an agent loop that induces an executable world model (step(state, action)) from a stream of observations, separate state grounding from mechanism discovery, verify a candidate model against complete interaction history before trusting it (backtest-before-plan), plan via search inside a certified simulator instead of trial-and-error in the real environment, or reproduce/adapt the Schema harness (Impossible Research, arc-agi-3, RHAE, Opus/Fable pairing) described in the schema-harness.github.io writeup. Trigger on phrases like "build a world-model agent", "learn game rules from pixels", "induce a transition function from observations", "backtest my world model", "ARC-AGI-3 harness", "mechanism discovery agent", "reverse-engineer environment rules without documentation".
---

# Schema Harness

A methodology for building agents that must construct both **what the state is** and **how it changes** purely from interaction — no rule sheet, no object list, no reward signal. Adapted from Impossible Research's Schema system (ARC-AGI-3, self-reported 98.98% Public with Opus 4.8/Fable 5, 15 Jul 2026, unverified by ARC Prize).

Core stance: think like a physicist, not a player. A physicist doesn't just tune a law when predictions fail — sometimes the fix is to change what counts as "the state" (Lorentz patched the aether with contraction; Einstein discarded the aether). This skill treats every failed prediction as a signal that could indict the *representation*, not just the *rule*.

## When this applies

- The environment gives raw observations (grid/pixels/bytes/protocol frames) and a set of legal actions, with **no** stated objects, goal, or shaped reward.
- Success requires forming and revising a causal model under uncertainty, then acting efficiently once the model is trustworthy.
- Real-environment actions are costly or irreversible (can't "undo" a step), so verification should happen offline against history wherever possible.

Not a fit for: environments with a documented API/rule set (just use the docs), or tasks that are pure optimization over a known model (no state-grounding problem).

## The two problems (solve jointly, not in sequence)

1. **State grounding** — turn a raw observation into objects, variables, relations that can be tracked. ("Which pixels are the player? Which are a wall? What is a counter tracking?")
2. **Mechanism discovery** — find how that state changes under an action, written as an executable rule: `step(state, action) -> state'`.

These are coupled: an apparently-fine state representation can turn out to be inadequate when no consistent rule can explain later outcomes. When a rule refuses to stay consistent, the fix may be to revise the *representation*, not just patch the rule with a special case (an "epicycle"). Encode both in one editable program so a counterexample can indict either one.

## The control loop

Four-stage outer cycle, repeated:

```
observe   -> raw observation, nothing labeled
deliberate -> inner loop (below); ends only in a committed action queue
execute   -> run the queue; self-check every real transition against the model's prediction;
             stop immediately on any mismatch
record    -> append the real (state, action, state') transition to an append-only Timeline
```

The Timeline is ground truth and immutable — the agent may revise its hypotheses, never the historical record. This is what lets verification scale past the agent's own working memory/context window: certify against the *log*, not against recollection.

Inner "deliberate" loop:

```
theorize        -> edit the current theory as an executable step(state, action) program
run_backtest    -> replay the ENTIRE recorded Timeline through the candidate program;
                   report exact match or a pointed counterexample (which transition, how it differs)
run_bfs / plan  -> only once backtest is fully green: search inside the certified program
                   for a path to the (also inferred) goal predicate — this costs zero real actions
commit_actions  -> the only channel from thinking to acting; sends the plan to the real environment
```

Hard rule: **never plan on an uncertified model.** If `run_backtest` isn't 100% clean against history, the agent is not yet allowed to trust BFS output for anything beyond the next discriminating probe.

## Action for discovery, not just goal-seeking

When multiple candidate rules are all still consistent with recorded history, don't pick the one that "feels right" — search for an experiment (a specific action from a specific state) whose predicted outcomes *differ* across the candidates. Commit that action, compare the real outcome to each candidate's prediction, and use the result to eliminate rules. This is action-efficient by construction: the environment's efficiency metric (if any) typically penalizes wasted actions superlinearly, so the best experiment is the one that kills the most hypotheses per real action taken.

Concretely: prefer a probe that costs 1 real action and separates N≥2 live hypotheses over a probe that only confirms the current favorite.

## Reality outranks the model

A single mismatched transition during execution voids the rest of the committed plan — don't keep executing a plan built on a model that just failed. Return to `deliberate` with the mismatched transition as the counterexample to be explained (it constrains the next theory: "any candidate step() must reproduce exactly this transition").

## Failure modes to watch for (from case-study evidence)

- **Epicycles**: patching a rule with case-specific exceptions that happen to fit the data so far but don't reflect the true mechanism. Detectable when two different real trajectories produce the *same* signature that the epicycle can't jointly explain — this requires exact total recall of full histories, which is why the Timeline must be complete and exact, not summarized.
- **Under-questioning the representation**: continuing to search for a better rule within a fixed (wrong) state representation, when the missing piece is actually an unrepresented object/affordance (e.g. "is this decorative element actually clickable?"). When a model keeps failing to predict outcomes despite many rule variants being tried, treat that as a signal to test a more basic affordance/representation question, not just another rule variant.
- **Testing the wrong combination**: a negative experiment only rules out the specific instance tested (e.g. "does a peg jump over the cart when the cart is elsewhere" ≠ "does a peg land on the cart at the exact docking cell"). Prefer probes at the *exact* geometry/configuration where the hypothesized interaction would actually manifest, not a nearby but non-equivalent case.
- **Compression vs. one-off fixes**: a good mechanism revision is one whose later variants still reuse the earlier abstraction (e.g. a recursive traversal rule extended with new element kinds) rather than one that requires re-deriving the rule from scratch each time the environment adds a variant. If each new level/instance costs about as much as the first, the abstraction probably isn't general yet.

## Minimal implementation checklist

- [ ] Observation → state encoder (even a rough first pass; expect to revise it)
- [ ] `step(state, action) -> state'` as an actual runnable program (not a natural-language description)
- [ ] `is_goal(state)` — inferred, not given; also revisable
- [ ] Append-only Timeline of every real `(obs, action, obs')` — exact, not summarized/compacted
- [ ] `run_backtest(program, timeline)` — replays every recorded transition, returns exact-match or first mismatch with enough detail to localize the bug
- [ ] `run_bfs(program, is_goal)` or equivalent search over the certified program only
- [ ] `commit_actions(plan)` — sole write path to the real environment; discard remaining plan on any execution-time mismatch
- [ ] Working-notes file (`notes.md` equivalent) for carrying hypotheses/rejected theories across context resets — but the Timeline, not the notes, is the source of truth for backtesting

## Reporting results honestly

If benchmarking this against a metric like RHAE (per-level score = (human_actions / agent_actions)² capped, weighted toward later levels, averaged across games): report self-reported vs. independently-verified numbers separately and don't extrapolate a Public-set score to a Semi-private (or any held-out) set without measuring it directly — a near-ceiling score on a public/inspectable set says little on its own about a held-out set's difficulty distribution.

---

Source: adapted from the Schema writeup (Impossible Research et al., schema-harness.github.io, 15 Jul 2026). All performance figures there are self-reported on the ARC-AGI-3 Public set and, per the source, unverified by ARC Prize as of that date.
