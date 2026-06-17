---
name: auto-research-engineer
description: Use this skill whenever the user wants to set up a tight, repeatable test-and-score loop to improve ONE thing — code performance, marketing copy, ad creative, email or DM scripts, landing pages, configs, or prompts — by changing it, measuring it against a single objective number, and keeping only the changes that beat the baseline. Trigger on phrases like "auto research engineer," "nanochat loop," "program train prepare," "A/B test loop," "evolutionary optimization," "hill climbing," or "keep what wins, trash what loses," and on any request to run iterative experiments against one metric (load time, click-through rate, open rate, conversion rate, reply rate, function speed, token cost, etc.) — even if the user doesn't name the skill directly. Also use when the user asks to run something "overnight," "indefinitely," or "in the background" to improve a number, so the actual execution constraints of the current environment get set honestly before work begins.
---

# Auto Research Engineer

Inspired by Andrej Karpathy's nanochat "program, train, prepare" loop. The whole idea: pick ONE thing, turn "is it good?" into a single honest number, then run a tight loop of changing it, scoring it, keeping what wins, and trashing what loses. This is hill-climbing / evolutionary optimization applied to a real business asset.

The power of this approach comes from discipline: one asset, one number, one change at a time, and a scoring method that never moves to flatter the result. Resist the urge to change two things at once or to declare victory on vibes — the whole point is that the number decides, not your judgment in the moment.

## Step 0: Set honest expectations before anything else

Before setting up, tell the user plainly what "the loop" can actually mean in the environment you're running in. Don't let the metaphor of an autonomous overnight worker create a promise you can't keep.

- **Claude.ai chat (web/mobile, this interface):** There's no standing background process. Work happens only when the user is actively in the conversation. What you *can* do here: run many rounds back-to-back in one working session using the bash tool, for anything testable computationally (code, algorithms, a scoring script you can execute). For things that need real-world signal (actual email opens, actual ad clicks), each round is naturally gated by how fast that traffic arrives, and you log results as they come in across sessions.
- **Claude Code:** Has real scheduling primitives — `/loop` for in-session recurring prompts (expires after a few days), and cloud-based scheduled tasks for durable, unattended runs that don't depend on a machine staying awake. This is the right place for genuinely overnight, indefinite loops.
- **Claude Cowork (desktop):** Has scheduled/recurring tasks too, but only fires while the computer is awake and the app is open; skipped runs catch up on next wake.

If the user wants truly unattended overnight execution and you're in plain Claude.ai chat, say so and suggest Claude Code or Cowork for that piece, while still building the three-file system now — it's portable to wherever the loop actually runs.

## Step 1: Build the three-file system

Every optimization target gets exactly three files (or one ASSET that's itself multiple files, e.g. a small codebase or a folder of HTML/CSS):

1. **`instructions.md`** — Locked to the human, edited only by them. States in plain English: what's being optimized and why, the rules of engagement, and the operating cadence ("run in short loops, indefinitely, until the goal is hit or the human stops it"). Use `assets/instructions_template.md` as a starting skeleton.
2. **The ASSET** — The only thing you're allowed to change. The literal artifact being optimized: source code, an HTML page, email copy, a DM script, an ad, a config file, a prompt. Every round mutates this and only this.
3. **`score.py` / `scoring.md`** — The objective measuring stick. Locked to you: you may *read* it to compute a score, but you must never edit it and never redefine what "better" means mid-run. No moving the goalposts to make a number look good. Use `assets/score_template.py` as a skeleton when the scoring is computational; use `scoring.md` instead when scoring depends on external data the human reports back (e.g. campaign analytics).

State this division explicitly to the user before touching anything: "I can only edit the asset. The instructions and the scoring method are yours — I'll read them, never rewrite them."

## Step 2: Interview to plug everything in

Ask, don't assume:

- **What's the asset?** Get the actual files, repo, or content, and the access needed (read+write on the asset only — never on the scoring file).
- **What's the ONE metric?** Page load in ms, positive reply rate, click-through rate, open rate, function runtime, token cost, conversion rate — one number, not a vibe. If the user proposes something fuzzy ("make it more engaging"), push to translate it into something measurable before moving on.
- **How will it actually be measured?** A script you can run, an API you can call, or numbers the human will report back after each round. This determines how fast the loop can actually spin.

If a relevant connector or API would help (e.g. an email platform, an ads platform, an analytics tool) and one isn't already connected, check available connectors before assuming you need raw API keys pasted into chat.

## Step 3: Run the FIT CHECK

Before committing to a target, score it honestly against these criteria. Tell the user directly if it fails — don't quietly proceed with a bad target.

**Must-haves (all three required, or stop and reshape the target):**

a) **Scored objectively** — a real number computed the same way every time, not "does this look nicer."
b) **Fast feedback loop** — results in minutes or hours, not weeks. SEO reindexing, long sales cycles, or anything needing months of churn data doesn't fit this loop.
c) **Real access to change the asset** — a file or API you can actually write to, not a published video or a printed flyer already in the mail.

**Nice-to-haves (more = a more powerful loop, but none are required):**

d) **High volume of feedback** — lots of traffic, sends, or runs per unit time, so rounds aren't bottlenecked waiting for data.
e) **Cheap to fail** — each test costs little (compute, a few cents of ad spend, an image generation) rather than a lot (hiring a designer, printing materials).
f) **Consistent measuring stick** — fair, repeatable comparisons (fresh audiences each round, no list fatigue, no contaminated samples).

If a must-have fails, say exactly which one and propose a better-shaped target instead of forcing the loop onto something that won't actually produce a trustworthy number.

## Step 4: Run the loop

Once the three files exist and the target passes the FIT CHECK, repeat:

1. **Record baseline** — current ASSET + its score from the scoring file.
2. **Form ONE hypothesis, make ONE change** — a single test variation. Resist bundling multiple changes; you won't know which one mattered.
3. **Test and score** — using the scoring file only, never your own judgment of whether it "seems better."
4. **Keep or revert** — if the new score beats baseline, it becomes the new baseline (natural selection: the winner survives). If not, revert to the previous file exactly and try a different change next round.
5. **Log the round** — round number, what changed, score before → after, kept or reverted. Use `assets/log_template.md` as the format.
6. **Repeat** — in short cycles, for as many rounds as the environment and feedback speed allow, until the goal is hit or the human stops the loop.

When running many rounds in one Claude.ai session via the bash tool, batch the cycle (change → run → score → keep/revert → log) tightly so each round is fast, and surface a running tally as you go rather than going silent for a long stretch.

## Step 5: Report back

Keep the log readable as a single running document, not scattered notes. At the end of a session (or whenever asked), offer a clean summary: total rounds run, how many changes were kept vs reverted, the score trajectory from the original baseline to the current best, and what's likely worth trying next. Be honest if a session produced no improvement — log that as a real finding, not a failure to hide.
