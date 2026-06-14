---
name: extract-cach-cuc
description: Extract Tử Vi cách cục from book pages into the validated cach_cuc YAML and append to cach_cuc_reviewed.yaml.
disable-model-invocation: true
---

# Extract Cách Cục

Read book page(s) → write records in the cách cục condition language → validate, dedup, append.
Domain knowledge (scopes, group members, priority, special cases, merge rule) lives in
`reference.md` — read it first.

**Arguments (optional):** page number(s), optionally a main-star focus — e.g. `76` or
`76 thien_luong`. If omitted, ask which page(s) to read.

Helper CLI (auto-detects repo root, so it runs from anywhere):
```
.venv/bin/python .claude/skills/extract-cach-cuc/scripts/cc_tools.py <subcommand> ...
```

## Workflow

1. **Read.** The page(s) from `data/tuvitanbien/page_NNN.md`.
2. **Vocab & schema.** `cc_tools.py vocab` → ids (use only these, never guess). `cc_tools.py schema`
   → condition model shape + leaf types. Do not read `condition_models.py`; `schema` is derived from it.
3. **Extract.** Each distinct configuration the page describes = one record (a bullet or câu phú
   is the usual unit; split when a brightness variant or an added clause changes the rule).
   Follow `schema` for shape/leaf types and `reference.md` for priority and the special cases.
4. **Write tmp.** Delete `cach_cuc_reviewed_tmp.yaml` if present; write a fresh one starting with a
   single top-level `cach_cuc:` key.
5. **Gate.** `cc_tools.py check cach_cuc_reviewed_tmp.yaml cach_cuc_reviewed.yaml` → fix until it
   prints `CHECK: PASS`. Resolve any reported collision group with the merge rule in `reference.md`;
   if a colliding record already lives in `cach_cuc_reviewed.yaml`, update it there and drop the
   duplicate from tmp.
6. **Review.** Show a compact table (id, config, meaning, priority) plus every skip / merge /
   ambiguity decision. **Wait for approval** — hard gate.
7. **Append.** `cc_tools.py append cach_cuc_reviewed_tmp.yaml cach_cuc_reviewed.yaml`, then clear tmp.

## cc_tools.py subcommands

| Command | Purpose |
|---|---|
| `vocab` | Dump canonical ids: stars, roles, chi, can, brightness, scopes, group_names, modes (JSON). |
| `schema` | Dump condition model shape (record fields, leaf types, rules), auto-derived from the pydantic models. |
| `validate <file...>` | Pydantic-validate; report duplicate ids + unknown star ids. |
| `dedup <file...>` | Report records with identical conditions across the given files. |
| `check <tmp> <reviewed>` | Preflight gate: validate both + id clash + collisions. Exit ≠ 0 on any issue. |
| `append <tmp> <reviewed>` | Append tmp → reviewed iff `check` passes; re-validate result. |
