# Workstream 04 — Rule partition + typed placement maps

**Status**: implemented  
**Depends on**: 01  
**Unblocks**: 05

## Goal

Keep **[rules.py](../../placement/rules.py)** as **one logical rule set**, but expose **named partitions** (`ROLE_RULES`, then **`CHINH_TINH_RULES`**, **`PHU_TINH_RULES`**, **`TU_HOA_RULES`**) so the ontology is obvious. Use **one** instance of the existing `PlacementRuleCompiler` for natal placement: register each list on that compiler so relative refs (including sao → palace anchors like `menh`) stay in **one** connected spec map and **`SpecializedPlacementRules`** structural validation stays meaningful.

Downstream (`resolve_natal_placement` → **`NatalPlacement`**, then `LaSoBuilder` in workstream 05) carries **`role_positions: dict[Role, DiaChi]`** and **`sao_positions: dict[ComponentId, DiaChi]`** by **partitioning** the single resolved flat map (ids that match `Role` vs everything else). **No second compiler class.**

**Catalog vs rules consistency** (every placement id exists in the JSON-backed catalog) is **not** implemented here; it runs **once inside `LaSoBuilder.build`** (workstream 05).

## Background

`Cung` separates `role: CungRole` and `saos: tuple[Sao, ...]`. A flat `dict[ComponentId, DiaChi]` mixes palace labels and star ids. Partitioning after **one** resolve gives typed maps without splitting the dependency graph across two compiler instances (which would duplicate anchors or weaken validation).

## Public API

In [rules.py](../../placement/rules.py): **`ROLE_RULES`**, **`CHINH_TINH_RULES`**, **`PHU_TINH_RULES`**, **`TU_HOA_RULES`** (declarative lists only).

In [bundle.py](../../placement/bundle.py):

- **`get_default_placement_rule_compiler() -> PlacementRuleCompiler`** — registers `ROLE_RULES` then the three sao-side lists on one compiler (supported default factory; no separate role/sao compiler factories).

In [natal_placement_resolver.py](../../builder/natal_placement_resolver.py):

- **`resolve_natal_placement(context, compiler=...) -> NatalPlacement`** — compile + resolve + partition (default compiler from **`bundle.get_default_placement_rule_compiler`** when `compiler` omitted).
- **`NatalPlacement`** (`frozen=True`): **`role_positions`**, **`sao_positions`** — partition using `Role` membership on string ids.

**Do not** add `src/refactored/placement/integrity.py` or separate validate call sites in this workstream.

## Specific changes

- [rules.py](../../placement/rules.py): rule lists only.
- [bundle.py](../../placement/bundle.py): **`get_default_placement_rule_compiler`**.
- [natal_placement_resolver.py](../../builder/natal_placement_resolver.py): **`resolve_natal_placement`**; **`NatalPlacement`** dataclass.

## Out of scope

- `LaSoBuilder` aggregate and catalog guard (workstream 05).
- Primitives / engine changes beyond using the typed maps.
- “Every catalog JSON row has a placement rule.”

## Acceptance criteria

- **`get_default_placement_rule_compiler`** (in `bundle.py`) wires `ROLE_RULES` and the three sao-side lists in one registration graph.
- **`resolve_natal_placement`** returns **`NatalPlacement`** with partitioned **`role_positions`** / **`sao_positions`** for default and custom `compiler=`.
- Tests: default compiler compiles and resolves for a known `NatalContext`; partition puts palace ids under `Role`, stars under `sao_positions` shape.
- All existing tests pass.
