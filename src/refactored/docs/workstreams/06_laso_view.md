# Workstream 06 — `LaSoView` query facade

**Status**: pending
**Depends on**: 05, 07
**Unblocks**: nothing (terminal)

## Goal

Provide `LaSoView`, a read-only facade that composes one `LaSo` with zero or more dynamic layers and exposes the domain question API listed in [domain_context.md](../domain_context.md). Layers are stored and keyed by **`LayerRef`** (`dict[LayerRef, Layer]`). Inject a `SaoStatusResolver` so sao status is resolved at view time.

## Background

Static `LaSo` is immutable. Dynamic slices are **`Layer`** values keyed by **`LayerRef`** in the view (`dict[LayerRef, Layer]`). `LayerCompiler.compile(...)` may still return **`tuple[Layer, ...]`** (natural for one atomic compile pass); **`LaSoView`** folds that into a dict keyed by `layer.ref()` and rejects duplicate refs. The view is where chart facts are queried; it must surface static + dynamic information with explicit provenance (`LayerRef | None` for natal).

## Public API to introduce

`src/refactored/chart/view.py`:

```python
class SaoStatusResolver(Protocol):
    def status_for(self, sao_id: ComponentId, dia_chi: DiaChi) -> SaoStatus: ...

DEFAULT_SAO_STATUS_RESOLVER: SaoStatusResolver  # adapter over MAP_SAO_STATUS


@dataclass(frozen=True)
class RelatedPositions:
    tam_hop: tuple[DiaChi, DiaChi]   # the two other tam-hop cungs
    xung_chieu: DiaChi
    nhi_hop: DiaChi
    luc_hai: DiaChi


@dataclass(frozen=True)
class PlacedComponent:
    """A catalog `Component` plus where it came from: natal (`source is None`)
    or a dynamic slice (`source` is that slice's `LayerRef`)."""
    component: Component
    source: LayerRef | None


@dataclass(frozen=True)
class LaSoView:
    static: LaSo
    layers: Mapping[LayerRef, Layer]  # immutable mapping (e.g. frozendict or types.MappingProxyType)
    status_resolver: SaoStatusResolver = DEFAULT_SAO_STATUS_RESOLVER

    @classmethod
    def build(
        cls,
        static: LaSo,
        *,
        layers: Mapping[LayerRef, Layer] | Iterable[Layer] = (),
        status_resolver: SaoStatusResolver = DEFAULT_SAO_STATUS_RESOLVER,
    ) -> "LaSoView":
        """If `layers` is an iterable of `Layer`, fold into `{layer.ref(): layer}` and
        raise if any duplicate `ref()`. If already a `Mapping`, validate duplicate-free keys."""
        ...

    def layer(self, ref: LayerRef) -> Layer | None: ...
    def layers_of_kind(self, kind: LayerKind) -> tuple[Layer, ...]: ...

    # Cung queries (natal unless documented otherwise)
    def cung_at(self, dia_chi: DiaChi) -> Cung: ...
    def role_of(self, dia_chi: DiaChi) -> Role: ...

    # Component queries — `scope is None` means natal only; set `scope` to a `LayerRef` to narrow to that slice
    def positions_of(
        self, component_id: ComponentId, *, scope: LayerRef | None = None
    ) -> list[DiaChi]: ...
    def components_in(
        self,
        dia_chi: DiaChi,
        *,
        include_dynamic: bool = True,
        scope: LayerRef | None = None,
    ) -> list[PlacedComponent]: ...
    def status_of(self, sao_id: ComponentId, *, at: DiaChi | None = None) -> SaoStatus: ...

    # Relational queries
    def related(self, dia_chi: DiaChi) -> RelatedPositions: ...

    # Dynamic-layer helpers
    def layer_components_in(
        self,
        dia_chi: DiaChi,
        kind: LayerKind | None = None,
    ) -> list[tuple[LayerRef, Component]]: ...
    def rotated_roles_at(
        self, dia_chi: DiaChi, kind: LayerKind | None = None
    ) -> list[tuple[LayerRef, Role]]: ...
```

**API notes**

- **`layers` canonical type:** `Mapping[LayerRef, Layer]` (read-only). Construction accepts either that mapping or an **`Iterable[Layer]`** (e.g. the `tuple` returned from `LayerCompiler.compile`) and normalizes to the dict.
- **`PlacedComponent`:** replaces bare `list[Component]` for merged static+dynamic lists so the same `component_id` from different slices stays distinguishable.
- **`positions_of` / `components_in`:** `scope: LayerRef | None = None` — `None` = natal only; non-`None` = that slice only. For “all sources”, omit `scope` and use overloads or a dedicated method (e.g. `components_in_all_sources(dia_chi)`) — pick one and document; the sketch above uses `include_dynamic` + optional `scope` together: when `include_dynamic` is true and `scope` is None, merge natal + every value in `layers.values()` in stable order (e.g. insertion order of the mapping, or sort by `(kind, anchor)` — document the chosen order).
- **`rotated_roles_at`:** only layers with non-empty `roles` contribute; `TUHOA_PHAI` layers yield nothing here. Return list of `(LayerRef, Role)` for disambiguation when multiple period layers exist.

## Specific changes

- New file `src/refactored/chart/view.py`.
- Implement `RelatedPositions` using [transforms.py](../../placement/transforms.py): `get_xung_chieu`, `get_nhi_hop`, `get_luc_hai`, `get_tam_hop` (twice for tam hợp).
- `DEFAULT_SAO_STATUS_RESOLVER` adapts [map_sao_status.py](../../builder/map_sao_status.py); document the key used (`MAP_SAO_STATUS` is keyed by sao display name — confirm at boundary).
- Layer composition rules: `components_in(dia_chi, include_dynamic=True)` returns static sao entities first,
then for each layer it appends every `(component_id → DiaChi)` pair from `layer.saos` where DiaChi ==
dia_chi, resolved via catalog.

## Out of scope

- Concrete `LayerCompiler` implementations (stubbed in workstream 07).
- Lazy compilation from a period spec — `LaSoView` accepts pre-built layers only (as `Mapping[LayerRef, Layer]` or `Iterable[Layer]` folded to that).
- Rendering / markdown (legacy `Cung.__repr__` not ported).

## Acceptance criteria

- Unit tests: `cung_at`, `role_of`, `related`, `build(static, layers=...)` with empty mapping and with a small `dict[LayerRef, Layer]`.
- Duplicate `LayerRef` on `build(..., layers=[...])` raises.
- `components_in` returns `PlacedComponent` rows with correct `source` / `None`.
- `layers_of_kind(LayerKind.TUHOA_PHAI)` returns 12 layers when the mapping holds 12 Tu Hoa Phái refs.
- `status_of(sao_id)` returns a value consistent with `MAP_SAO_STATUS` for a known
sao+cung pair.
- `LaSoView.build(static=laso)` succeeds with default empty layers.
- Existing tests still pass.
