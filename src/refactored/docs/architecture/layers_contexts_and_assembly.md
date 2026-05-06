# Layers, Contexts, and Assembly

This document records the implemented layer/context foundation and build
pipeline. Domain formulas are summarized in `../domain_context.md`.

## Layer Identity

`LayerKind` describes the category of a layer:

- `NATAL`
- `TIEU_HAN`
- `DAI_HAN`
- `LUU_NIEN_DAI_HAN`
- `TU_HOA_PHAI`

`LayerId` describes one exact layer. It is a union of explicit frozen value
objects:

- `NatalLayerId`
- `TieuHanLayerId(year)`
- `DaiHanLayerId(start_age, end_age)`
- `LuuNienDaiHanLayerId(year)`
- `TuHoaPhaiLayerId(source_dia_chi)`

`kind` is a read-only property, not an init field, so callers cannot construct
an inconsistent layer identity.

## Context Protocols

Generic structural protocols live in `context/protocol.py`:

- `PlacementContext`
- `LayerContext`
- `PeriodContext`

They are intentionally broad. Placement primitives use whichever attributes a
concrete context provides.

Concrete contexts live outside the protocol module:

- `NatalContext`
- `TieuHanContext`
- `DaiHanContext`
- `LuuNienDaiHanContext`
- `TuHoaPhaiContext`

Each layer-producing context exposes `layer_id`. Period contexts also expose
`focus_position`.

## Natal Assembly

`assembly/natal.py` builds the base `TinhBan`.

Pipeline:

1. Compile all natal placement rules with `NatalContext`.
2. Resolve the full natal graph with `PlacementEngine`.
3. Build `CungId` values from resolved roles, `cung_than`, and Cung Thiên Can.
4. Build `natal_layer` after removing structural role ids.
5. Build static period focus maps.
6. Return `TinhBan`.

`TU_HOA_PHAI` layers are not built eagerly during natal assembly.

## Period Focus

`context/period_focus.py` owns period focus formulas and static focus maps.

Implemented values:

- `TenYearRange`
- `DaiHanFocusMap`
- `PeriodFocusMaps`
- `build_tieu_han_focus_map(...)`
- `build_dai_han_focus_map(...)`
- `luu_nien_dai_han_focus_position(...)`

`TIEU_HAN` and `DAI_HAN` focus maps are static for one natal chart and are
stored on `TinhBan`. `LUU_NIEN_DAI_HAN` focus is derived from the matching
`DaiHanContext`.

## Period Context Factory

`context/period.py` exposes `PeriodKind` and `build_period_context(...)`.

`LaSo.period_layer(kind, year)` uses this factory so callers do not need to
construct concrete period contexts themselves.

Concrete context notes:

- `TieuHanContext` stores `year` and `focus_position`; lunar year is cached.
- `DaiHanContext` stores `age_range`, `focus_position`, and the Thiên Can of
  the focused natal Cung; it intentionally does not store `year`.
- `LuuNienDaiHanContext` stores `year` and `focus_position`.

## Scoped Compilation

`PlacementRuleCompiler.compile(...)` supports:

```python
compile(context, scope=..., seed=...)
```

When a scope is supplied, the compiler specializes only the requested
component ids plus their unseeded dependency closure. If a relative dependency
is outside the scope but present in `seed`, the compiler rewrites it as an
absolute anchor.

This allows period and `TU_HOA_PHAI` contexts to provide only the attributes
needed by their scoped rules.

## Period Layer Assembly

`assembly/period.py` materializes one period layer:

1. Select scope from `context.layer_id.kind`.
2. Build a natal seed from `natal_layer.by_component` plus
   `tinh_ban.natal_role_positions`.
3. Compile with `scope` and `seed`.
4. Resolve positions.
5. Build `PlacementLayer` with `context.layer_id` and
   `context.focus_position`.

## Tu Hoa Phai Assembly

`assembly/tu_hoa_phai.py` can materialize `TU_HOA_PHAI` layers from a
`TuHoaPhaiContext`.

The assembly exists, but the stable `LaSo` query API for requesting these
layers is still pending and tracked in `../plan/01_remaining_work.md`.

