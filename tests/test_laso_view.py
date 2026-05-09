import pytest
from pydantic import ValidationError

from src.refactored.component.elementary import DiaChi
from src.refactored.context.prior import Gender, LaSoPrior
from src.refactored.la_so import LaSo
from src.refactored.placement.layer import LayerKind
from src.refactored.view.builder import build_laso_view
from src.refactored.view.streamlit_adapter import (
    laso_view_to_streamlit_payload,
    render_laso_view_html,
)


def _prior() -> LaSoPrior:
    return LaSoPrior(
        hour=DiaChi.MEO,
        date=10,
        month=11,
        year=1996,
        gender=Gender.MALE,
    )


def test_build_laso_view_materializes_catalog_enriched_period_snapshot():
    la_so = LaSo.from_prior(_prior())

    view = build_laso_view(la_so, study_year=2034)

    assert view.hour == DiaChi.MEO
    assert view.year == 1996
    assert view.study_year == 2034
    assert view.dia_chi_natal_year == la_so.prior.dia_chi
    assert view.thien_can_natal_year == la_so.prior.thien_can
    assert len(view.cungs) == 12
    assert len(view.tieu_han_focus_map) == 12
    assert len(view.dai_han_focus_map) == 12
    assert view.tieu_han_focus_map[0].year_dia_chi == DiaChi.TY
    assert view.dai_han_focus_map[0].start_age == la_so.natal_context.cuc.number
    assert view.dai_han_focus_map[0].end_age == la_so.natal_context.cuc.number + 9

    ty_cung = next(
        cung
        for cung in view.cungs
        if cung.dia_chi_entity.value == DiaChi.TY
    )
    assert ty_cung.role.id
    assert ty_cung.thien_can_entity.id
    assert any(
        component.layer_kind == LayerKind.NATAL
        for component in ty_cung.components
    )
    assert any(
        component.layer_kind == LayerKind.TIEU_HAN
        for cung in view.cungs
        for component in cung.components
    )
    assert any(
        component.layer_kind == LayerKind.DAI_HAN
        for cung in view.cungs
        for component in cung.components
    )
    assert any(
        component.layer_kind == LayerKind.LUU_NIEN_DAI_HAN
        for cung in view.cungs
        for component in cung.components
    )


def test_laso_view_is_immutable_and_serializable():
    view = build_laso_view(LaSo.from_prior(_prior()), study_year=2034)

    dumped = view.model_dump(mode="json")

    assert dumped["hour"] == "meo"
    assert dumped["study_year"] == 2034
    assert isinstance(dumped["tieu_han_focus_map"], list)
    assert isinstance(dumped["dai_han_focus_map"], list)
    assert isinstance(dumped["cungs"], list)
    with pytest.raises(ValidationError):
        view.study_year = 2035


def test_streamlit_adapter_creates_render_payload_without_old_tinh_ban_shape():
    view = build_laso_view(LaSo.from_prior(_prior()), study_year=2034)

    payload = laso_view_to_streamlit_payload(view)
    html = render_laso_view_html(view)

    assert DiaChi.TY in payload.cells
    assert payload.cells[DiaChi.TY].components
    assert "map_cung" not in type(payload).model_fields
    assert "<table" in html
    assert "Năm xem: 2034" in html
    assert "Tiểu hạn" in html
    assert "Đại hạn" in html
    assert "component-layer-title" in html
