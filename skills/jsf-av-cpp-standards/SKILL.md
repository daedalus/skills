---
name: jsf-av-cpp-standards
description: Reference and apply the Joint Strike Fighter (JSF) Air Vehicle C++ Coding Standards (Doc. No. 2RDU00001 Rev C, "AV Rules") — the Lockheed Martin/MISRA-derived safety-critical C++ standard used in avionics and other high-assurance software. Use this skill whenever the user asks to review, audit, or lint C++ code against the JSF/AV rules or against safety-critical C++ coding standards generally; asks about a specific "AV Rule" by number; wants to write safety-critical, MISRA-style, or DO-178B-adjacent C++ code; asks about coding standards for embedded, avionics, automotive, or other high-integrity C++ systems; or references "JSF", "Air Vehicle coding standards", "2RDU00001", or similar. Also use it to explain the rationale behind a specific rule, find which rule(s) a code snippet violates, or draft a project's own coding standard based on this one.
---

# JSF Air Vehicle C++ Coding Standards

This skill packages the full text of the **Joint Strike Fighter Air Vehicle C++ Coding Standards**
(Doc. No. 2RDU00001 Rev C, December 2005, Lockheed Martin — distribution unlimited, publicly
released). It contains 228 numbered "AV Rules" governing safety-critical C++ development, built
on top of the MISRA C guidelines and a Vehicle Systems Safety-Critical C standard, plus a full
appendix of code examples.

Use this skill to check code against the standard, look up or explain a specific rule, or help
someone write new C++ that already conforms to it. Don't rely on memory for exact rule text or
numbers — always look them up in the bundled reference files, since misquoting a "shall" rule
number or rationale defeats the point of citing a standard.

## Reference files

- `references/rule-index.md` — a table of all 228 AV Rules with rule number, MISRA
  cross-reference (where one exists), and a one-line summary. **Start here** to find the rule(s)
  relevant to a question or a piece of code.
- `references/standards-body.md` — the full text of the standard: introduction, general design
  principles (coupling/cohesion, size/complexity), and all 228 rules with their complete
  statement, rationale, and any exceptions, organized under the original section numbering
  (4.4 Environment, 4.9 Style, 4.10 Classes, 4.13 Functions, 4.22 Pointers & References, etc.).
- `references/appendix-a-examples.md` — Appendix A: worked code examples ("do this / not this")
  for many of the rules, referenced by rule number.

Appendix B (compliance/tooling checklist) is not included — it referred to an external LDRA
tool-mapping spreadsheet, not standard content.

## How to use this skill

### Looking up or explaining a specific rule
Search `rule-index.md` for the rule number or topic, then read the corresponding entry in
`standards-body.md` for the exact wording, rationale, and exceptions. Quote the rule number and
its "should/will/shall" strength (see below) rather than paraphrasing loosely — the distinction
is load-bearing in this standard. If Appendix A has an example for that rule, pull it in too.

### Reviewing or auditing C++ code against the standard
1. Skim `rule-index.md` and identify which rule categories plausibly apply to the code at hand
   (e.g., naming, class design, pointers/references, memory allocation, flow control,
   templates, exceptions).
2. Read the full rule text for each candidate rule in `standards-body.md` before judging
   compliance — summaries in the index are for triage only, not for citing.
3. Go through the code and flag violations, citing the exact rule number, e.g. "AV Rule 143
   (shall): ... — violated here because ...". Distinguish clearly between:
   - **shall** — mandatory, verified; a real violation to flag as such
   - **will** — mandatory but not formally verified (often naming/style conventions)
   - **should** — advisory; note as a recommendation, not a hard violation
4. Where useful, show the corrected code alongside the flagged snippet.
5. Don't invent violations for rules not in this document — if something looks like bad
   practice but isn't covered by an AV Rule, say so as general advice, separate from standard
   compliance.

### Writing new code to conform to the standard
Apply the relevant "shall"/"will" rules as you write (naming conventions in 4.9, class/ctor/dtor
rules in 4.10, function rules in 4.13, pointer/reference rules in 4.22, etc.), and mention which
rules informed non-obvious choices (e.g., why a base class destructor is virtual, why a
conversion is explicit). If a deviation is genuinely necessary, say so explicitly and note that
the real standard requires documented, approved deviations for "shall"/"will" rules (AV Rules
4–7) — this skill can flag the need for a deviation but can't grant the approval itself.

### Drafting a derived/house coding standard
If the user wants their own project standard based on this one, use `standards-body.md` as the
source of truth for what to keep, relax, or drop, and preserve the should/will/shall
terminology if they're aiming for a similarly enforceable document.
