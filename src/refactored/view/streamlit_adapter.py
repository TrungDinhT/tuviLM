from __future__ import annotations

from html import escape
from typing import Mapping

from pydantic import BaseModel, ConfigDict

from src.refactored.component.elementary import DiaChi
from src.refactored.placement.layer import LayerKind
from src.refactored.view.models import CungView, LaSoView


class StreamlitComponentLine(BaseModel):
    model_config = ConfigDict(frozen=True)

    layer_kind: LayerKind
    name: str


class StreamlitCungCell(BaseModel):
    model_config = ConfigDict(frozen=True)

    dia_chi: DiaChi
    title: str
    subtitle: str
    components: tuple[StreamlitComponentLine, ...]


class StreamlitLaSoPayload(BaseModel):
    model_config = ConfigDict(frozen=True)

    common_info: str
    cells: Mapping[DiaChi, StreamlitCungCell]


HTML_TABLE_TEMPLATE = """
<style>
    .custom-table {{
        width: 100%;
        border-collapse: collapse;
    }}
    .custom-table, .custom-table th, .custom-table td {{
        border: 1px solid black;
    }}
    .custom-table td {{
        width: 1000px;
        min-height: 150px;
        text-align: center;
        vertical-align: top;
    }}
    .cung-cell {{
        padding: 6px;
        font-size: 14px;
    }}
    .cung-title {{
        font-weight: 700;
        font-size: 18px;
        margin-bottom: 4px;
    }}
    .cung-meta {{
        font-size: 12px;
        color: #555;
        margin-bottom: 8px;
    }}
    .component-row {{
        margin: 2px 0;
        white-space: nowrap;
    }}
    .component-layer-block {{
        margin-top: 10px;
        padding-top: 6px;
        border-top: 1px solid #999;
        background: #fafafa;
    }}
    .component-layer-block:first-child {{
        margin-top: 0;
        border-top: 0;
    }}
    .component-layer-title {{
        margin-bottom: 4px;
        color: #444;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
    }}
    .layer-tag {{
        color: #777;
        font-size: 11px;
    }}
    .focus-map {{
        margin-top: 10px;
        text-align: left;
        font-size: 12px;
    }}
    .focus-map-title {{
        margin-top: 8px;
        font-weight: 700;
    }}
    .focus-map-row {{
        margin: 1px 0;
    }}
    .merged-cell {{
        grid-column: span 2;
        grid-row: span 2;
    }}
</style>

<table class="custom-table"; table-layout: auto;>
    <tr>
        <td>{cung_1}</td>
        <td>{cung_2}</td>
        <td>{cung_3}</td>
        <td>{cung_4}</td>
    </tr>
    <tr>
        <td>{cung_5}</td>
        <td class="merged-cell" rowspan="2" colspan="2">{common_info}</td>
        <td>{cung_6}</td>
    </tr>
    <tr>
        <td>{cung_7}</td>
        <td>{cung_8}</td>
    </tr>
    <tr>
        <td>{cung_9}</td>
        <td>{cung_10}</td>
        <td>{cung_11}</td>
        <td>{cung_12}</td>
    </tr>
</table>
"""

CHART_TABLE_ORDER: tuple[DiaChi, ...] = (
    DiaChi.TI,
    DiaChi.NGO,
    DiaChi.MUI,
    DiaChi.THAN,
    DiaChi.THIN,
    DiaChi.DAU,
    DiaChi.MEO,
    DiaChi.TUAT,
    DiaChi.DAN,
    DiaChi.SUU,
    DiaChi.TY,
    DiaChi.HOI,
)


def laso_view_to_streamlit_payload(view: LaSoView) -> StreamlitLaSoPayload:
    cells = {
        cung.dia_chi_entity.value: cung_view_to_streamlit_cell(cung)
        for cung in view.cungs
    }
    common_info = (
        f"Ngày âm lịch: {view.date}/{view.month}/{view.year}<br>"
        f"Giờ sinh: {view.hour.value}<br>"
        f"Giới tính: {view.gender.value}<br>"
        f"Năm xem: {view.study_year}"
        f"{_render_focus_maps(view)}"
    )
    return StreamlitLaSoPayload(common_info=common_info, cells=cells)


def cung_view_to_streamlit_cell(cung: CungView) -> StreamlitCungCell:
    title = cung.role.name + (" - Thân" if cung.is_cung_than else "")
    subtitle = f"{cung.thien_can_entity.name} {cung.dia_chi_entity.name}"
    return StreamlitCungCell(
        dia_chi=cung.dia_chi_entity.value,
        title=title,
        subtitle=subtitle,
        components=tuple(
            StreamlitComponentLine(
                layer_kind=component.layer_kind,
                name=component.component.name,
            )
            for component in cung.components
        ),
    )


def render_laso_view_html(view: LaSoView) -> str:
    return render_streamlit_payload_html(laso_view_to_streamlit_payload(view))


def render_streamlit_payload_html(payload: StreamlitLaSoPayload) -> str:
    rendered_cells = {
        f"cung_{idx}": render_streamlit_cung_cell_html(payload.cells[dia_chi])
        for idx, dia_chi in enumerate(CHART_TABLE_ORDER, start=1)
    }
    return HTML_TABLE_TEMPLATE.format(
        **rendered_cells,
        common_info=payload.common_info,
    )


def render_streamlit_cung_cell_html(cell: StreamlitCungCell) -> str:
    component_blocks = tuple(
        _render_component_layer_block(layer_kind, components)
        for layer_kind, components in _group_components_by_layer(cell.components)
    )
    return (
        "<div class='cung-cell'>"
        f"<div class='cung-title'>{escape(cell.title)}</div>"
        f"<div class='cung-meta'>{escape(cell.subtitle)}</div>"
        + "".join(component_blocks)
        + "</div>"
    )


def _group_components_by_layer(
    components: tuple[StreamlitComponentLine, ...],
) -> tuple[tuple[LayerKind, tuple[StreamlitComponentLine, ...]], ...]:
    groups: list[tuple[LayerKind, list[StreamlitComponentLine]]] = []
    for component in components:
        if not groups or groups[-1][0] != component.layer_kind:
            groups.append((component.layer_kind, []))
        groups[-1][1].append(component)
    return tuple((layer_kind, tuple(items)) for layer_kind, items in groups)


def _render_component_layer_block(
    layer_kind: LayerKind,
    components: tuple[StreamlitComponentLine, ...],
) -> str:
    component_rows = tuple(
        "<p class='component-row'>"
        f"{escape(component.name)} "
        f"<span class='layer-tag'>[{escape(layer_kind.value)}]</span>"
        "</p>"
        for component in components
    )
    return (
        "<div class='component-layer-block'>"
        f"<div class='component-layer-title'>{escape(layer_kind.value)}</div>"
        + "".join(component_rows)
        + "</div>"
    )


def _render_focus_maps(view: LaSoView) -> str:
    tieu_han_rows = tuple(
        "<div class='focus-map-row'>"
        f"{escape(row.year_dia_chi.value)} -> {escape(row.focus_position.value)}"
        "</div>"
        for row in view.tieu_han_focus_map
    )
    dai_han_rows = tuple(
        "<div class='focus-map-row'>"
        f"{row.start_age}-{row.end_age} -> {escape(row.focus_position.value)}"
        "</div>"
        for row in view.dai_han_focus_map
    )
    return (
        "<div class='focus-map'>"
        "<div class='focus-map-title'>Tiểu hạn</div>"
        + "".join(tieu_han_rows)
        + "<div class='focus-map-title'>Đại hạn</div>"
        + "".join(dai_han_rows)
        + "</div>"
    )
