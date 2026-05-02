# Workstream 04 — Compiler split (two instances)

**Status**: pending
**Depends on**: 01
**Unblocks**: 05

## Goal

Partition the single rule set in [rules.py](../../placement/rules.py) into two groups (roles, components) registered against two separate instances of the existing `PlacementRuleCompiler`. Downstream (`LaSoBuilder`, workstream 05) receives two typed position maps. **No new compiler classes.**

**Catalog vs rules consistency** (every placement id must exist in the JSON-backed catalog) is **not** implemented here; it runs **once inside `LaSoBuilder.build`** (workstream 05). That keeps a single choke point: nothing is asserted “meaningful” until a `LaSo` is built.

## Background

`Cung` already separates `role: CungRole` and `saos: tuple[Sao, ...]`. The placement pipeline today produces one flat `dict[ComponentId, DiaChi]` mixing both, which forces consumers to know the role-vs-component distinction by string id. By feeding the role rules and component rules to two compiler instances, downstream consumers get two typed maps. [component_catalog.py](../../builder/component_catalog.py) already loads **`CungRole` and other entities** from JSON into one id map; workstream 05’s single check uses that same catalog for **all** registered placement ids (roles + components).

## Public API to introduce

In [rules.py](../../placement/rules.py), expose the existing rule lists in a way that makes the partition obvious:

```python
COMPONENT_RULES: list[Rule] = [
    *CHINH_TINH_RULES,
    *PHU_TINH_RULES,
    *TU_HOA_RULES,
]
```

Replace `get_default_placement_rule_compiler()` with two factories:

```python
def get_default_role_compiler() -> PlacementRuleCompiler:
    compiler = PlacementRuleCompiler()
    compiler.register_rules(ROLE_RULES)
    return compiler

def get_default_component_compiler() -> PlacementRuleCompiler:
    compiler = PlacementRuleCompiler()
    compiler.register_rules(COMPONENT_RULES)
    return compiler
```

**Do not** add `src/refactored/placement/integrity.py` or separate `validate_role_ids` / `validate_component_ids` call sites in this workstream.

## Specific changes

- [rules.py](../../placement/rules.py): introduce `COMPONENT_RULES` aliases. Keep the existing per-section lists (`CHINH_TINH_RULES`, etc.) for clarity.
- Remove `get_default_placement_rule_compiler` (or keep it as a deprecated shim if any test still uses it; remove on cleanup).
- Update [placement_builder.py](../../builder/placement_builder.py) to:
  - Construct the two compilers via the new factories.
  - Compile each compiler against the same `NatalContext` and resolve into two maps (no catalog validation here):
    - `roles: dict[Role, DiaChi]` — keys converted from string id to `Role` enum members at this boundary.
    - `saos: dict[ComponentId, DiaChi]` (name of this map in downstream chart/layer APIs).
  - Expose both maps to downstream consumers (workstream 05 will read them).

## Out of scope

- The actual `LaSoBuilder` aggregate and catalog guard (workstream 05).
- Any change to primitives or engine.
- Enforcing the converse (“every JSON catalog row has a placement rule”).

## Acceptance criteria

- Two distinct compilers, each registered with its respective rule set; default factories wire the shipped rule lists correctly.
- Tests (see [08_testing_plan.md](08_testing_plan.md)): two factories produce distinct compilers; default registration round-trips compile+resolve for a known `NatalContext` without requiring catalog validation in this workstream.
- `placement_builder.PlacementBuilder.resolve_all()` (or its replacement) returns a typed pair `(roles_map, saos_map)`. If this would break existing callers, keep a back-compat wrapper that re-merges into a flat map and mark deprecated.
- All existing tests pass.
