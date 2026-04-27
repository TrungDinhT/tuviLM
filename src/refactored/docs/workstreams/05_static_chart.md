# Workstream 05 — Static `LaSo` aggregate + `LaSoBuilder`

**Status**: pending
**Depends on**: 01, 04
**Unblocks**: 06

## Goal

Build the immutable `LaSo` aggregate that ties together the 12 `Cung`s with their `DiaChiEntity`, `ThienCanEntity`, static `CungRole`, `is_cung_than` flag, attached components (sao + tu hoa + tràng sinh + tuần/triệt), from the typed maps produced by workstream 04 and the `ComponentCatalog`.

## Background

Today, [Cung](../../component/cung.py) is a frozen dataclass with the right shape but is never constructed. The flat positions map is the end of the pipeline. This workstream is the first time the pipeline produces a *chart*.

## Public API to introduce

`src/refactored/chart/laso.py`:

```python
@dataclass(frozen=True)
class LaSo:
    natal: NatalContext
    cungs: tuple[Cung, ...]                              # length 12, ordered by DiaChi
    component_positions: dict[ComponentId, DiaChi]        # forward index, immutable
    role_positions: dict[Role, DiaChi]                    # forward index, immutable
    cung_than_position: DiaChi

    def cung_at(self, dia_chi: DiaChi) -> Cung: ...
```

In [src/refactored/component/cung.py](../../component/cung.py): change `components: list[Component]` to `components: tuple[Component, ...]` and adjust the field default accordingly.

`src/refactored/chart/builder.py`:

```python
@dataclass
class LaSoBuilder:
    catalog: ComponentCatalog
    role_compiler_factory: Callable[[], PlacementRuleCompiler] = get_default_role_compiler
    component_compiler_factory: Callable[[], PlacementRuleCompiler] = get_default_component_compiler

    def build(self, prior: LaSoPrior) -> LaSo: ...
```

`build()` orchestration:
1. Create `NatalContext.from_prior(prior)`.
2. Construct role + component compilers via factories.
3. Run **one** catalog guard (same module or a small helper next to `LaSoBuilder`): every string id registered on **both** compilers must resolve in `ComponentCatalog` (the JSON-backed map already includes `CungRole` and sao / tu hoa / etc.). Aggregate all offending ids into a single error if any are missing. **Explicit non-goal:** do *not* require that every row in JSON catalogs has a placement rule.
4. `compile(natal)` each → resolve via `PlacementEngine` → two maps.
5. Determine `cung_than_position` from `role_positions[Role.CUNG_THAN]`.
6. For each of the 12 DiaChi positions, build a `Cung`:
   - `dia_chi`: the `DiaChiEntity` from catalog.
   - `thien_can`: derived via `cung_thien_can_for(natal.thien_can, position)` then resolved to the catalog `ThienCanEntity`.
   - `role`: from `role_positions` reversed (which `Role` lives at this `DiaChi`?).
   - `components`: tuple of catalog-resolved `Component`s for every component id whose `component_positions[id] == this dia_chi`. Order by component id stable (alphabetical or catalog-order — pick one and document).
   - `is_cung_than`: `True` iff this dia_chi == `cung_than_position`.
7. Return `LaSo`.

## Specific changes

- New `src/refactored/chart/__init__.py`, `chart/laso.py`, `chart/builder.py`.
- Implement the **single** catalog guard in `chart/builder.py` (or `chart/catalog_guard.py` imported by it): union of registered ids from both compilers ⊆ catalog keys; one aggregated error listing every missing id.
- Adjust [Cung](../../component/cung.py) to use `tuple[Component, ...]` and remove the mutable default.
- Move `cung_thien_can_for` import path if needed (currently in primitives.py per [rules.py](../../placement/rules.py); keep it where it is).
- Tuần/Triệt: today these resolve to two ids each (`tuan_1`, `tuan_2`, `triet_1`, `triet_2`). The `LaSoBuilder` should treat them as components attached to those two cungs (the catalog already loads `TuanTriet` entities); no special flag on `Cung` is needed unless workstream 06 wants one — defer that decision to 06.

## Out of scope

- Sao status (workstream 06).
- Any mutation API. `LaSo` is read-only.
- Layers (workstream 07).

## Acceptance criteria

- New unit test builds a `LaSo` for a fixed `LaSoPrior` and asserts:
  - All 12 `Cung`s are present, indexed by `DiaChi`.
  - `cung_at(dia_chi).role` matches a known expected role for that birth.
  - `cung_at(menh_position).is_cung_than` matches the expected flag.
  - `component_positions["tu_vi"]` matches a known expected position for that birth (cross-check against [src/tuvi/](../../../tuvi/) legacy chart).
  - Each `Cung.components` is a `tuple`.
- A targeted test: seed a compiler factory with an extra rule whose id is absent from the catalog; `LaSoBuilder.build` raises with that id named (aggregated form if multiple). Default `build` succeeds for shipped rules + catalog.
- Existing tests still pass.
