---
name: fgts-naming-convention
description: FGTS — From General To Specific. A deterministic, scope-descending identifier system for files, variables, configs, and APIs. Makes names sortable, groupable, and self-documenting.
---

# FGTS — From General To Specific
> A deterministic, scope-descending identifier system for files, variables, configs, and APIs · v1.0

---

## Core Principle

Every identifier is a path through a conceptual namespace, moving from the broadest context down to the most specific detail. Reading left to right is like zooming in on a map — each segment narrows the scope of the one before it.

This makes names **sortable**, **groupable**, and **self-documenting** without external tooling. The convention applies uniformly to filenames, variables, config keys, API routes, and database fields.

---

## Segment Anatomy

```
<domain>_<system>_<entity>_<attribute>_<qualifier>
```

| Position | Level | Role | Examples |
|---|---|---|---|
| 1 | **Domain** | Top-level context | `net` `auth` `db` `ui` `cfg` |
| 2 | **System** | Subsystem / module | `flow` `session` `query` `form` `cache` |
| 3 | **Entity** | Object / resource | `iface` `user` `table` `input` `entry` |
| 4 | **Attribute** | Property / metric | `bytes` `count` `ts` `id` `name` `rate` |
| 5 | **Qualifier** | Direction / state / variant | `in` `out` `prev` `max` `raw` `err` |

**Canonical example:**

```
net_flow_iface_bytes_in
│   │    │     │     └─ qualifier : inbound direction
│   │    │     └─────── attribute : byte count
│   │    └───────────── entity    : network interface
│   └────────────────── system    : NetFlow pipeline
└────────────────────── domain    : network monitoring
```

Segments are separated by `_` (snake_case). Use `-` (kebab-case) for filenames and URLs. Omit trailing segments when specificity is unambiguous in context.

---

## Rules

1. **Left-to-right specificity is mandatory.** Never place a narrower segment before a broader one. `auth_session_user_id` is valid; `id_user_session_auth` is not.

2. **All lowercase, no spaces.** Snake_case for code identifiers; kebab-case for file paths and URLs. Mixed case within segments is forbidden.

3. **Use abbreviations consistently.** Establish a project-level glossary (e.g. `ts` = timestamp, `cnt` = count, `cfg` = config). Never mix abbreviated and full forms of the same word.

4. **Omit obvious segments.** Inside the `auth` module, `session_id` is sufficient — prepending `auth_` is redundant. Apply the innermost-scope rule.

5. **No verbs in data names.** Verbs belong in function/method names. Data identifiers describe *what a thing is*, not what you do with it. `db_query_result_rows` not `db_get_query_rows`.

6. **Qualifiers are the last resort.** Only add a Level 5 qualifier when the attribute is genuinely ambiguous without it. `bytes_in` vs `bytes_out` is valid. `count_final` is a smell.

7. **Plural only at the entity level.** `net_flow_ifaces_count` — the entity (`ifaces`) is plural because it's a collection. Attributes and qualifiers stay singular.

---

## Examples by Context

| Context | FGTS Identifier | Meaning |
|---|---|---|
| Variable | `net_flow_iface_bytes_in` | Inbound byte count for a specific interface in the NetFlow pipeline |
| Config key | `db_cache_ttl_sec` | TTL in seconds for the database cache layer |
| Filename | `auth-session-token-refresh.py` | Script for refreshing session tokens in the auth subsystem |
| API route | `/net/flow/iface/{id}/bytes` | REST endpoint exposing byte metrics for an interface |
| DB column | `auth_session_user_id` | FK to user within the session table of the auth schema |
| Metric | `net_flow_iface_pkt_drop_rate` | Packet drop rate per interface in the flow domain |
| CSS variable | `--ui-form-input-border-focus` | Border color token for focused state of form inputs |
| Env var | `DB_REPLICA_HOST_PRIMARY` | Hostname of the primary replica (SCREAMING_SNAKE) |

---

## Good vs. Bad

### ✗ Violations

```
getFlowBytesIn          # verb prefix + camelCase — wrong casing, wrong order
in_bytes_iface_net      # reversed specificity — qualifier before domain
iface_bytes             # missing domain context — collides across systems
netFlowIfaceByteIn      # camelCase — reserved for method/function names
```

### ✓ Correct

```
net_flow_iface_bytes_in       # all five levels, left-to-right, snake_case
net_flow_iface_bytes_out      # parallel structure — differs only at qualifier
net_flow_iface_pkt_cnt        # abbreviation used consistently per glossary
flow_iface_bytes_in           # domain omitted — valid inside a net-scoped module
net-flow-iface-report.md      # kebab-case for filename; same hierarchy
```

---

## Starter Abbreviation Glossary

| Abbrev | Full form | Abbrev | Full form |
|---|---|---|---|
| `ts` | timestamp | `cnt` | count |
| `cfg` | config | `pkt` | packet |
| `iface` | interface | `err` | error |
| `sec` | seconds | `ms` | milliseconds |
| `max` / `min` | maximum / minimum | `prev` / `cur` | previous / current |
| `req` / `res` | request / response | `raw` | unprocessed value |

---

*FGTS Naming Convention · From General To Specific · v1.0 · 2026*