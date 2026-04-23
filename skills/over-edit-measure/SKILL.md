---
name: over-edit-measure
description: >
  Measures over-editing in Python code diffs — quantifies how much a model or developer changed
  beyond what was strictly necessary. Use this skill whenever the user wants to: evaluate whether
  an AI coding tool (Claude Code, Copilot, Cursor, etc.) over-rewrote code, measure the "faithfulness"
  of a code edit, benchmark multiple diffs for edit minimality, compare a model's patch against a
  known minimal fix, or produce a per-function report of Levenshtein distance and Cognitive
  Complexity delta. Trigger on phrases like "measure over-editing", "how much did it rewrite",
  "was that a minimal fix", "compare these diffs", "over-edit benchmark", or any request to score
  or quantify the scope of a code change.
---

# Over-Edit Measurement Skill

Measures two key metrics from the [minimal editing research](https://nrehiew.github.io/blog/minimal_editing/):

- **Token-level Normalized Levenshtein Distance** — how much the code changed at the token level, normalized so functions of different sizes are comparable.
- **Added Cognitive Complexity (CC)** — how much harder to understand the modified code became, per function.
- **Patch Score S** (when a ground-truth minimal fix is available) — `S = D_model - D_true`. Zero is perfect; positive means over-editing.

## Dependency

The skill uses `cognitive-complexity`. Install once if needed:
```bash
pip install cognitive-complexity --break-system-packages
```

The measurement script is at `scripts/measure.py`.

## Verdict thresholds

| Normalized Levenshtein | Verdict  |
|------------------------|----------|
| 0.00 – 0.05            | ✅ minimal   |
| 0.05 – 0.15            | 🟡 slight    |
| 0.15 – 0.30            | 🟠 moderate  |
| 0.30+                  | 🔴 excessive |

---

## Workflow

### 1. Collect the inputs

Determine which case applies:

**Single diff**: user provides two code snippets or files (original + modified), optionally a ground-truth minimal fix.

**Batch**: user provides multiple pairs (e.g., several test problems, a CSV, or a folder of `original_N.py` / `modified_N.py` files).

If the user pastes code inline, write it to temp files before running the script.

### 2. Run the measurement script

**Single pair (CLI):**
```bash
python3 scripts/measure.py \
  --original original.py \
  --modified modified.py \
  [--ground-truth groundtruth.py] \
  [--format text|json]
```

**Single pair (stdin, good for inline code):**
```bash
python3 scripts/measure.py <<'EOF'
{"original": "...", "modified": "...", "ground_truth": "..."}
EOF
```

**Batch (JSON file):**
```bash
python3 scripts/measure.py --batch batch.json
```

Batch JSON format:
```json
[
  {
    "name": "bubble_sort_fix",
    "original": "path/to/original.py",
    "modified": "path/to/modified.py",
    "ground_truth": "path/to/gt.py"   // optional
  }
]
```

The script can also accept a list via stdin in the same format.

### 3. Present the report

The text output is human-readable with per-function CC breakdowns. For batch runs, always include the summary section.

If the user wants JSON output (e.g., to pipe into another tool), use `--format json`.

### 4. Interpret and explain the results

After printing the report, add a brief interpretation:

- **Levenshtein** above 0.15 usually indicates the model rewrote logic it didn't need to touch.
- **Added CC** above 0 means the modified code is harder to read, even if correct.
- **Patch score S > 0.10** is a meaningful over-edit signal when ground truth is available; the blog post found frontier models ranging from 0.06 (Claude Opus 4.6) to 0.44 (GPT-5.4).
- If CC *decreased* (negative delta), flag this too — unnecessary simplification is also an unwanted change in brown-field edits.

### 5. Handling non-Python code

This skill is currently Python-only (tokenization and CC both rely on the Python AST). For other languages, you can:
- Still compute a *line-level* Levenshtein using `difflib.unified_diff` as a rough proxy.
- Explain to the user that CC measurement requires Python.

---

## Example inline usage

User: "Here's the original and what Claude Code produced. Was it a minimal fix?"

1. Write each snippet to a temp file: `/tmp/orig.py`, `/tmp/mod.py`
2. Run: `python3 scripts/measure.py --original /tmp/orig.py --modified /tmp/mod.py`
3. Present the report and interpretation.

## Output structure (JSON mode)

```json
[
  {
    "name": "sample",
    "normalized_levenshtein": 0.0613,
    "verdict": "slight",
    "cognitive_complexity": {
      "per_function": {
        "my_func": {"original": 4, "modified": 5, "delta": 1}
      },
      "added_cc": 1,
      "removed_cc": 0,
      "net_cc_delta": 1
    },
    "patch_score": {
      "d_true": 0.0156,
      "d_model": 0.0613,
      "patch_score": 0.0457
    }
  }
]
```
