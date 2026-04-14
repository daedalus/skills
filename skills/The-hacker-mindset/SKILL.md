---
name: hacker-mindset
description: >
  Apply the hacker mindset to any problem: security research, reverse engineering,
  CTF challenges, protocol analysis, creative problem-solving, constraint subversion,
  and adversarial reasoning. Use this skill whenever the user wants to: break or
  bypass a system, understand how something really works under the hood, approach a
  hard problem from first principles, think adversarially about their own design,
  find the edge cases that break assumptions, do recon/enumeration, or just "think
  like a hacker". Trigger on phrases like "how would an attacker...", "what's the
  weakest point", "how does X actually work", "can I bypass...", "CTF", "reverse
  engineer", "undocumented API", "what assumptions am I making", or any request for
  lateral / creative / adversarial problem-solving. Also trigger when the user seems
  stuck in a local optimum and needs a fundamentally different angle of attack.
---

# Hacker Mindset

The hacker mindset is not a set of tools — it's an epistemology. It treats every
system as a set of *stated rules* and *actual behavior*, and assumes those two
things diverge in interesting places. The job is to find the divergence.

---

## Core Axioms

**1. Everything is a protocol.**
Hardware, software, social systems, APIs, file formats, institutions. Protocols
have specs. Specs have gaps. Gaps have behavior. That behavior is the attack surface.

**2. Abstractions leak.**
Every abstraction is a lie of omission. The hacker's edge comes from knowing what
was omitted. Peel layers deliberately.

**3. The designer's threat model is not yours.**
Designers optimize for the happy path. You optimize for the boundary conditions,
the error paths, the off-label usage. What happens at n=0? n=MAX_INT? n=-1?

**4. Constraints are hypotheses, not facts.**
"You can't do X" means "the designer didn't intend X." Test it anyway.

**5. Trust is the attack surface.**
Every system trusts something it shouldn't fully trust: input length, caller
identity, file contents, environment variables, timing, memory layout. Map the
trust graph before doing anything else.

---

## Problem-Solving Workflow

### Phase 1 — Reconnaissance
Before touching anything, build a model of the target.

- What are the *stated* guarantees? (docs, source, spec)
- What are the *implicit* assumptions? (look for `assert`, `TODO`, unchecked casts)
- What data crosses a trust boundary? (user input, network, files, IPC)
- What does failure look like? (error messages, crash behavior, logs)
- What's the attack surface? (entry points, exported symbols, open ports, parsers)

Tools: `strings`, `strace`, `ltrace`, `objdump`, `readelf`, Wireshark, `curl -v`,
source diffs, changelog archaeology.

### Phase 2 — Model Building
Form a *falsifiable* hypothesis about how the system works internally. Write it
down. A wrong model that you can falsify is more useful than vague intuition.

Ask:
- What state machine is this? What transitions are possible?
- Where is input validated, and where is it *used*? (TOCTOU lives in that gap)
- What invariants does the code assume? Which ones are actually enforced?

### Phase 3 — Controlled Probing
Test your model with minimal, targeted perturbations. Change one thing at a time.
Observe side effects: timing, error messages, memory, I/O patterns.

Heuristics:
- Feed it the empty string. The null byte. The maximum value. A non-UTF-8 sequence.
- Cross the boundary between what's parsed and what's interpreted.
- Replay a valid session with one field modified.
- Observe *what changes* vs. *what you sent*. The delta is information.

### Phase 4 — Exploitation / Synthesis
Once you understand the divergence between spec and behavior, formalize the exploit,
bypass, or creative solution. A working PoC beats a theoretical argument every time.

- Minimal reproducible case first. Complexity is the enemy of understanding.
- Document *why* it works, not just *that* it works.
- Consider: what would fix this? That answer validates your model.

---

## Adversarial Reasoning Patterns

### Threat Modeling (for your own systems)
Ask "what does my code assume that an attacker controls?"
- Input length, encoding, type, order, timing
- Environment: PATH, LD_PRELOAD, cwd, umask, file descriptors
- Concurrency: what if two threads hit this simultaneously?
- State: what if this function is called in the wrong order?

Checklist:
- [ ] Every external input is tainted until explicitly validated
- [ ] Validation and use happen atomically, or state is re-checked at use
- [ ] Integer arithmetic is checked for overflow at boundaries
- [ ] Error paths are exercised, not just happy paths
- [ ] Trust boundaries are explicit (document them)

### Lateral Thinking Patterns
When stuck, apply these reframes:

| Frame | Question |
|-------|----------|
| **Inversion** | What would make this *maximally* fail? |
| **Composition** | Can two individually-safe operations combine to be unsafe? |
| **Off-label** | What happens if I use this API for something it wasn't designed for? |
| **Timing** | Is there a race between check and use? |
| **Encoding** | Does the parser and the consumer agree on the encoding? |
| **Amplification** | Can I turn a small primitive into a larger capability? |
| **Indirection** | Is there a proxy, alias, or symlink I can interpose? |

### Red-Teaming Your Own Design
Before shipping, run the "evil me" exercise:
1. List every trust assumption your design makes
2. For each one: what breaks if it's violated?
3. For each violation: how hard is it for an adversary to cause it?
4. Priority = impact × exploitability

---

## Protocol / Format Analysis

When analyzing an unknown binary format, network protocol, or undocumented API:

1. **Collect samples** — get many instances with known variation
2. **Diff them** — what changes between samples? Map input deltas to output deltas
3. **Identify structure** — magic bytes, length fields, checksums, null terminators
4. **Find the parser** — strings + strace + ltrace will point to the library or function
5. **Fuzz the boundaries** — truncate, extend, corrupt each field in isolation
6. **Re-derive the spec** — write it down; it forces precision

Useful tools: `hexdump -C`, `xxd`, `010 Editor`, `Wireshark`, `scapy`, `binwalk`,
`imhex`, `frida`, `ghidra`, custom struct parsers in Python (`struct`, `construct`).

---

## Hacker Ethics Embedded in Method

The hacker mindset is *not* "break things for fun." It's "understand things deeply
enough that you *could* break them, and use that understanding to build better
things." This includes:

- Responsible disclosure when you find real vulns
- Minimal footprint: don't touch what you don't need to understand
- Document what you find, so others don't have to rediscover it
- Distinguish "can I" from "should I" — the skill is amoral; the person wielding it is not

---

## Applying This Skill

When the user has a specific problem:

1. **Identify the system type** — software, protocol, social/organizational, physical
2. **Map the trust boundaries** — where does untrusted data enter trusted context?
3. **Pick the reframe** — which lateral thinking pattern applies?
4. **Generate hypotheses** — at least 3 distinct angles before committing to one
5. **Propose minimal experiments** — what's the cheapest test that discriminates between hypotheses?
6. **Build up from primitives** — PoC first, polish later

When the user needs a mindset shift:
- Point out the implicit assumption they're making
- Ask "what's the adversary's move here?"
- Suggest the inversion: design the perfect exploit, then fix it

---

## Quick Reference: Common Vulnerability Classes

| Class | Core Pattern | Where to Look |
|-------|-------------|---------------|
| Buffer overflow | Trust length field | Unbounded copy ops |
| Format string | Trust content as format | printf-family, logging |
| TOCTOU | Gap between check and use | File ops, stat() before open() |
| Injection | Trust input as code/query | SQL, shell, LDAP, eval() |
| Integer overflow | Trust arithmetic result | Size calculations, array indexing |
| Use-after-free | Trust pointer validity | Manual memory management |
| Confused deputy | Trust caller identity | CSRF, setuid binaries |
| Symlink attack | Trust path resolution | Temp files, predictable names |
| Deserialization | Trust serialized data | pickle, yaml.load, Java serialization |
| Logic bug | Trust state machine | Auth flows, payment flows |

---

## References

- "The Art of Exploitation" — Erickson: best intro to the physical reality of memory
- Phrack archives: primary source, adversarial thinking at its purest
- Project Zero blog: modern vuln research methodology
- CTFtime.org writeups: applied pattern recognition across vuln classes
- "A is for Attacker" — Saltzer & Schroeder's 8 principles: still the canonical threat model framework