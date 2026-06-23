# Codex Security Adapter

Guide any agent to find and invoke the right codex-security plugin files for security tasks. This skill is a **router** — it maps user intent to specific files, scripts, and workflows inside `~/.codex/.tmp/plugins/plugins/codex-security/`.

## Plugin Root

All paths below are relative to:

```
~/.codex/.tmp/plugins/plugins/codex-security/
```

Canonical variable: `PLUGIN=~/.codex/.tmp/plugins/plugins/codex-security`

---

## Intent → File Map

### "Scan my repo for vulnerabilities"
→ `$PLUGIN/skills/security-scan/SKILL.md` — orchestrator skill, runs 4 phases in order:
1. Threat model
2. Finding discovery
3. Validation
4. Attack path analysis

Supporting references:
- `$PLUGIN/skills/security-scan/references/scan-artifacts-and-ledger.md`
- `$PLUGIN/skills/security-scan/references/repository-wide-scan.md`
- `$PLUGIN/skills/security-scan/references/repo-wide-artifacts-and-ledger.md`
- `$PLUGIN/skills/security-scan/references/repo-wide-high-impact-families.md`
- `$PLUGIN/skills/security-scan/references/repo-wide-instance-expansion.md`
- `$PLUGIN/skills/security-scan/references/repo-wide-validation-closure.md`

### "Scan this PR / diff / commit"
→ `$PLUGIN/skills/security-diff-scan/SKILL.md` — Git-backed change set review

Supporting: `$PLUGIN/scripts/generate_rank_input.py` — generates worklists from diffs

### "Deep / exhaustive scan"
→ `$PLUGIN/skills/deep-security-scan/SKILL.md` — multi-pass, worker-specific threat models

### "Build a threat model for this repo"
→ `$PLUGIN/skills/threat-model/SKILL.md`
→ `$PLUGIN/skills/threat-model/references/threat-model-guidance.md`

### "Find vulnerabilities in this code"
→ `$PLUGIN/skills/finding-discovery/SKILL.md` — candidate finding discovery

### "Validate this finding"
→ `$PLUGIN/skills/validation/SKILL.md`
→ `$PLUGIN/skills/validation/references/validation-guidance.md`

### "Trace the attack path for this finding"
→ `$PLUGIN/skills/attack-path-analysis/SKILL.md`
→ `$PLUGIN/skills/attack-path-analysis/references/attack-path-facts.md`
→ `$PLUGIN/skills/attack-path-analysis/references/severity-policy.md`

### "Fix this security finding"
→ `$PLUGIN/skills/fix-finding/SKILL.md`

### "Triage these existing findings / CVEs / advisories"
→ `$PLUGIN/skills/triage-finding/SKILL.md`
→ `$PLUGIN/skills/triage-finding/references/triage-result-contract.md`
→ `$PLUGIN/skills/triage-finding/references/github-rest-intake.md`

### "Track findings in Linear / Jira / GitHub"
→ `$PLUGIN/skills/track-findings/SKILL.md`
→ `$PLUGIN/skills/track-findings/references/jira.md`
→ `$PLUGIN/skills/track-findings/references/github-security-advisories.md`

---

## Python Scripts — Direct Invocation

These scripts work without the MCP server. Run them directly.

### Scan worklist generation
```bash
# From a diff (PR/commit/branch)
python $PLUGIN/scripts/generate_rank_input.py make-diff-rank-input \
  --repo <repo_root> --base <base_ref> --mode revisions --head <head_ref> \
  --out <output_dir>/rank_input.jsonl

# From a local patch
python $PLUGIN/scripts/generate_rank_input.py make-diff-repo-input \
  --repo <repo_root> --base <base_ref> --mode local-patch \
  --out <output_dir>/rank_input.jsonl

# Copy to deep review input
python $PLUGIN/scripts/generate_rank_input.py copy-deep-review-input \
  --rank-input <output_dir>/rank_input.jsonl \
  --out <output_dir>/deep_review_input.jsonl
```

### Finalize scan (seal artifacts)
```bash
python $PLUGIN/scripts/finalize_scan_contract.py \
  --scan-dir <scan_dir> --source-root <repo_root>
```

### Validate report format
```bash
python $PLUGIN/scripts/validate_report_format.py \
  --scan-dir <scan_dir>
```

### Config preflight
```bash
python $PLUGIN/scripts/config_preflight.py \
  --profile <security_scan|security_diff_scan|deep_security_scan> \
  --plugin-dir $PLUGIN
```

### Workbench state (SQLite)
```bash
# Full state management — call with subcommands:
# create-workspace, save-workspace, start-scan, complete-scan,
# fail-scan, get-scan, update-progress, list-findings, export-findings, etc.
python $PLUGIN/scripts/workbench_db.py <subcommand> [args...]
```

### Other utilities
```bash
python $PLUGIN/scripts/validate_tracking_source.py   # validate sealed scan for tracking
python $PLUGIN/scripts/snapshot_sqlite.py             # SQLite snapshot
python $PLUGIN/scripts/filesystem_identity.py         # filesystem identity helpers
python $PLUGIN/scripts/finding_preview.py             # bounded finding details
python $PLUGIN/scripts/report_projection.py           # JSON → markdown report
python $PLUGIN/scripts/workbench_source_excerpt.py    # source excerpts from sealed revisions
python $PLUGIN/scripts/config_preflight.py            # capability preflight check
```

---

## JSON Schemas — Structured Output

Use these to validate or generate scan artifacts:

| Schema | Path | Purpose |
|--------|------|---------|
| Scan manifest | `$PLUGIN/schemas/scan-manifest.schema.json` | Top-level completed scan document |
| Findings | `$PLUGIN/schemas/findings.schema.json` | Array of finding objects with severity, CWE, attack paths |
| Coverage | `$PLUGIN/schemas/coverage.schema.json` | Scan completeness, surfaces, dispositions |

### Example completed scan (reference)
- `$PLUGIN/examples/completed-scan/scan-manifest.json`
- `$PLUGIN/examples/completed-scan/findings.json`
- `$PLUGIN/examples/completed-scan/coverage.json`

---

## Reference Documents

### Shared (top-level)
| File | When to read |
|------|-------------|
| `$PLUGIN/references/scan-artifacts.md` | Any scan — defines artifact directory layout |
| `$PLUGIN/references/final-report.md` | Final reporting — JSON authoring + markdown projection |
| `$PLUGIN/references/scan-contract.md` | Machine-readable scan contract semantics |
| `$PLUGIN/references/finding-detail-fields.md` | Rich finding fields (codeEvidence, rootCause, attackPath) |
| `$PLUGIN/references/sarif-adapter.md` | SARIF 2.1.0 export |
| `$PLUGIN/references/static-finding-assessment.md` | Static evidence assessment guidance |
| `$PLUGIN/references/config-preflight.md` | Preflight workflow and remediation |
| `$PLUGIN/references/shared-hard-rules.md` | Hard rules for every scan workflow |

---

## Workflow Without MCP Server

For agents that cannot use the MCP server (non-Codex environments):

1. **Read the top-level SKILL.md** for the task (e.g., `security-scan/SKILL.md`)
2. **Follow the phase sequence** — each skill is self-contained
3. **Call Python scripts directly** for scan state, worklist generation, and finalization
4. **Use JSON schemas** to validate output artifacts
5. **Read reference docs** for artifact paths, hard rules, and report format

The SKILL.md files reference each other via `$threat-model`, `$finding-discovery`, `$validation`, `$attack-path-analysis` — treat these as "load and execute that skill's workflow."

---

## Scan Artifact Directory Convention

Default scan output goes to:
```
<tmpdir>/codex-security-scans-<random>/
  <scan_id>/
    scan-manifest.json
    findings.json
    coverage.json
    threat-model.md
    discovery/
      rank_input.jsonl
      deep_review_input.jsonl
      worklist.jsonl
      coverage-ledger.jsonl
    validation/
      per-finding/
        <finding-id>/
          validation-report.md
    attack-path/
      per-finding/
        <finding-id>/
          attack-path-report.md
```

Override with `--scan-dir` on Python script calls.
