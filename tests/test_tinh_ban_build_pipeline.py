from dataclasses import dataclass

from src.refactored.assembly.natal import build_natal_tinh_ban
from src.refactored.assembly.tu_hoa_phai import build_tu_hoa_phai_layer
from src.refactored.component.cung_role import Role
from src.refactored.component.elementary import DiaChi
from src.refactored.context.natal import NatalContext
from src.refactored.context.prior import Gender, LaSoPrior
from src.refactored.context.tu_hoa_phai import TuHoaPhaiContext
from src.refactored.la_so import LaSo
from src.refactored.placement.layer import NatalLayerId, PlacementLayer, TieuHanLayerId


def _prior() -> LaSoPrior:
    return LaSoPrior(
        hour=DiaChi.MEO,
        date=10,
        month=11,
        year=1996,
        gender=Gender.MALE,
    )


def test_build_natal_tinh_ban_creates_structural_cung_ids_and_natal_layer():
    ctx = NatalContext.from_prior(_prior())

    tinh_ban = build_natal_tinh_ban(ctx)

    menh_cung = tinh_ban.cung_at(ctx.menh_position)
    assert menh_cung.natal_role == Role.MENH
    assert tinh_ban.position_of("tu_vi") is not None
    assert tinh_ban.position_of("menh") == ctx.menh_position
    assert tinh_ban.position_of("cung_than") == tinh_ban.than_position
    assert tinh_ban.menh_position == ctx.menh_position
    assert tinh_ban.natal_role_positions[Role.MENH] == ctx.menh_position
    assert "menh" not in tinh_ban.natal_layer.by_component
    assert "cung_than" not in tinh_ban.natal_layer.by_component
    assert any(cung_id.is_cung_than for cung_id in tinh_ban.cung_ids.values())


def test_build_natal_tinh_ban_does_not_eagerly_build_tu_hoa_phai_layers():
    ctx = NatalContext.from_prior(_prior())

    tinh_ban = build_natal_tinh_ban(ctx)

    assert tinh_ban.overlay_layers == {}


def test_build_tu_hoa_phai_layer_uses_scope_and_natal_seed():
    ctx = NatalContext.from_prior(_prior())
    tinh_ban = build_natal_tinh_ban(ctx)
    cung_id = tinh_ban.cung_ids[DiaChi.TY]

    layer = build_tu_hoa_phai_layer(
        context=TuHoaPhaiContext(
            source_dia_chi=cung_id.dia_chi,
            thien_can=cung_id.thien_can,
        ),
        natal_layer=tinh_ban.natal_layer,
    )

    assert set(layer.by_component) == {"hoa_loc", "hoa_quyen", "hoa_khoa", "hoa_ky"}


def test_laso_from_prior_wraps_tinh_ban_and_catalog():
    la_so = LaSo.from_prior(_prior())

    assert la_so.natal_context.layer_id == NatalLayerId()
    assert la_so.component("tu_vi").name == "Tử Vi"
    assert la_so.position_of("tu_vi") is not None


@dataclass(frozen=True)
class _FakePeriodContext:
    layer_id: TieuHanLayerId
    focus_position: DiaChi


def test_tinh_ban_period_layer_cache_is_lru_by_layer_kind():
    ctx = NatalContext.from_prior(_prior())
    tinh_ban = build_natal_tinh_ban(ctx)

    # Force the cache to only keep 2 layers per kind,
    # so we can test eviction logic without building too many layers
    tinh_ban._period_layer_cache.max_layers_per_kind = 2

    build_count = 0

    def _build_layer(period_context: _FakePeriodContext) -> PlacementLayer:
        nonlocal build_count
        build_count += 1
        return PlacementLayer.from_component_positions(
            id=period_context.layer_id,
            positions={"thai_tue": period_context.focus_position},
            focus_position=period_context.focus_position,
        )

    first = _FakePeriodContext(TieuHanLayerId(2026), DiaChi.TY)
    second = _FakePeriodContext(TieuHanLayerId(2027), DiaChi.SUU)
    third = _FakePeriodContext(TieuHanLayerId(2028), DiaChi.DAN)

    tinh_ban.period_layer(first, _build_layer)
    tinh_ban.period_layer(second, _build_layer)
    tinh_ban.period_layer(first, _build_layer)
    tinh_ban.period_layer(third, _build_layer)

    assert build_count == 3
    assert first.layer_id in tinh_ban.overlay_layers
    assert second.layer_id not in tinh_ban.overlay_layers
    assert third.layer_id in tinh_ban.overlay_layers
