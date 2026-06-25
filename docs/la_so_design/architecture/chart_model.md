# Chart Model

This document records the implemented foundation for the refactored chart
model. Domain background lives in `../domain_context.md`.

## Package Ownership

The refactored code separates the core chart model, component definitions, and
placement solving:

- `model/` owns `TinhBan`, `Cung`, layer identities, placement layers, prior
  values, and period focus maps.
- `components/` owns component definitions, JSON data, and
  `ComponentRepository`.
- `placement/` owns the rule language, compiler, scopes, transforms, and rule
  groups.
- `LaSo` is the public aggregate root that holds the chart model and component
  repository, joining them only when needed.

The core remains query-oriented. View models such as `LaSoView` and `CungView`
are built in the `view` package and documented in `view_model.md`.

## LaSo

`LaSo` is the user-facing entry point.

Implemented responsibilities:

- build itself from `LaSoPrior`
- hold `prior`, `natal_context`, `catalog`, and `tinh_ban`
- delegate placement queries to `TinhBan`
- expose component-repository lookup by component id
- expose period focus maps
- build period layers from `PeriodKind` and studied year

`LaSo.period_layer(kind, year)` builds the concrete period context internally,
then delegates caching and storage to `TinhBan`.

## TinhBan

`TinhBan` is the internal chart placement map and query model. It lives in
`model/tinh_ban.py`.

Implemented storage:

- `cung_ids: dict[DiaChi, CungId]`
- `natal_layer: PlacementLayer`
- `period_focus_maps: PeriodFocusMaps`
- `period_layers: PeriodLayerStore`

The natal chart and individual placement layers are immutable values. The
period layer store is mutable so dynamic period layers can be built lazily and
evicted.

Implemented queries:

- `layer(layer_id)`
- `position_of(component_id, layer_id)`
- `components_at(dia_chi, layer_ids)`
- `cung_at(dia_chi, layer_ids)`
- `tieu_han_focus_map()`
- `dai_han_focus_map()`
- `period_layer(layer_id, build_fn)`

Natal roles and `cung_than` are structural data, so they are not exposed as
normal natal-layer components. They are still queryable through
`natal_role_positions`, `menh_position`, `than_position`, and `position_of`.

## CungId and Cung

`CungId`, `Cung`, and related helpers live in `model/cung.py`.

`CungId` is the stable structural identity of one Cung position:

- `dia_chi`
- `thien_can`
- `natal_role`
- `is_cung_than`

`Cung` is an immutable query result assembled from `TinhBan`. It contains the
same structural fields plus lightweight `LayeredComponent` entries:

- `layer_id`
- `component_id`

`Cung` does not contain full catalog components.

## PlacementLayer

`PlacementLayer` and layer identity values live in `model/layer.py`.

`PlacementLayer` stores one layer of component placement.

The canonical index is:

```python
by_component: Mapping[ComponentId, DiaChi]
```

The reverse index is derived for efficient position queries:

```python
by_position: Mapping[DiaChi, frozenset[ComponentId]]
```

Each layer can optionally store `focus_position`, used by period layers.

## Period Layer Cache

Periodic overlays are built lazily and cached inside `TinhBan.period_layers`.
The cache policy is LRU per `LayerKind`, implemented by `PeriodLayerStore` and
`PeriodLayerCache` in `model/period_layer_store.py`.
`TinhBan.period_layer(...)` accepts only `PeriodLayerId` values and verifies
that the built `PlacementLayer.id` matches the requested cache key. `TU_HOA_PHAI`
layers are not wired into this cache yet.

Cache flow:

1. Check `period_layers.layers`.
2. If present, mark the layer id as recently used.
3. If missing, build the layer with the supplied build function.
4. Store it in `period_layers.layers`.
5. Evict the least-recently-used periodic layer of the same kind when the
   per-kind limit is exceeded.

Individual `PlacementLayer` instances remain immutable.
