---
name: search-as-code
allowed-tools:
  - Bash
  - Python
description: >
  Use this skill whenever a task requires multi-step, knowledge-intensive research that
  benefits from parallel search, iterative gap-filling, and structured synthesis. Triggers
  include: competitive analysis, literature reviews, data extraction from web results,
  finding and comparing multiple sources across vendors or time periods, security advisory
  research, market research, technology landscape surveys, academic paper discovery, and
  any task where a single search would clearly be insufficient. Also triggers on: "research",
  "find all", "compare across", "gather information about", "extract from the web", "scan
  for", "compile a list of", "run a search agent", "use SaC", "search as code". Prefer
  this skill over a plain web search whenever the task has multiple facets, requires
  verifying information across sources, or needs structured output extracted from results.
  Do not wait for the user to explicitly ask — if the task is clearly research-shaped,
  invoke this skill immediately.
---

# Search as Code (SaC)

An agentic search architecture where Claude generates Python code using a composable
Search SDK, executes it in a sandbox, and persists intermediate state across turns via
explicit filesystem serialization — producing higher-quality research with fewer tokens
than serial function-call-based search.

## How It Works

Rather than calling search as a black-box tool, Claude acts as the **control plane**:
it writes a Python program that orchestrates the search stack, executes that program,
inspects intermediate results, and iterates until it has enough evidence to synthesize.

The three layers:
1. **Claude** — reasons about strategy, generates code, decides when to synthesize
2. **Sandbox** — executes code deterministically (parallelism, filtering, aggregation)
3. **Agentic Search SDK** — composable primitives from raw retrieval to LLM subroutines

## Variants

| Variant | File | Runtime | Search backend |
|---------|------|---------|---------------|
| **CLI** | `sac.py` | Python subprocess | Brave API or Claude-simulated |
| **Browser** | `search-as-code.jsx` | React artifact | Claude-simulated (real search via proxy optional) |

The CLI and browser variants share the same agent protocol but the browser version uses
a richer response format — see [Browser (JSX) variant](#browser-jsx-variant) below.

## Setup

```bash
pip install anthropic rich requests
export ANTHROPIC_API_KEY=sk-...
```

**Search backend** — set one for real web search (otherwise results are simulated by Claude):

| Backend | Install | Env var | Best for |
|---------|---------|---------|----------|
| **Brave** | *(built-in)* | `BRAVE_SEARCH_API_KEY` | Keyword-heavy, site-scoped, CVE/exact-match queries |
| **Exa** *(optional)* | `pip install exa-py` | `EXA_API_KEY` | Semantic / conceptual queries — requires SDK extension (see below) |

Without a search API key, `SearchSDK` falls back to asking Claude to generate plausible
results. This is useful for demos and logic testing but **not for real research** — treat
simulated results as structured placeholders only.

**Sandbox hardening** (production):
```bash
pip install llm-sandbox[mcp-docker]   # Docker-isolated execution
```
Set `SANDBOX_BACKEND=docker` to replace the default `exec()`-based sandbox with a fully
isolated container. Recommended when the agent has network access or handles untrusted inputs.

Place `sac.py` anywhere on your path. Run:
```bash
python sac.py "Your research task here"
# or interactive:
python sac.py
```

## SDK Reference

All primitives are available in generated code as `sdk.*`.

### `sdk.search`

```python
# Single web search
results = sdk.search.web(query, limit=8)          # -> list[SearchResult]

# Parallel web searches — queries can be strings or dicts with a 'query' key
results = sdk.search.web_many(queries, limit_per_query=8, concurrency=6)
# -> list[list[SearchResult]]
```

`SearchResult` fields: `.url`, `.title`, `.snippet`, `.domain`

> **Note:** There is no `sdk.search.neural()` method and no `mode=` parameter on
> `web_many` in the base implementation. Neural/Exa search requires the extension
> described in [Extending the SDK](#extending-the-sdk).

### `sdk.llm`

```python
# Synthesize/extract insights from a list of items
answer = sdk.llm.synthesize(items, instruction)       # -> str

# Generate a search plan
plan = sdk.llm.plan(context, goal)                    # -> str

# Batch-extract structured records matching a schema
# Items must be dicts. Internally chunks at 10 items per LLM call.
records = sdk.llm.extract_many(items, instruction, schema={
    "field_name": str,   # type hints guide extraction
    "matches": bool,
    "confidence": float,
})                                                     # -> list[dict]
```

### `sdk.fs` — Filesystem state (persists across turns)

```python
sdk.fs.write(key, data)       # serialize any Python object (pickle)
data = sdk.fs.read(key)       # deserialize
keys = sdk.fs.list()          # list persisted keys
exists = sdk.fs.exists(key)   # check before reading
```

Prefer `sdk.fs` over in-memory variables for anything needed in a later turn. Explicit
serialization forces the model to be deliberate about what state matters.

### `sdk.utils`

```python
# ⚠ dedupe_by and filter_by require dict items, not SearchResult objects.
# Convert first: items = [vars(r) for r in results]  — or build dicts inline.
items = sdk.utils.dedupe_by(items, key="url")               # list[dict] -> list[dict]
items = sdk.utils.filter_by(items, field="domain", value="github.com")

summary = sdk.utils.summarize_coverage(items, by_fields=["vendor", "year"])
flat    = sdk.utils.flatten(list_of_lists)
text    = sdk.utils.join_result_fields(result)   # SearchResult -> "title | snippet"
```

> **No `sdk.utils.chunk`** — do not call it; it will raise `AttributeError`.
> `sdk.llm.extract_many` already chunks at 10 items internally; pass the full list.

## Agent Response Protocol

Each turn Claude returns **one JSON object** (no markdown fences):

**Code turn** — execute a search phase:
```json
{
  "turn_type": "code",
  "reasoning": "Brief explanation of this phase",
  "code": "# Python using sdk\nresults = sdk.search.web_many([...])"
}
```

**Synthesis turn** — final answer:
```json
{
  "turn_type": "synthesis",
  "reasoning": "What was found and how",
  "answer": "Complete answer to the task"
}
```

## Search Strategy Patterns

### Pattern 1 — Parallel fanout (Phase 1)

Fan out many query variants in parallel. Note: `dedupe_by` requires dicts — convert
`SearchResult` objects before passing.

```python
queries = [
    'site:arxiv.org "inference optimization" 2025',
    'site:github.com LLM serving throughput benchmark',
    '"speculative decoding" latency site:arxiv.org',
    '"KV cache compression" transformer 2024 2025',
]

raw = sdk.search.web_many(queries, limit_per_query=8, concurrency=6)
flat = sdk.utils.flatten(raw)

# Convert SearchResult -> dict before deduplication
items = [{"url": r.url, "title": r.title, "snippet": r.snippet, "domain": r.domain}
         for r in flat]
deduped = sdk.utils.dedupe_by(items, key="url")
sdk.fs.write("phase1_results", deduped)
```

### Pattern 2 — Gap analysis + backfill (Phase 2)

After Phase 1, identify sparse areas and generate targeted follow-up queries.

```python
results = sdk.fs.read("phase1_results")   # already dicts from Pattern 1
coverage = sdk.utils.summarize_coverage(results, by_fields=["domain"])
gap_queries = sdk.llm.synthesize(
    [{"coverage": coverage, "goal": "Find high-severity CVEs from 2024"}],
    instruction="Suggest 5 more site-scoped queries to fill coverage gaps. Return as JSON list."
)
# parse gap_queries and run sdk.search.web_many(...)
```

### Pattern 3 — Structured extraction (Phase 3)

Extract typed records from raw results with confidence filtering. Pass dicts to
`extract_many`; build them inline from SearchResult if needed.

```python
raw = sdk.fs.read("phase1_results")   # already dicts
records = sdk.llm.extract_many(
    raw,   # extract_many chunks internally — pass the full list
    instruction="Extract papers where the abstract describes a new training method.",
    schema={
        "matches": bool,
        "title": str,
        "method_name": str,
        "key_claim": str,
        "source_url": str,
        "confidence": float,
    }
)
verified = [r for r in records if r.get("matches") and r.get("confidence", 0) > 0.75]
sdk.fs.write("verified_records", verified)
```

### Pattern 4 — Inline LLM subroutine

Use `sdk.llm.synthesize` as an intermediate planning step mid-trajectory.

```python
seed_results = sdk.fs.read("phase1_results")   # dicts
plan = sdk.llm.plan(
    context=str([r["title"] for r in seed_results[:20]]),
    goal="Identify which vendors have the most coverage gaps"
)
sdk.fs.write("gap_plan", plan)
```

## Multi-Turn Trajectory Structure

A typical 3-turn trajectory:

| Turn | Phase | Key operations |
|------|-------|----------------|
| 1 | Broad fanout | `web_many` with 8–20 parallel queries, convert to dicts, `fs.write("phase1")` |
| 2 | Gap analysis + backfill | `fs.read("phase1")`, `llm.synthesize` for gaps, targeted `web_many` |
| 3 | Extract + synthesize | `llm.extract_many` on dict items, final answer |

For simple tasks (2 turns): fanout → synthesize.
For complex tasks (4–5 turns): fanout → gap analysis → backfill → extract → synthesize.

## Code Generation Guidelines

When writing code for the sandbox:

- **One phase per turn** — don't try to do everything in one code block
- **Always persist to `sdk.fs`** after collecting results — explicit serde outperforms REPL-style namespaces on long trajectories
- **Use `concurrency=6–12`** for `web_many` to maximize parallel throughput
- **Convert SearchResult to dict before utils calls** — `dedupe_by` and `filter_by` call `.get()` and will raise `AttributeError` on dataclasses
- **Don't pre-chunk for `extract_many`** — it chunks at 10 internally; pre-chunking adds boilerplate for no gain
- **Scope keyword queries precisely** — `site:` prefixes, exact-phrase constraints (`"CVE-2024"`), year filters
- **Filter early** — use `sdk.utils.filter_by` and `sdk.utils.dedupe_by` before passing to LLM calls
- **Confidence threshold** — filter `extract_many` results by `confidence > 0.75`
- **Check `sdk.fs.list()`** at the start of turns 2+ to understand available state

## Example Trajectories

### CVE Advisory Research

```python
# Turn 1: Fan out vendor-specific advisory queries
templates = [
    ("Mozilla", 'site:mozilla.org/security/advisories "CVE-2024" "Impact: high"'),
    ("Chrome",  'site:chromereleases.googleblog.com "High CVE-2024" stable'),
    ("Jenkins", 'site:jenkins.io/security/advisory "CVE-2024" "High" "Fix"'),
]
queries = [{"query": q} for _, q in templates]
hits = sdk.search.web_many(queries, limit_per_query=8, concurrency=12)
pages = sdk.utils.dedupe_by(
    [{"url": r.url, "title": r.title, "snippet": r.snippet, "domain": r.domain}
     for r in sdk.utils.flatten(hits)],
    key="url"
)
sdk.fs.write("advisory_pages", pages)
```

```python
# Turn 2: Extract structured CVE records
pages = sdk.fs.read("advisory_pages")   # dicts
records = sdk.llm.extract_many(pages,
    instruction="Extract CVEs where a vendor advisory names the fixed version.",
    schema={"cve": str, "vendor": str, "product": str,
            "fix_version": str, "source_url": str,
            "version_bound_to_cve": bool, "confidence": float}
)
verified = [r for r in records if r.get("version_bound_to_cve") and r.get("confidence", 0) > 0.75]
sdk.fs.write("cve_records", verified)
```

### Competitive Analysis

```python
# Turn 1: Parallel per-company searches
companies = ["OpenAI", "Anthropic", "Google DeepMind", "Mistral", "Meta AI"]
queries = [f"{co} model release announcement 2025" for co in companies]
raw = sdk.search.web_many(queries, limit_per_query=6, concurrency=8)
results = [{"url": r.url, "title": r.title, "snippet": r.snippet, "domain": r.domain,
            "company": co}
           for co, batch in zip(companies, raw) for r in batch]
sdk.fs.write("company_results", results)
```

## Browser (JSX) Variant

`search-as-code.jsx` is a self-contained React artifact that calls the Anthropic API
directly from the browser. It uses a richer response format and simulates search via
a second Claude call (no real search backend by default).

**Extended response format** (browser only):

Code turn:
```json
{
  "turn_type": "code",
  "reasoning": "...",
  "code": "# Python-style pseudocode shown in UI",
  "operations": [
    {"type": "web_search", "queries": ["query1", "query2"]},
    {"type": "fs_write",   "key": "phase1_results"},
    {"type": "fs_read",    "key": "phase1_results"},
    {"type": "llm_call",   "purpose": "gap analysis"}
  ],
  "next_turn_hint": "What the next turn will do"
}
```

Synthesis turn:
```json
{
  "turn_type": "synthesis",
  "reasoning": "...",
  "answer": "Complete answer",
  "sources": ["url1", "url2"],
  "stats": {
    "searches_run": 12,
    "results_processed": 87,
    "token_estimate": "~42K"
  }
}
```

The `operations` array drives actual execution: `web_search` operations trigger
`executeSearches(queries)`, and `fs_write`/`fs_read` operations update the simulated
`currentFs` dict in React state. The Python `code` field is rendered for display only —
it is not executed in the browser.

## Extending the SDK

The `AgenticSearchSDK` class in `sac.py` has four sub-SDKs you can extend:

- `SearchSDK` — add retrieval backends; `_search_one(query, limit)` is the extension point; must return `list[SearchResult]`
- `LLMSDKClient` — add extraction/synthesis patterns
- `FilesystemSDK` — swap pickle for JSON, SQLite, or a real key-value store
- `UtilsSDK` — add domain-specific helpers

**Wiring Exa** (neural search) — subclass `SearchSDK`:
```python
from exa_py import Exa

class ExaSearchSDK(SearchSDK):
    def __init__(self, client, brave_key=None):
        super().__init__(client, brave_key)
        self._exa = Exa(api_key=os.environ["EXA_API_KEY"])

    def neural(self, query: str, limit: int = 8) -> list[SearchResult]:
        """Semantic / embedding-based search via Exa."""
        results = self._exa.search_and_contents(query, num_results=limit, use_autoprompt=True)
        return [SearchResult(url=r.url, title=r.title or "", snippet=(r.text or "")[:300])
                for r in results.results]

# Instantiate with ExaSearchSDK instead of the default:
sdk = AgenticSearchSDK.__new__(AgenticSearchSDK)
sdk.search = ExaSearchSDK(client, brave_key)
sdk.llm    = LLMSDKClient(client)
sdk.fs     = FilesystemSDK(fs_dir)
sdk.utils  = UtilsSDK()
```

Once wired, call `sdk.search.neural(query, limit)` from generated code.

**Wiring llm-sandbox** (Docker isolation):
```python
# Replace Sandbox.execute() with:
from llm_sandbox import SandboxSession
with SandboxSession(lang="python", keep_template=True) as session:
    result = session.run(code)
```
Set `SANDBOX_BACKEND=docker` to activate. Provides CPU/memory limits, network isolation,
and automatic cleanup — essential when the agent accesses the open web.

## Troubleshooting

**`AttributeError: 'SearchResult' object has no attribute 'get'`** — you passed
`list[SearchResult]` to `dedupe_by` or `filter_by`. Convert first:
`items = [{"url": r.url, "title": r.title, "snippet": r.snippet, "domain": r.domain} for r in results]`

**`AttributeError: 'UtilsSDK' object has no attribute 'chunk'`** — `chunk` is not
implemented. Remove the call; `extract_many` chunks at 10 items internally.

**`AttributeError: 'SearchSDK' object has no attribute 'neural'`** — `neural()` is not
in the base `SearchSDK`. Use the Exa extension above or fall back to `sdk.search.web()`.

**JSON parse errors from agent** — the model returned markdown-wrapped JSON; the runtime
strips fences automatically, but very long outputs can overflow `max_tokens`. Increase it
in `SaCAgent`.

**Sandbox execution errors** — printed with a traceback; the agent receives the error and
can self-correct on the next turn. If errors recur, check that the generated code only
references SDK methods that exist.

**Empty or low-quality results** — without a real search backend, results are simulated
by Claude. For production tasks set `BRAVE_SEARCH_API_KEY` or wire Exa. Simulated results
are useful for validating pipeline logic but should not be trusted for factual research.

**Too many turns** — default `max_turns=6`. Increase in `SaCAgent.__init__` for complex
tasks (e.g. 200+ record extraction).

**Sandbox security** — the default `exec()`-based sandbox has no isolation. For tasks
involving untrusted input or open-web access, use `llm-sandbox` with Docker backend.

## Evals

Test cases live in `evals/evals.json`. Run against a task to verify the skill triggers
correctly and produces structured, accurate output.

```json
{
  "skill_name": "search-as-code",
  "evals": [
    {
      "id": 1,
      "prompt": "Find the five most-cited papers on speculative decoding published in 2024, with author names and arxiv links.",
      "expected_output": "A list of 5 papers with titles, authors, and arxiv URLs, sourced from real search results across multiple turns."
    },
    {
      "id": 2,
      "prompt": "Compare the pricing and context window of the latest models from OpenAI, Anthropic, and Google as of today.",
      "expected_output": "A structured comparison table with accurate, sourced data — not from training knowledge."
    },
    {
      "id": 3,
      "prompt": "List all high-severity CVEs patched by Mozilla in 2024 with fix versions from official advisories.",
      "expected_output": "Structured records with CVE IDs, products, fix versions, and mozilla.org source URLs. Confidence > 0.75 on all records."
    }
  ]
}
```
