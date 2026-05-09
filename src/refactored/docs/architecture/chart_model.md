# Chart Model

This document records the implemented foundation for the refactored chart
model. Domain background lives in `../domain_context.md`.

## Core Split

The model separates placement from catalog data:

- `TinhBan` owns placement.
- `ComponentCatalog` owns component data.
- `LaSo` is the aggregate root that holds both and joins them only when needed.

The core remains query-oriented. View models such as `LaSoView` and `CungView`
are built in the `view` package and documented in `view_model.md`.

## LaSo

`LaSo` is the user-facing entry point.

Implemented responsibilities:

- build itself from `LaSoPrior`
- hold `prior`, `natal_context`, `catalog`, and `tinh_ban`
- delegate placement queries to `TinhBan`
- expose catalog lookup by component id
- expose period focus maps
- build period layers from `PeriodKind` and studied year

`LaSo.period_layer(kind, year)` builds the concrete period context internally,
then delegates caching and storage to `TinhBan`.

## TinhBan

`TinhBan` is the placement map.

Implemented storage:

- `cung_ids: dict[DiaChi, CungId]`
- `natal_layer: PlacementLayer`
- `period_focus_maps: PeriodFocusMaps`
- `overlay_layers: dict[LayerId, PlacementLayer]`
- private `_period_layer_cache`

The natal chart and individual placement layers are immutable values. The
overlay dictionary is mutable so dynamic layers can be added and evicted.

Implemented queries:

- `layer(layer_id)`
- `position_of(component_id, layer_id)`
- `components_at(dia_chi, layer_ids)`
- `cung_at(dia_chi, layer_ids)`
- `tieu_han_focus_map()`
- `dai_han_focus_map()`
- `period_layer(context, build_fn)`

Natal roles and `cung_than` are structural data, so they are not exposed as
normal natal-layer components. They are still queryable through
`natal_role_positions`, `menh_position`, `than_position`, and `position_of`.

## CungId and Cung

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

Periodic overlays are built lazily and cached inside `TinhBan.overlay_layers`.
The cache policy is LRU per `LayerKind`, implemented by `PeriodLayerCache`.

Cache flow:

1. Check `overlay_layers`.
2. If present, mark the layer id as recently used.
3. If missing, build the layer with the supplied build function.
4. Store it in `overlay_layers`.
5. Evict the least-recently-used periodic layer of the same kind when the
   per-kind limit is exceeded.

Individual `PlacementLayer` instances remain immutable.
