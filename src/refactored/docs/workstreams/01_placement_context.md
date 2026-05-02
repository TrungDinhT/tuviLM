# Workstream 01 — `PlacementContext` marker + primitives refactor

**Status**: pending
**Depends on**: nothing (foundation)
**Unblocks**: 03, 04, 05

## Goal

Introduce a `PlacementContext` Protocol as a structural marker (no required members) so primitives have a meaningful parameter type. Refactor [primitives.py](../../placement/primitives.py) so they read context fields uniformly (e.g. `ctx.thien_can`) rather than dotting into `context.prior.get_*()`. Rename `LaSoContext` to `NatalContext` (prior types live in `context/prior.py`).

This is the wedge that makes period-context overrides clean for later workstreams.

## Design choice: marker Protocol + duck typing (Option 2)

Different concrete contexts (`NatalContext`, future `PeriodContext`, future `TuHoaPhaiContext`, etc.) provide different subsets of fields. A fat Protocol that demands every field would force contexts to fake the ones they should not have. We deliberately avoid that.

For this iteration:

- `PlacementContext` is a `Protocol` with **no required members** — it serves as a structural marker.
- Each concrete context class advertises its surface by what attributes it actually defines. Nothing is faked.
- Primitives are typed against `PlacementContext` and read whatever fields they need (`ctx.thien_can`, `ctx.cuc`, `ctx.prior.date`, etc.).
- Misrouting a context at runtime (e.g. passing a context that lacks `cuc` to a primitive that reads `cuc`) surfaces as `AttributeError` mid-resolution. The stack trace points at the offending primitive and the missing attribute, which is debuggable but not as tidy as a precise compile-time error.

We accept this trade-off explicitly because LayerCompilers (which are where context misrouting can realistically happen) are out of scope for this iteration. See the upgrade note at the bottom for the path to stronger guarantees.

## Public API to introduce

`src/refactored/context/protocol.py`:

```python
@runtime_checkable
class PlacementContext(Protocol):
    """Structural marker for any context object accepted by placement primitives.

    Concrete contexts expose whichever of the following attributes they need;
    primitives access them ad hoc. There are no required members.
    """
```

`src/refactored/context/natal.py`:

```python
@dataclass(frozen=True)
class NatalContext:  # satisfies PlacementContext
    prior: LaSoPrior
    menh_position: DiaChi

    @classmethod
    def from_prior(cls, prior: LaSoPrior) -> "NatalContext": ...

    @property
    def dia_chi(self) -> DiaChi: return self.prior.year.dia_chi
    @property
    def thien_can(self) -> ThienCan: return self.prior.year.thien_can
    @property
    def cuc(self) -> Cuc: ...                       # same logic as today's LaSoContext
    @property
    def am_duong(self) -> LuongNghi: ...
    @property
    def van_direction(self) -> CircleDirection: ... # same logic as today's LaSoContext
```

## Specific changes

- New module `src/refactored/context/` with `protocol.py`, `prior.py` (`LaSoPrior` / birth helpers), `natal.py`, `__init__.py`.
- Refactor [primitives.py](../../placement/primitives.py) so context reads are flat field access:
  - `context.prior.get_dia_chi()` → `context.dia_chi`.
  - `context.prior.get_thien_can()` → `context.thien_can`.
  - `context.prior.month`, `context.prior.date`, `context.prior.hour` stay as-is (natal-only fields; passed through `prior`).
  - Function signatures change from `LaSoContext` to `PlacementContext`.
- Rename references in [rules.py](../../placement/rules.py) accordingly (function bodies, comments). The naming choice is deliberate: `dia_chi` and `thien_can` on a context describe "the dia_chi / thien_can relevant to this context" — for natal that happens to be the birth year's, for a future TuHoaPhái context it would be a per-Cung value. Dropping the `year_` prefix keeps the property name honest across context kinds.
- `_get_prior_attr_steps` and any helpers that read `context.prior.<attr>` keep their current shape.
- Update [registry.py](../../placement/registry.py): `AbsolutePositionResolver` and `RelativePositionTransform` accept `PlacementContext` instead of `LaSoContext`.
- Update [compiler.py](../../placement/compiler.py) `compile()` signature to accept `PlacementContext`.

## Authoring convention to keep migration cheap (read this!)

To make the future Option 4 upgrade trivial, **do not introduce anonymous lambdas as `position_fn` / `transform` directly in [rules.py](../../placement/rules.py)**. Every callable that ends up stored in a spec should originate from a named factory in [primitives.py](../../placement/primitives.py).

- Today's [rules.py](../../placement/rules.py) is mostly already in this shape; the few inline lambdas live inside primitive constructors (`TamHop`, `MirrorAcross`, `TuHoaPosition`, `Circle._member_offset_transform`). Keep them where they are; do not move them out into `rules.py` ad hoc.
- New rules that need a new computation should add a new factory in [primitives.py](../../placement/primitives.py), not inline a lambda in [rules.py](../../placement/rules.py).

This keeps the set of stamping sites bounded to one file when Option 4 is adopted later.

## Out of scope

- `PeriodContext` (workstream 03).
- Any change to engine.py.
- Capability Protocols and runtime auditing — see "Future upgrade" below.

## Acceptance criteria

- All existing tests in `tests/test_placement_primitives.py` and `tests/test_elementary_components.py` pass with no behavioral change for natal placements.
- `grep` for `context.prior.get_dia_chi`, `context.prior.get_thien_can`, `year_dia_chi`, and `year_thien_can` outside `NatalContext` returns no hits.
- `NatalContext` and `LaSoPrior` live under `src/refactored/context/`; the old `LaSoContext` name is retired in code (use `NatalContext`).
- Type-check passes; primitives are typed against `PlacementContext`.
- No new lambdas appear at `position_fn=` / `transform=` call sites in [rules.py](../../placement/rules.py).

## Future upgrade — Option 4 (capability audit)

When LayerCompiler implementations land and start producing non-natal contexts, upgrade this workstream to **capability Protocols + runtime audit**. The migration is additive and localized; nothing built in this iteration becomes wrong.

What gets added then:

1. **Capability Protocols** in `context/protocol.py`, all `@runtime_checkable`:
   `HasDiaChi`, `HasThienCan`, `HasMenhPosition`, `HasCuc`, `HasVanDirection`, `HasNatalPrior`. Existing context classes structurally satisfy them with zero edits.
2. **A `_requires(*caps)` decorator/stamper** in `placement/capabilities.py` (~5 lines) that sets `__capabilities__` on a callable.
3. **Stamping** at every factory and inline-rule lambda site:
   - Every factory in [primitives.py](../../placement/primitives.py) wraps its returned callable with `_requires(...)`.
   - Each primitive class that constructs an inline lambda (`TamHop`, `MirrorAcross`, `TuHoaPosition`, `Circle._member_offset_transform`) wraps that lambda the same way.
   - The full list of sites is bounded; expect ≈10–15 stamps in primitives.py and ≈4 in rules.py-adjacent classes.
4. **`audit_capabilities(rules, context)`** invoked at the end of `PlacementRuleCompiler.compile()`. Walks every spec, reads `__capabilities__` off the callable, and `isinstance`-checks the context against each. Raises an aggregated error naming the offending rule and the missing capability.
5. **Lint guard**: a tiny test or AST check that fails CI if a primitive callable is missing `__capabilities__`, so future contributors don't silently bypass the audit.

What does *not* change in the upgrade:

- Context classes (no edits — they already structurally satisfy the new Protocols).
- [rules.py](../../placement/rules.py) (rules don't carry context types).
- [engine.py](../../placement/engine.py).
- Tests for static placements.

The cost is concentrated in [primitives.py](../../placement/primitives.py), the audit function, and one compiler-level call. That's why following the "no inline lambdas in rules.py" convention now keeps the upgrade cheap.
