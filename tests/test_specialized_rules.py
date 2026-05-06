import pytest

from src.refactored.component.elementary import DiaChi
from src.refactored.placement.compiler import (
    PlacementRuleCompiler,
    SpecializedPlacementRules,
    SpecializedRelativeSpec,
)
from src.refactored.placement.engine import PlacementEngine
from src.refactored.placement.registry import AbsolutePositionSpec, RelativePositionSpec


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


def test_scoped_compile_includes_unseeded_dependency_closure():
    compiler = PlacementRuleCompiler()
    compiler.register_component_lazy(
        "leaf",
        RelativePositionSpec("mid", lambda p: p + 1),
    )
    compiler.register_component_lazy(
        "mid",
        RelativePositionSpec("root", lambda p: p + 1),
    )
    compiler.register_component_lazy(
        "root",
        AbsolutePositionSpec(lambda _ctx: DiaChi.DAN),
    )

    rules = compiler.compile(object(), scope={"leaf"}, seed={})
    resolved = PlacementEngine(rules).resolve_all()

    assert set(resolved) == {"root", "mid", "leaf"}
    assert resolved["leaf"] == DiaChi.THIN


def test_scoped_compile_rewrites_external_reference_from_seed():
    compiler = PlacementRuleCompiler()
    compiler.register_component_lazy(
        "satellite",
        RelativePositionSpec("anchor", lambda p: p + 3),
    )

    rules = compiler.compile(
        object(),
        scope={"satellite"},
        seed={"anchor": DiaChi.TY},
    )

    assert PlacementEngine(rules).resolve_all() == {
        "satellite": DiaChi.MEO,
    }


def test_scoped_compile_does_not_specialize_unneeded_rules_for_partial_context():
    class PartialContext:
        pass

    compiler = PlacementRuleCompiler()
    compiler.register_component_lazy(
        "wanted",
        AbsolutePositionSpec(lambda _ctx: DiaChi.DAN),
    )
    compiler.register_component_lazy(
        "unwanted",
        AbsolutePositionSpec(lambda ctx: ctx.missing_attribute),
    )

    rules = compiler.compile(PartialContext(), scope={"wanted"}, seed={})

    assert PlacementEngine(rules).resolve_all() == {"wanted": DiaChi.DAN}


def test_scoped_compile_missing_dependency_raises_precise_key_error():
    compiler = PlacementRuleCompiler()
    compiler.register_component_lazy(
        "child",
        RelativePositionSpec("missing_parent", lambda p: p),
    )

    with pytest.raises(
        KeyError,
        match=r"Component id `missing_parent` has no registered position spec",
    ):
        compiler.compile(object(), scope={"child"}, seed={})
