from src.refactored.assembly.natal import build_natal_tinh_ban
from src.refactored.assembly.period import build_period_layer, build_period_layer_id
from src.refactored.model.elementary import CircleDirection, DiaChi
from src.refactored.context.natal import NatalContext
from src.refactored.context.period import (
    DaiHanContext,
    LuuNienDaiHanContext,
    PeriodKind,
    TieuHanContext,
    build_period_context,
)
from src.refactored.model.period_focus import (
    TenYearRange,
    build_dai_han_focus_map,
    build_tieu_han_focus_map,
    luu_nien_dai_han_focus_position,
)
from src.refactored.model.prior import Gender, LaSoPrior
from src.refactored.la_so import LaSo
from src.refactored.model.layer import (
    DaiHanLayerId,
    LuuNienDaiHanLayerId,
    TieuHanLayerId,
)
from src.refactored.placement.transforms import get_xung_chieu


def _prior() -> LaSoPrior:
    return LaSoPrior(
        hour=DiaChi.MEO,
        date=10,
        month=11,
        year=1996,
        gender=Gender.MALE,
    )


def test_tieu_han_focus_map_places_year_branches_from_static_anchor():
    focus_map = build_tieu_han_focus_map(
        natal_year_dia_chi=DiaChi.TY,
        van_direction=CircleDirection.CW,
    )

    assert focus_map[DiaChi.TY] == DiaChi.TUAT
    assert focus_map[DiaChi.SUU] == DiaChi.HOI
    assert focus_map[DiaChi.DAN] == DiaChi.TY


def test_dai_han_focus_map_places_ten_year_ranges_from_menh():
    ctx = NatalContext.from_prior(_prior())
    focus_map = build_dai_han_focus_map(
        cuc_number=ctx.cuc.number,
        menh_position=ctx.menh_position,
        van_direction=ctx.van_direction,
    )

    first_range = TenYearRange(start_age=ctx.cuc.number)
    second_range = TenYearRange(start_age=ctx.cuc.number + 10)
    assert focus_map.by_range[first_range] == ctx.menh_position
    assert focus_map[ctx.cuc.number] == ctx.menh_position
    assert focus_map.range_for_age(ctx.cuc.number + 10) == second_range
    assert focus_map[ctx.cuc.number + 10] == ctx.menh_position + ctx.van_direction


def test_build_natal_tinh_ban_stores_queryable_period_focus_maps():
    ctx = NatalContext.from_prior(_prior())
    tinh_ban = build_natal_tinh_ban(ctx)
    la_so = LaSo.from_prior(_prior())

    assert tinh_ban.period_focus_maps.tieu_han[DiaChi.TY] == DiaChi.TUAT
    assert la_so.tieu_han_focus_map() == dict(tinh_ban.period_focus_maps.tieu_han)
    assert la_so.dai_han_focus_map() == tinh_ban.period_focus_maps.dai_han


def test_period_assembly_derives_layer_ids_from_contexts():
    ctx = NatalContext.from_prior(_prior())
    tinh_ban = build_natal_tinh_ban(ctx)

    tieu_han = TieuHanContext.from_focus_maps(
        natal_context=ctx,
        year=2034,
        focus_maps=tinh_ban.period_focus_maps,
    )
    dai_han = DaiHanContext.from_focus_maps(
        natal_context=ctx,
        year=2002,
        focus_maps=tinh_ban.period_focus_maps,
        cung_ids=tinh_ban.cung_ids,
    )
    luu_nien = LuuNienDaiHanContext.from_dai_han_context(
        natal_context=ctx,
        year=2002,
        dai_han_context=dai_han,
    )

    assert build_period_layer_id(PeriodKind.TIEU_HAN, tieu_han) == TieuHanLayerId(
        year=2034
    )
    assert tieu_han.focus_position == tinh_ban.period_focus_maps.tieu_han[DiaChi.DAN]

    assert build_period_layer_id(PeriodKind.DAI_HAN, dai_han) == DaiHanLayerId(
        start_age=ctx.cuc.number,
        end_age=ctx.cuc.number + 9,
    )
    assert dai_han.age_range.start_age == ctx.cuc.number
    assert dai_han.thien_can == tinh_ban.cung_ids[dai_han.focus_position].thien_can

    assert build_period_layer_id(
        PeriodKind.LUU_NIEN_DAI_HAN,
        luu_nien,
    ) == LuuNienDaiHanLayerId(year=2002)
    assert luu_nien.focus_position == get_xung_chieu(dai_han.focus_position)


def test_luu_nien_dai_han_focus_rule_uses_dai_han_focus_and_age_delta():
    assert (
        luu_nien_dai_han_focus_position(
            dai_han_focus_position=DiaChi.DAN,
            dai_han_start_age=10,
            current_age=10,
            van_direction=CircleDirection.CW,
        )
        == DiaChi.DAN
    )
    assert (
        luu_nien_dai_han_focus_position(
            dai_han_focus_position=DiaChi.DAN,
            dai_han_start_age=10,
            current_age=11,
            van_direction=CircleDirection.CW,
        )
        == DiaChi.THAN
    )
    assert (
        luu_nien_dai_han_focus_position(
            dai_han_focus_position=DiaChi.DAN,
            dai_han_start_age=10,
            current_age=12,
            van_direction=CircleDirection.CW,
        )
        == DiaChi.MUI
    )


def test_build_period_layer_materializes_scope_and_focus_position():
    ctx = NatalContext.from_prior(_prior())
    tinh_ban = build_natal_tinh_ban(ctx)
    tieu_han = TieuHanContext.from_focus_maps(
        natal_context=ctx,
        year=2034,
        focus_maps=tinh_ban.period_focus_maps,
    )

    layer = build_period_layer(
        kind=PeriodKind.TIEU_HAN,
        context=tieu_han,
        tinh_ban=tinh_ban,
    )

    assert layer.id == TieuHanLayerId(year=2034)
    assert layer.focus_position == tieu_han.focus_position
    assert set(layer.by_component) == {
        "thai_tue",
        "bach_ho",
        "tang_mon",
        "thien_ma",
        "loc_ton",
        "kinh_duong",
        "da_la",
        "thien_khoc",
        "thien_hu",
        "hoa_loc",
        "hoa_quyen",
        "hoa_khoa",
        "hoa_ky",
    }


def test_build_period_context_factory_and_laso_period_layer_api():
    la_so = LaSo.from_prior(_prior())

    context = build_period_context(
        kind=PeriodKind.DAI_HAN,
        year=2002,
        natal_context=la_so.natal_context,
        focus_maps=la_so.tinh_ban.period_focus_maps,
        cung_ids=la_so.tinh_ban.cung_ids,
    )
    layer = la_so.period_layer(PeriodKind.DAI_HAN, year=2002)

    assert isinstance(context, DaiHanContext)
    assert layer.id == build_period_layer_id(PeriodKind.DAI_HAN, context)
    assert layer.focus_position == context.focus_position
