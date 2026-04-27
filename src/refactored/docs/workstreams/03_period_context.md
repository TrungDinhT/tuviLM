# Workstream 03 — Dynamic context placeholder (no code)

**Status**: deferred (placeholder only)
**Depends on**: 01
**Unblocks**: nothing in this iteration

## Why this workstream is empty

Originally this workstream was going to introduce a single `PeriodContext` type that wrapped `NatalContext` plus an override set, with fall-back-to-natal property delegation. We deliberately rejected that design.

The reasons:

- **Dynamic context types should not depend on natal context.** A `PeriodContext` whose properties silently delegate to a wrapped `NatalContext` re-introduces the cascade-corruption class of bug we already prevented in [02_specialized_rules_upgrade.md](02_specialized_rules_upgrade.md): the moment a primitive reaches for a non-overridden field, it transparently reads natal data, which is exactly the implicit coupling we want to avoid.
- **Per-`LayerKind` shapes diverge.** A `TieuHanContext` does not need `cuc` or `prior`. A `TuHoaPhaiContext` only needs `thien_can`, and that value is not even a year's thien can. Forcing them all through one `PeriodContext` shape makes every concrete subtype lie about its surface.
- **Construction belongs to the LayerCompiler.** Building a context for tiểu hạn requires natal context, the static chart, and a target year. That orchestration is the LayerCompiler's job, not the context's. The context value the LayerCompiler hands to the engine should be a self-contained snapshot of "exactly what the projected rules need to read", with no further dependencies.

## Constraints recorded for the future iteration that implements dynamic contexts

When LayerCompilers land, each new dynamic context type must:

1. **Satisfy the marker `PlacementContext`** Protocol from [01_placement_context.md](01_placement_context.md) (a no-op since the Protocol has no required members).
2. **Be self-contained.** Expose final values directly. No delegation to a wrapped natal context; no fallback semantics.
3. **Expose only the fields its primitives consume.** A `TuHoaPhaiContext` is allowed to expose only `thien_can`. A `TieuHanContext` exposes whatever the lưu projection set + role-rotation rules need (to be determined when those rules are catalogued).
4. **Be frozen** (`@dataclass(frozen=True)` or pydantic equivalent).
5. **Be constructed entirely by its LayerCompiler.** External callers do not instantiate dynamic contexts directly; they go through the compiler.

## Acceptance criteria

This workstream produces no code. It exists to record the constraints above so a future agent does not reinvent fallback-to-natal contexts.

If during implementation of any future LayerCompiler workstream you find yourself wanting a shared `PeriodContext` base or a delegation pattern, stop and revisit this document first.
