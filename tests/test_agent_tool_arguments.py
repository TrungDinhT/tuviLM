from __future__ import annotations

import pytest
from pydantic_ai import Agent, ModelRetry

from src.agent.tool.book import read_catalog
from src.agent.tool.cach_cuc.models import SourceKind
from src.agent.tool.cach_cuc.tool import get_list_cach_cuc
from src.agent.tool.chart import (
    get_cung_by_position,
    get_cung_by_role,
    get_tam_hop,
    get_xung_chieu,
)
from src.agent.tool.guidance import get_role_instruction
from src.agent.tool.phu_tinh.tool import (
    get_phu_tinh_tam_phuong_tu_chinh,
    get_trang_sinh,
)
from src.agent.tool.tu_vi_tan_bien.tool import get_star_role_interaction
from src.refactored.components.definitions.cung_role import Role
from src.refactored.model.elementary import DiaChi


def _validate_tool_arguments(tool, arguments: dict[str, object]) -> dict[str, object]:
    agent = Agent("test", tools=[tool])
    registered_tool = agent.toolsets[0].tools[tool.__name__]
    return registered_tool.function_schema.validator.validate_python(arguments)


def test_role_instruction_keeps_cung_than_unsupported() -> None:
    arguments = _validate_tool_arguments(
        get_role_instruction, {"role": Role.CUNG_THAN.value}
    )

    assert arguments["role"] is Role.CUNG_THAN
    with pytest.raises(ModelRetry):
        get_role_instruction(arguments["role"])


@pytest.mark.parametrize(
    ("tool", "parameter", "string_value", "typed_value"),
    [
        (get_cung_by_position, "position", DiaChi.TY.value, DiaChi.TY),
        (get_cung_by_role, "role", Role.MENH.value, Role.MENH),
        (
            get_list_cach_cuc,
            "source_kind",
            SourceKind.TUVITANBIEN.value,
            SourceKind.TUVITANBIEN,
        ),
        (
            get_phu_tinh_tam_phuong_tu_chinh,
            "role",
            Role.MENH.value,
            Role.MENH,
        ),
        (get_trang_sinh, "role", Role.MENH.value, Role.MENH),
        (get_tam_hop, "position", DiaChi.TY.value, DiaChi.TY),
        (get_xung_chieu, "position", DiaChi.TY.value, DiaChi.TY),
        (get_star_role_interaction, "role", Role.MENH.value, Role.MENH),
        (get_role_instruction, "role", Role.MENH.value, Role.MENH),
        (read_catalog, "depth", "3", 3),
    ],
)
def test_scalar_tool_argument_string_validates_like_typed_value(
    tool, parameter: str, string_value: str, typed_value: object
) -> None:
    required_arguments = (
        {"star_name": "Tử Vi"} if tool is get_star_role_interaction else {}
    )
    from_string = _validate_tool_arguments(
        tool, {**required_arguments, parameter: string_value}
    )[parameter]
    from_typed_value = _validate_tool_arguments(
        tool, {**required_arguments, parameter: typed_value}
    )[parameter]

    assert from_string == from_typed_value == typed_value
    assert type(from_string) is type(typed_value)
