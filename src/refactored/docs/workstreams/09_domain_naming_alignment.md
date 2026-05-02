# Workstream 09 — Domain naming alignment (`Component` / `Sao` / `CungRole`)

**Status**: pending  
**Depends on**: none  
**Unblocks**: 01, 02, 04, 05, 06, 07

## Goal

Align naming using **typing-only conventions** (no extra inheritance layer for `Component` / `Sao`):

- **`Component`** — a strict **`TypeAlias`** for everything the unified catalog can return and chart code treats as a catalog “component.”
- **`Sao`** — a **`TypeAlias`** for the non-role union placed on a `Cung` (chính/phụ tinh + tu hóa + tràng sinh + tuần/triệt).
- Concrete entity classes keep subclassing **`ComponentBase`** as today; **`Component` is not a superclass.**

Keep `ComponentId` and `component_id` naming in placement APIs unchanged.

This workstream is intended to run **first** so subsequent workstreams can implement behavior on top of stable vocabulary.

## Type aliases (canonical)

Declared in [component/__init__.py](../../component/__init__.py) (or a dedicated `component/types.py` re-exported from `__init__.py`):

```python
from typing import TypeAlias

# Concrete classes still subclass ComponentBase (pydantic models).
Sao: TypeAlias = ChinhPhuTinh | TuHoa | VongTrangSinh | TuanTriet

Component: TypeAlias = (
    DiaChiEntity
    | ThienCanEntity
    | Cuc
    | CungRole
    | Sao
)
```

Equivalently, expanding `Sao`:

`Component = DiaChiEntity | ThienCanEntity | Cuc | CungRole | ChinhPhuTinh | TuHoa | VongTrangSinh | TuanTriet`.

**Strict union:** do not model `Component` as “any subclass of `ComponentBase`” for typing — only these members. Adding a new catalog model later requires updating the alias (and tests).

## Conventions to enforce

1. **Class names (implementation)**
   - Rename the current star class **`Sao` → `ChinhPhuTinh`** in [sao.py](../../component/sao.py).
   - `TuHoa`, `VongTrangSinh`, `TuanTriet` remain separate classes under **`ComponentBase`**.
   - **`Sao`** is only the **union alias** above, not a runtime class (avoid `isinstance(x, Sao)` — use `isinstance(x, ChinhPhuTinh)` or a small helper / `TypeGuard` if needed).

2. **Field names**
   - `Cung.components` → `Cung.saos` with type `tuple[Sao, ...]`.
   - `LaSo.component_positions` → `LaSo.sao_positions`.
   - `Layer.components` → `Layer.saos`.

3. **Placement id naming**
   - Keep `ComponentId = str` in `placement/registry.py`.
   - Keep `component_id` parameter names across rules/primitives/compiler/engine.

4. **View naming**
   - Keep **`PlacedComponent`** (do not rename).
   - `PlacedComponent.component: Component` — valid because **`Component`** is the catalog union.

## Specific changes

- [component/__init__.py](../../component/__init__.py): export **`Component`** and **`Sao`** as the aliases above; export concrete classes (`ChinhPhuTinh`, …). Replace the old narrow `Component = (...)` union with this scheme.
- [component/sao.py](../../component/sao.py): rename class **`Sao` → `ChinhPhuTinh`**; fix imports (catalog, tests).
- [component/cung.py](../../component/cung.py): `saos: tuple[Sao, ...]`.
- [builder/component_catalog.py](../../builder/component_catalog.py): `get(...) -> Component`; load địa chi / thiên can / cục into the same id map if not already, consistent with the union.
- [chart/](../../chart/), [layer/types.py](../../layer/types.py), [chart/view.py](../../chart/view.py): `sao_positions` / `Layer.saos`; **`PlacedComponent.component: Component`** unchanged in meaning.
- Tests: replace `isinstance(x, Sao)` where it meant the **star class** with **`ChinhPhuTinh`**; use **`Component`** only for annotations / `get()` results.

## Out of scope

- Introducing a runtime class `class Component(ComponentBase)` or `class Sao(ComponentBase)` as a shared superclass.
- Changing placement rule ids (`component_id` strings).
- Enforcing “every JSON catalog row must have a placement rule.”

## Acceptance criteria

- `Component` and `Sao` are **`TypeAlias`** definitions; **`Component`** is exactly  
  `DiaChiEntity | ThienCanEntity | Cuc | CungRole | Sao` with **`Sao = ChinhPhuTinh | TuHoa | VongTrangSinh | TuanTriet`**.
- Star model class is **`ChinhPhuTinh`**, not `Sao`.
- `Cung.saos`, `LaSo.sao_positions`, `Layer.saos` used consistently in plan/code touchpoints.
- `ComponentId` / `component_id` unchanged in placement modules.
- `PlacedComponent` name unchanged in `LaSoView`.
- Docs/workstreams and WS08 tests updated for union-based typing.
