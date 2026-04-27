# Workstream 07 — `Layer` skeleton (types + compiler protocol stubs)

**Status**: pending
**Depends on**: 02
**Unblocks**: 06

## Goal

Land the final-shape types for the dynamic layer system: `LayerKind`, `LayerRef`, `LayerAnchor` (a tagged anchor union), `Layer`, the projection sets `LIST_SAO_LUU` / `TU_HOA_IDS`, and a `LayerCompiler` Protocol with stubbed implementations. After this workstream, `LaSoView` (workstream 06) holds layers as **`dict[LayerRef, Layer]`** (see WS06 for folding from compiler output). No concrete layer compiler runs in this iteration.

## Background

A `Layer` carries deltas only — never a duplicate of static positions. Each layer has a single anchor that identifies what produced it. Atomicity rule: building a `LayerKind` produces however many layers that kind requires, in one compile pass. **`LayerCompiler.compile`** returns **`tuple[Layer, ...]`** (ordered output from one compile call). **`LaSoView`** (WS06) stores **`dict[LayerRef, Layer]`** built from those layers — O(1) by ref, duplicate `ref()` rejected at view construction.

Per discussion:

| `LayerKind`         | Produced by             | Layers per compile | Anchor type    | Extra inputs                       | `roles` map populated? |
| ------------------- | ----------------------- | :----------------: | -------------- | ---------------------------------- | :--------------------: |
| `TIEU_HAN`          | `TieuHanCompiler`       |         1          | `PeriodAnchor` | year                               |          yes           |
| `DAI_HAN`           | `DaiHanCompiler`        |         1          | `PeriodAnchor` | year                               |          yes           |
| `LUU_NIEN_DAI_HAN`  | `LuuNienDaiHanCompiler` |         1          | `PeriodAnchor` | the built `DAI_HAN` `Layer` + year |          yes           |
| `TUHOA_PHAI`        | `TuHoaPhaiCompiler`     |  12 (one per natal Cung)  | `CungAnchor`   | none                               |           no           |

Lưu Niên Đại Hạn is domain-coupled to Đại Hạn (its context is derived from the Đại Hạn Địa Chi). The compiler split keeps this as an **explicit declared dependency**: `LuuNienDaiHanCompiler.compile(natal, dai_han_layer, year)` takes the already-built `DAI_HAN` `Layer` as input and reads `dai_han.anchor.dia_chi` (for a `PeriodAnchor`) to derive its own context. This preserves the 1:1 "compiler ↔ kind" shape while making the data dependency visible in the type signature, rather than baking it into class identity.

For `TUHOA_PHAI`, `roles` is an empty dict — the Tu Hoa Phái pattern only places Tu Hoa; it does not rotate cung roles.

## Public API to introduce

`src/refactored/layer/types.py`:

```python
class LayerKind(StrEnum):
    TIEU_HAN = "tieu_han"
    DAI_HAN = "dai_han"
    LUU_NIEN_DAI_HAN = "luu_nien_dai_han"
    TUHOA_PHAI = "tuhoa_phai"


@dataclass(frozen=True)
class LayerRef:
    """Lightweight identity for a layer: (kind, anchor). Hashable; used as dict
    keys and in query provenance without carrying placement payloads."""
    kind: LayerKind
    anchor: LayerAnchor


@dataclass(frozen=True)
class PeriodAnchor:
    """Anchor for vận hạn layers (TIEU_HAN / DAI_HAN / LUU_NIEN_DAI_HAN).
    Field semantics are interpreted per LayerKind."""
    thien_can: ThienCan
    dia_chi: DiaChi


@dataclass(frozen=True)
class CungAnchor:
    """Anchor for TuHoaPhái: identifies the natal Cung whose ThienCan
    drove this layer's Tu Hoa placement."""
    cung_dia_chi: DiaChi
    cung_thien_can: ThienCan


LayerAnchor = PeriodAnchor | CungAnchor


@dataclass(frozen=True)
class Layer:
    """Payload for one dynamic slice. `Layer` does not embed a stored `LayerRef`;
    identity is computed via `ref()` so the struct can evolve without coupling
    to the ref type."""
    kind: LayerKind
    anchor: LayerAnchor
    components: dict[ComponentId, DiaChi]
    roles: dict[Role, DiaChi]

    def ref(self) -> LayerRef:
        return LayerRef(self.kind, self.anchor)


# Projection sets (subsets of component ids that overlay layers recompute)
LIST_SAO_LUU: frozenset[ComponentId] = frozenset({
    "thai_tue", "bach_ho", "tang_mon", "thien_ma",
    "loc_ton", "kinh_duong", "da_la", "thien_khoc", "thien_hu",
})

TU_HOA_IDS: frozenset[ComponentId] = frozenset({
    "hoa_loc", "hoa_quyen", "hoa_khoa", "hoa_ky",
})
```

Notes on the API shape:

- **No `Source` namespacing inside a `Layer`.** A layer is single-anchor; multi-anchor patterns (TuHoaPhái) produce multiple layers, not one layer with internal sources.
- **Identity** for indexing and provenance is `LayerRef` (`ref()` on `Layer`). Two layers with the same `ref()` must not appear in one composition; **`LaSoView.build`** rejects duplicates when folding an iterable into `dict[LayerRef, Layer]`. WS07 defines the types; WS06 owns the dict and validation.
- **`components`** is a flat `dict[ComponentId, DiaChi]`, same shape as the natal component positions map, so restriction-with-seed (workstream 02) plugs in directly. **Not** the same shape as `Cung.components` on a palace (which is a `tuple` of catalog entities); on `Layer`, `components` is always a position map keyed by id.
- **`roles`** is `dict[Role, DiaChi]` — for each cung-role label, which `DiaChi` that label occupies in this layer's frame. Empty when the kind does not rotate roles (e.g. TuHoaPhái).
- **Construction is atomic per `LayerKind`.** `LayerCompiler.compile()` for `TUHOA_PHAI` must return all 12 layers in one call. Lazy or selective generation is rejected to keep the build/query stages cleanly separated.

`src/refactored/layer/compiler.py`:

```python
class LayerCompiler(Protocol):
    """Compiles all Layers for a given LayerKind from natal positions and
    layer-specific input.

    Concrete implementations narrow `compile` to their actual input shape;
    we deliberately do not enforce a uniform signature on the Protocol because
    the inputs differ per kind (and one kind — LUU_NIEN_DAI_HAN — takes a
    previously-built Layer as a declared dependency).

    Concrete bodies are out of scope for this workstream; stubs raise
    NotImplementedError.
    """
    @property
    def kind(self) -> LayerKind: ...

    def compile(self, natal: LaSo, *args: Any, **kwargs: Any) -> tuple[Layer, ...]: ...

# Stub implementations — one per LayerKind. Each raises NotImplementedError.
# The signatures below are normative for the future implementation iteration.
class TieuHanCompiler:
    kind = LayerKind.TIEU_HAN
    def compile(self, natal: LaSo, year: int) -> tuple[Layer]: ...

class DaiHanCompiler:
    kind = LayerKind.DAI_HAN
    def compile(self, natal: LaSo, year: int) -> tuple[Layer]: ...

class LuuNienDaiHanCompiler:
    kind = LayerKind.LUU_NIEN_DAI_HAN
    # Declares its dependency on a built DAI_HAN layer in the type signature.
    # Reads `dai_han.anchor.dia_chi` to derive its own context.
    def compile(self, natal: LaSo, dai_han: Layer, year: int) -> tuple[Layer]: ...

class TuHoaPhaiCompiler:
    kind = LayerKind.TUHOA_PHAI
    def compile(self, natal: LaSo) -> tuple[Layer, ...]:  # exactly 12
        ...
```

## Specific changes

- New `src/refactored/layer/__init__.py`, `layer/types.py`, `layer/compiler.py`.
- `LIST_SAO_LUU` lives here, *not* in [rules.py](../../placement/rules.py). Coordinate with workstream 04 to ensure the placeholder list is removed from `rules.py`.
- Each stub compiler's `compile()` body raises `NotImplementedError` and includes a docstring describing in free form what it will eventually do (which projection set, what context shape, how many layers it returns).
- Document in the module docstring: `Layer.components` / `Layer.roles` are flat per-anchor; multi-anchor patterns produce multiple `Layer` objects; `Layer.ref()` is the stable key for `dict[LayerRef, Layer]` in the view (WS06).

## Implementation hint for follow-up iterations (not this one)

A concrete `TieuHanCompiler.compile` will look roughly like:

```python
def compile(self, natal: LaSo, year: int) -> tuple[Layer]:
    # 1. Derive (thien_can, dia_chi) for tiểu hạn from natal + year.
    # 2. Construct a self-contained TieuHanContext per WS03's constraints.
    ctx = TieuHanContext(...)

    # 3. Compile component rules under TieuHanContext, then restrict to projection.
    component_compiler = get_default_component_compiler()
    full = component_compiler.compile(ctx)
    restricted = full.restrict_to(
        ids=LIST_SAO_LUU | TU_HOA_IDS,
        seed=natal.component_positions,
    )
    resolved_components = PlacementEngine(restricted).resolve_all()

    # 4. Same dance for role rules → resolved_roles.
    # 5. Wrap in one Layer.
    return (Layer(
        kind=LayerKind.TIEU_HAN,
        anchor=PeriodAnchor(...),
        components=resolved_components,
        roles=resolved_roles,
    ),)
```

`LuuNienDaiHanCompiler.compile(natal, dai_han, year)` will read `dai_han.anchor.dia_chi`, derive the lưu niên context from natal + that anchor + year, then run the same projection-and-restrict dance as tiểu hạn. Note: this compiler does not produce the đại hạn layer — callers must run `DaiHanCompiler` first and feed its output here. A small façade (out of scope for this workstream) can wire them together for ergonomic call sites.

`TuHoaPhaiCompiler.compile(natal)` will iterate the 12 natal Cungs and return a tuple of 12 layers, each anchored on `CungAnchor(cung_dia_chi, cung_thien_can)` and projected to `TU_HOA_IDS` only. `roles` is `{}`.

These snippets are illustrative only; do not implement them in this workstream.

## Out of scope

- Concrete bodies for any `*Compiler` stub.
- Wiring `LaSoView` to lazily compile layers — `LaSoView` accepts pre-built **`Mapping[LayerRef, Layer]`** or **`Iterable[Layer]`** folded to that dict (WS06); compilers still return **`tuple[Layer, ...]`** from `compile`.
- The dynamic context types themselves (`TieuHanContext` etc.) — those land per LayerCompiler iteration; see [03_period_context.md](03_period_context.md) for constraints they must satisfy.

## Acceptance criteria

- `Layer`, `LayerRef`, `LayerKind`, `PeriodAnchor`, `CungAnchor`, `LayerAnchor`, `LIST_SAO_LUU`, `TU_HOA_IDS` exist and are importable from `src.refactored.layer.types`.
- `LayerCompiler` Protocol exists; the four stub classes exist and raise `NotImplementedError` from `compile()`.
- A unit test constructs an empty `Layer(kind=LayerKind.TIEU_HAN, anchor=PeriodAnchor(...), components={}, roles={})` successfully and asserts `layer.ref() == LayerRef(LayerKind.TIEU_HAN, anchor)`.
- A unit test builds a `dict[LayerRef, Layer]` with 12 entries (distinct `LayerRef`s, each `TUHOA_PHAI` + unique `CungAnchor`) — e.g. fold a 12-tuple of `Layer` the same way `LaSoView.build` would (no compiler invoked).
- A unit test asserts `LuuNienDaiHanCompiler.compile`'s signature accepts a `Layer` parameter typed as the đại hạn dependency (signature inspection is enough; the body still raises `NotImplementedError`).
- Existing tests still pass.
