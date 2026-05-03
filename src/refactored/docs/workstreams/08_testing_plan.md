# Workstream 08 — Testing plan

**Status**: pending
**Depends on**: nothing (can start in parallel from day one)
**Unblocks**: faster sign-off on 05, 06

## Goal

Provide shared test fixtures and a testing strategy that the other workstreams can plug into. The intent is to avoid each workstream inventing its own birth data and expected positions.

## Fixtures to land

`tests/fixtures/laso_priors.py`:

- `FIXTURE_PRIOR_A`: a fully-specified `LaSoPrior` with known year, month, date, hour, gender. Used as the canonical happy-path birth.
- `FIXTURE_PRIOR_FEMALE_AM`: a `Nữ + Âm` case (chooses CCW van direction).
- `FIXTURE_PRIOR_MALE_DUONG`: a `Nam + Dương` case (chooses CW van direction).

For each fixture, the file also exports a hand-validated expected snapshot:

```python
EXPECTED_A = {
    "menh_position": DiaChi.<known>,
    "cuc_number": <known>,
    "tu_vi_position": DiaChi.<known>,
    "thien_phu_position": DiaChi.<known>,
    "loc_ton_position": DiaChi.<known>,
    "cung_than_position": DiaChi.<known>,
    "cung_at_<dia_chi>": {"role": Role.<known>, "thien_can": ThienCan.<known>},
    # ... add more as workstreams need them
}
```

These snapshots can be cross-checked against the legacy `src/tuvi/` builder before checking in.

## Per-workstream test outline

| Workstream | Test file | Key assertions |
|---|---|---|
| 01 | `tests/test_laso_fixtures.py` (+ primitives tests) | `FIXTURE_PRIOR_A` snapshot vs `resolve_natal_placement` / `NatalPlacement`; `NatalContext` / `context.prior`. |
| 02 | new `tests/test_specialized_rules.py` | Structural invariant raises on dangling reference; `restrict_to` round-trips with self-contained ids; `restrict_to` rewrites externals from seed; `restrict_to` raises a precise error on missing seed. |
| 03 | new `tests/test_period_context.py` | Field overrides reflect; non-overridden fields fall back to natal; satisfies `PlacementContext` Protocol. |
| 04 | `tests/test_placement_builder.py` (partition / default compiler tests) | `placement.bundle.get_default_placement_rule_compiler` independent instances + nonempty compile; `resolve_natal_placement` yields `NatalPlacement` with typed `role_positions` / `sao_positions`. |
| 05 | new `tests/test_static_chart.py` | `LaSoBuilder.build(FIXTURE_PRIOR_A)` returns a `LaSo` whose forward/reverse indices match `EXPECTED_A`. `Cung.saos` is a tuple and `sao_positions` resolves known ids. Catalog guard: `build` fails with named missing ids when a compiler is seeded with a rule id absent from the catalog. |
| 09 | new `tests/test_domain_naming_alignment.py` | `Component` / `Sao` are `TypeAlias` unions (`Component` includes `DiaChiEntity`, `ThienCanEntity`, `Cuc`, `CungRole`, `Sao`; `Sao` is `ChinhPhuTinh | TuHoa | VongTrangSinh | TuanTriet`); star class is `ChinhPhuTinh`; `ComponentId` / `component_id` unchanged in placement APIs. |
| 06 | new `tests/test_laso_view.py` | All query methods round-trip; `related(menh_position)` matches expected tam hợp / xung chiếu / nhị hợp / lục hại; status resolver returns correct values; empty `layers` tuple works. |
| 07 | new `tests/test_layer_types.py` | Layer constructs with empty maps; `LaSoView(layers=(layer,))` constructs; stub compilers raise `NotImplementedError`. |

## Cross-fixture invariants

Two invariants worth asserting in a single test that runs on every fixture:

1. The set of `DiaChi`s covered by `LaSo.cungs` equals `set(DiaChi)`.
2. `LaSo.role_positions[Role.MENH] == LaSo.natal.menh_position`.

## Out of scope

- Performance benchmarks.
- Property-based testing (Hypothesis) — useful eventually, not in this iteration.

## Acceptance criteria

- Fixtures live in `tests/fixtures/` and are importable by the per-workstream test files above.
- The `EXPECTED_*` dicts have been cross-checked against the legacy `src/tuvi/` chart builder before merging.
