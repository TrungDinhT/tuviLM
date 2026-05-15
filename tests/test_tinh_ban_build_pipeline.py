from dataclasses import dataclass

from src.refactored.assembly.natal import build_natal_tinh_ban
from src.refactored.assembly.tu_hoa_phai import build_tu_hoa_phai_layer
from src.refactored.components.definitions.cung_role import Role
from src.refactored.model.elementary import DiaChi
from src.refactored.context.natal import NatalContext
from src.refactored.model.prior import Gender, LaSoPrior
from src.refactored.context.tu_hoa_phai import TuHoaPhaiContext
from src.refactored.components.definitions.ban_menh import BanMenh, compute_ban_menh_id
from src.refactored.la_so import LaSo
from src.refactored.model.elementary import NguHanh
import pytest

from src.refactored.model.layer import PlacementLayer, TieuHanLayerId, TuHoaPhaiLayerId


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

    assert tinh_ban.period_layers.layers == {}


def test_build_tu_hoa_phai_layer_uses_scope_and_natal_seed():
    ctx = NatalContext.from_prior(_prior())
    tinh_ban = build_natal_tinh_ban(ctx)
    cung_id = tinh_ban.cung_ids[DiaChi.TY]
    tu_hoa_phai_context = TuHoaPhaiContext(
        source_dia_chi=cung_id.dia_chi,
        thien_can=cung_id.thien_can,
    )

    layer = build_tu_hoa_phai_layer(
        layer_id=TuHoaPhaiLayerId(source_dia_chi=cung_id.dia_chi),
        context=tu_hoa_phai_context,
        natal_layer=tinh_ban.natal_layer,
    )

    assert set(layer.by_component) == {"hoa_loc", "hoa_quyen", "hoa_khoa", "hoa_ky"}


def test_laso_from_prior_wraps_tinh_ban_and_catalog():
    la_so = LaSo.from_prior(_prior())

    assert la_so.component("tu_vi").name == "Tử Vi"
    assert la_so.position_of("tu_vi") is not None


def test_laso_from_prior_computes_ban_menh_from_year():
    la_so = LaSo.from_prior(_prior())

    assert isinstance(la_so.ban_menh, BanMenh)
    assert la_so.ban_menh.id == "gian_ha_thuy"
    assert la_so.ban_menh.ngu_hanh == NguHanh.THUY


def test_compute_ban_menh_id_cycle():
    assert compute_ban_menh_id(1900) == "bich_thuong_tho"
    assert compute_ban_menh_id(1948) == "tich_lich_hoa"
    assert compute_ban_menh_id(1949) == "tich_lich_hoa"
    assert compute_ban_menh_id(1950) == "tung_bach_moc"
    assert compute_ban_menh_id(2008) == "tich_lich_hoa"
    assert compute_ban_menh_id(2009) == "tich_lich_hoa"
    assert compute_ban_menh_id(1930) == "lo_bang_tho"
    assert compute_ban_menh_id(2050) == "lo_bang_tho"
    assert compute_ban_menh_id(1996) == "gian_ha_thuy"
    assert compute_ban_menh_id(1997) == "gian_ha_thuy"
    assert compute_ban_menh_id(2000) == "bach_lap_kim"
    assert compute_ban_menh_id(2001) == "bach_lap_kim"


@dataclass(frozen=True)
class _FakePeriodContext:
    focus_position: DiaChi


def test_tinh_ban_period_layer_cache_is_lru_by_layer_kind():
    ctx = NatalContext.from_prior(_prior())
    tinh_ban = build_natal_tinh_ban(ctx)

    # Force the cache to only keep 2 layers per kind,
    # so we can test eviction logic without building too many layers
    tinh_ban.period_layers.cache.max_layers_per_kind = 2

    build_count = 0

    def _build_layer(layer_id: TieuHanLayerId, context: _FakePeriodContext):
        def _build() -> PlacementLayer:
            nonlocal build_count
            build_count += 1
            return PlacementLayer.from_component_positions(
                id=layer_id,
                positions={"thai_tue": context.focus_position},
                focus_position=context.focus_position,
            )
        return _build

    first_layer_id = TieuHanLayerId(2026)
    second_layer_id = TieuHanLayerId(2027)
    third_layer_id = TieuHanLayerId(2028)

    first = _FakePeriodContext(DiaChi.TY)
    second = _FakePeriodContext(DiaChi.SUU)
    third = _FakePeriodContext(DiaChi.DAN)

    tinh_ban.period_layer(first_layer_id, _build_layer(first_layer_id, first))
    tinh_ban.period_layer(second_layer_id, _build_layer(second_layer_id, second))
    tinh_ban.period_layer(first_layer_id, _build_layer(first_layer_id, first))
    tinh_ban.period_layer(third_layer_id, _build_layer(third_layer_id, third))

    assert build_count == 3
    assert first_layer_id in tinh_ban.period_layers.layers
    assert second_layer_id not in tinh_ban.period_layers.layers
    assert third_layer_id in tinh_ban.period_layers.layers


def test_tinh_ban_period_layer_rejects_non_period_layer_id():
    ctx = NatalContext.from_prior(_prior())
    tinh_ban = build_natal_tinh_ban(ctx)

    with pytest.raises(ValueError, match="Expected period layer id"):
        tinh_ban.period_layer(
            TuHoaPhaiLayerId(source_dia_chi=DiaChi.TY),  # type: ignore[arg-type]
            lambda: PlacementLayer.from_component_positions(
                id=TuHoaPhaiLayerId(source_dia_chi=DiaChi.TY),
                positions={},
            ),
        )


def test_tinh_ban_period_layer_rejects_mismatched_built_layer_id():
    ctx = NatalContext.from_prior(_prior())
    tinh_ban = build_natal_tinh_ban(ctx)

    with pytest.raises(ValueError, match="does not match requested"):
        tinh_ban.period_layer(
            TieuHanLayerId(2026),
            lambda: PlacementLayer.from_component_positions(
                id=TieuHanLayerId(2027),
                positions={},
            ),
        )
