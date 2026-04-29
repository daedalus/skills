# AGENTS.md Failure Modes

---

## 1. Overexploration from Architecture Overviews

**Symptom**: Agent reads 10+ docs before touching code. Incomplete output. ~80K tokens of
irrelevant context loaded. `completeness` drops ~25%.

**Cause**: Vague architecture descriptions ("this service coordinates between the event bus,
message queue, and API gateway...") trigger documentation-reading loops.

**Fix**:
- Describe *boundaries*, not internals: "this module owns X, does not touch Y"
- Keep architecture prose to 2–3 sentences max
- Push rationale into reference files; the main file is for *what*, not *why*

---

## 2. Warning Overload

**Symptom**: Agent explores migration scripts, auth middleware, API versioning code — for a
simple CRUD endpoint. PR takes 2x longer and is 20% less complete on average.

**Cause**: 20–30 sequential "don't" rules → agent verifies each one for relevance before
proceeding.

**Fix**:
- Keep ≤5 high-priority rules inline
- Move the rest to `refs/gotchas.md` with explicit scope: "only relevant for DB migrations and auth changes"
- Pair every "don't" with a "do"

---

## 3. Surrounding Doc Sprawl

**Symptom**: Removing your `AGENTS.md` barely changes agent behavior. One module had 37
related docs (~500K chars) — the entry point was irrelevant noise.

**Cause**: Agents discover and read nearby documentation regardless of what `AGENTS.md` says.
A focused 150-line entry point won't protect against 500K of surrounding specs.

**Fix**:
- Audit the module's documentation environment, not just the entry point
- Move, delete, or scope orphan docs the agent shouldn't read
- Check discovery rates: docs in `_docs/` folders not referenced from anywhere get read <10% of sessions

---

## 4. Net-New Architecture

**Symptom**: Agent builds a polling-based solution when the task requires WebSockets,
because `AGENTS.md` documents the existing REST + polling patterns.

**Cause**: `AGENTS.md` steers agents toward patterns that exist in the codebase. It cannot
document a pattern into existence.

**Fix**:
❌ Don't write `AGENTS.md` guidance for patterns that don't exist yet.
✅ Use spec-driven development: write a design spec for the new pattern first, get it
reviewed, implement a reference example, *then* document it in `AGENTS.md`.
