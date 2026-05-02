import pytest

from src.refactored.component.elementary import DiaChi
from src.refactored.placement.compiler import (
    PlacementRuleCompiler,
    SpecializedAbsoluteSpec,
    SpecializedPlacementRules,
    SpecializedRelativeSpec,
)
from src.refactored.placement.engine import PlacementEngine
from src.refactored.placement.registry import RelativePositionSpec


def test_specialized_rules_rejects_dangling_reference():
    with pytest.raises(KeyError, match=r"child -> missing"):
        SpecializedPlacementRules(
            specs={
                "child": SpecializedRelativeSpec(
                    reference_id="missing",
                    transform=lambda p: p,
                ),
            }
        )


def test_restrict_to_self_contained_matches_full_resolution():
    rules = SpecializedPlacementRules(
        specs={
            "root": SpecializedAbsoluteSpec(position_fn=lambda: DiaChi.DAN),
            "mid": SpecializedRelativeSpec(
                reference_id="root",
                transform=lambda p: p + 1,
            ),
            "leaf": SpecializedRelativeSpec(
                reference_id="mid",
                transform=lambda p: p + 1,
            ),
        }
    )
    subset = {"root", "mid", "leaf"}
    restricted = rules.restrict_to(subset, seed={})
    full = PlacementEngine(rules).resolve_all()
    part = PlacementEngine(restricted).resolve_all()
    for cid in subset:
        assert part[cid] == full[cid]


def test_restrict_to_rewrites_external_reference_from_seed():
    rules = SpecializedPlacementRules(
        specs={
            "anchor": SpecializedAbsoluteSpec(position_fn=lambda: DiaChi.DAN),
            "satellite": SpecializedRelativeSpec(
                reference_id="anchor",
                transform=lambda p: p + 3,
            ),
        }
    )
    restricted = rules.restrict_to(
        {"satellite"},
        seed={"anchor": DiaChi.TY},
    )
    assert PlacementEngine(restricted).resolve_all() == {
        "satellite": DiaChi.TY + 3,
    }


def test_restrict_to_missing_seed_raises_precise_key_error():
    rules = SpecializedPlacementRules(
        specs={
            "parent": SpecializedAbsoluteSpec(position_fn=lambda: DiaChi.DAN),
            "child": SpecializedRelativeSpec(
                reference_id="parent",
                transform=lambda p: p,
            ),
        }
    )
    with pytest.raises(
        KeyError,
        match=r"Restricted spec 'child' requires reference 'parent' which is not in `ids` and not in `seed`",
    ):
        rules.restrict_to({"child"}, seed={})


def test_compiler_validation_moves_to_rules_constructor():
    compiler = PlacementRuleCompiler()
    compiler.register_component_lazy(
        "child",
        RelativePositionSpec("missing_parent", lambda p: p),
    )
    from src.refactored.context.natal import NatalContext
    import datetime as dt

    from src.refactored.context.prior import Gender, LaSoPrior

    ctx = NatalContext.from_prior(
        LaSoPrior.from_solar_day(dt.datetime(1996, 12, 19, 6, 30), Gender.MALE)
    )
    with pytest.raises(KeyError):
        compiler.compile(ctx)
