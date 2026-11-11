from __future__ import annotations

from src.refactored.context.period import PeriodKind
from src.refactored.model.cung import Cung
from src.refactored.la_so import LaSo
from src.refactored.model.layer import NATAL_LAYER_ID
from src.refactored.model.elementary import DiaChi
from src.refactored.view.models import (
    CungView,
    DaiHanFocusView,
    LaSoView,
    LayeredComponentView,
    TieuHanFocusView,
)


def build_laso_view(la_so: LaSo, study_year: int) -> LaSoView:
    period_layers = (
        la_so.period_layer(PeriodKind.TIEU_HAN, study_year),
        la_so.period_layer(PeriodKind.DAI_HAN, study_year),
        la_so.period_layer(PeriodKind.LUU_NIEN_DAI_HAN, study_year),
    )
    layer_ids = (NATAL_LAYER_ID, *(layer.id for layer in period_layers))

    return LaSoView(
        hour=la_so.prior.hour,
        date=la_so.prior.date,
        month=la_so.prior.month,
        year=la_so.prior.year,
        gender=la_so.prior.gender,
        dia_chi_natal_year=la_so.prior.dia_chi,
        thien_can_natal_year=la_so.prior.thien_can,
        study_year=study_year,
        ban_menh_name=la_so.ban_menh.name,
        cuc_name=la_so.natal_context.cuc.name,
        menh_cuc_relation_label=la_so.menh_cuc_relation().label,
        tieu_han_focus_map=build_tieu_han_focus_view(la_so),
        dai_han_focus_map=build_dai_han_focus_view(la_so),
        cungs=tuple(
            build_cung_view(
                la_so=la_so,
                cung=la_so.cung_at(dia_chi, layer_ids=layer_ids),
            )
            for dia_chi in DiaChi
        ),
    )


def build_tieu_han_focus_view(la_so: LaSo) -> tuple[TieuHanFocusView, ...]:
    focus_map = la_so.tieu_han_focus_map()
    return tuple(
        TieuHanFocusView(
            year_dia_chi=year_dia_chi,
            focus_position=focus_map[year_dia_chi],
        )
        for year_dia_chi in DiaChi
    )


def build_dai_han_focus_view(la_so: LaSo) -> tuple[DaiHanFocusView, ...]:
    focus_map = la_so.dai_han_focus_map()
    return tuple(
        DaiHanFocusView(
            start_age=age_range.start_age,
            end_age=age_range.end_age,
            focus_position=focus_position,
        )
        for age_range, focus_position in sorted(
            focus_map.by_range.items(),
            key=lambda item: item[0].start_age,
        )
    )


def build_cung_view(*, la_so: LaSo, cung: Cung) -> CungView:
    return CungView(
        dia_chi_entity=la_so.catalog.get_dia_chi(cung.dia_chi),
        thien_can_entity=la_so.catalog.get_thien_can(cung.thien_can),
        role=la_so.catalog.get(cung.natal_role.value),
        is_cung_than=cung.is_cung_than,
        components=tuple(
            LayeredComponentView(
                layer_kind=layered_component.layer_id.kind,
                component=la_so.catalog.get(layered_component.component_id),
            )
            for layered_component in cung.components
        ),
    )
