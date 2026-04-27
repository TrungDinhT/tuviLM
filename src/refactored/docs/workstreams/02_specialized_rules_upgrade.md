# Workstream 02 — Self-validating `SpecializedPlacementRules` + `restrict_to`

**Status**: pending
**Depends on**: nothing (can run in parallel with 01)
**Unblocks**: 07

## Goal

Make `SpecializedPlacementRules` enforce its own structural invariant on construction, and add a `restrict_to(ids, seed)` method that produces a layer-safe subset of the spec map by rewriting external references into constants drawn from a natal seed.

## Background

Today, [compiler.py](../../placement/compiler.py) holds:
- `PlacementRuleCompiler._validate_references_exist(specs)` — a static method called at the end of `compile()`.
- `SpecializedPlacementRules` — a dataclass holding `specs: SpecializedPlacementSpecMap`, with no methods.

Two motivations to change:
1. The structural invariant ("every relative spec's `reference_id` is a key in this spec map") is a property of the artifact, not of the compiler.
2. Layers need a way to compute only a subset of components under a `PeriodContext`, with all external references resolved against natal positions, *without recompiling the full rule set under that period context* (which would silently corrupt cascading positions like `liem_trinh` ← `tu_vi` ← `cuc`).

## Public API to introduce

```python
@dataclass(frozen=True)
class SpecializedPlacementRules:
    specs: SpecializedPlacementSpecMap

    def __post_init__(self) -> None:
        self._validate_structural_integrity()

    def restrict_to(
        self,
        ids: set[ComponentId],
        seed: Mapping[ComponentId, DiaChi],
    ) -> "SpecializedPlacementRules":
        """Return a new artifact containing only `ids`'s specs, with every
        external reference rewritten as a constant `SpecializedAbsoluteSpec`
        from `seed`. Fails fast if any external reference is missing in seed."""
        ...

    # private:
    def _validate_structural_integrity(self) -> None: ...
    def _check_seed_covers_external_refs(
        self, ids: set[ComponentId], seed: Mapping[ComponentId, DiaChi]
    ) -> None: ...
```

## Specific changes

- Move the body of `PlacementRuleCompiler._validate_references_exist` into `SpecializedPlacementRules._validate_structural_integrity` (called from `__post_init__`).
- Drop the static method from the compiler.
- `PlacementRuleCompiler.compile()` now simply returns `SpecializedPlacementRules(specs=specialized_specs)`; validation happens implicitly in the constructor.
- Implement `restrict_to(ids, seed)`:
  1. Run `_check_seed_covers_external_refs` first → raises a descriptive error if a kept rule has an external reference missing in seed.
  2. Build a new spec map:
     - For each id in `ids`: keep the existing spec (compiled under whatever context this `SpecializedPlacementRules` was compiled with).
     - For each external reference id (any reference of a kept relative spec that isn't in `ids`): inject a `SpecializedAbsoluteSpec(lambda pos=seed[id]: pos)`.
  3. Return `SpecializedPlacementRules(specs=new_specs)` (constructor validates structural integrity).
- Add a small helper to enumerate external references of kept specs (only `SpecializedRelativeSpec` carries references).

## Error messages (definition of done)

- Missing seed key error must name the consuming id and the missing reference: `f"Restricted spec {consumer_id!r} requires reference {ref_id!r} which is not in `ids` and not in `seed`."`
- Structural failure error stays similar to today: `f"Component reference has no registered position spec: {component_id} -> {reference_id}"`.

## Out of scope

- Anything related to `PeriodContext` or layer compilation. This workstream is pure compiler/artifact mechanics; it does not assume how the seed is produced.
- Touching `PlacementEngine`.

## Acceptance criteria

- New unit tests in `tests/test_specialized_rules.py` (or extend `test_placement_primitives.py`):
  - Constructing a `SpecializedPlacementRules` with a dangling reference raises (covers structural invariant).
  - `restrict_to` with a self-contained `ids` set returns a working artifact whose `resolve_all` matches the original artifact's resolution restricted to those ids.
  - `restrict_to` with `ids` referencing externals + a seed that covers them returns an artifact whose external refs resolve to the seed's constants.
  - `restrict_to` with `ids` referencing externals + an incomplete seed raises a precise error naming the consumer and the missing reference.
- Existing tests still pass.
