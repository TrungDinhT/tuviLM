# Placement Rules

This document records the implemented placement-rule architecture. Layer and
context assembly are documented in `layers_contexts_and_assembly.md`.

## Rule Graph

Placement rules form one static rule graph. Natal, period, and `TU_HOA_PHAI`
assembly do not own separate rule lists; they use context and scope selection
to choose which parts of the graph participate in a given layer.

Static rule facts are grouped by component/domain concern under
`placement/rules/data/*.yaml`:

- Cung roles
- chính tinh
- phụ tinh
- tuần / triệt
- tứ hóa

The data files describe rule kind and parameters only. They do not import
Python paths or contain arbitrary expressions.

## Declaration Pipeline

`placement/rules/loader.py` is the package-level entrypoint for YAML-backed
rule groups. It loads `placement/rules/data/*.yaml`, validates declaration
objects, and delegates registration into the placement registry.

Pipeline:

```text
placement/rules/data/*.yaml
  -> typed declaration models
  -> declaration validation
  -> registration into PlacementRegistry
  -> PlacementRuleCompiler
  -> PlacementEngine
```

The implementation is split by responsibility:

- `placement/rules/declarations/models.py`: internal typed declaration models
- `placement/rules/declarations/validation.py`: declaration group validation
- `placement/rules/declarations/resolvers.py`: closed YAML symbol names to
  Python callables
- `placement/rules/registration.py`: declarations to `AbsolutePositionSpec` /
  `RelativePositionSpec`
- `placement/rules/positions/absolute.py`: root absolute placement formulas
- `placement/rules/positions/relative.py`: derived relative position helpers

## Closed Symbol Resolution

YAML declarations reference named formulas and transforms through closed
resolver maps. This preserves authorable data while keeping executable behavior
in Python.

Examples of absolute formula symbols:

- `menh_position`
- `tuvi_position`
- `thai_tue_position`
- `loc_ton_position`
- `dau_quan_position`
- `trang_sinh_position`
- `tuan_positions`
- `triet_positions`

Examples of transform symbols:

- `same`
- `xung_chieu`
- `nhi_hop`
- `luc_hai`
- `tam_hop`
- `mirror_across`
- `move_by_dia_chi`
- `move_by_birth_hour`
- `move_by_birth_month`
- `move_by_birth_date`
- `move_by_van_direction`

These names are intentionally explicit and finite. Adding a new symbol requires
adding Python implementation and registering it in
`placement/rules/declarations/resolvers.py`.

## Registration

Declarations register directly into `PlacementRegistry` using the same
`AbsolutePositionSpec` and `RelativePositionSpec` objects as hand-written rules.
This keeps the compiler and engine independent from YAML.

`placement/rules/registration.py` owns the declaration-to-registry bridge. It
handles special declaration shapes such as circles, offset groups, Tuần/Triệt
pairs, and Tứ Hóa mappings while preserving the core placement graph contract.

## Context And Scope

Placement formulas accept structural placement contexts. The same rule graph can
therefore be compiled with `NatalContext`, period contexts, or
`TuHoaPhaiContext` as long as the selected rules only need attributes provided
by that context.

Layer scopes live in `placement/scopes.py`. During scoped compilation, seeded
natal dependencies can be rewritten into absolute anchors so period and
`TU_HOA_PHAI` overlays do not need to resolve the whole natal graph again.
