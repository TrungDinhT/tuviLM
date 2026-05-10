import pytest

from src.refactored.components.definitions.sao import Status


def test_status_values_and_lookup():
    assert Status.HAM.value == "Hãm"
    assert Status.BINH.value == "Bình"
    assert Status.DAC.value == "Đắc"
    assert Status.VUONG.value == "Vượng"
    assert Status.MIEU.value == "Miếu"
    assert Status.NONE.value == "Không xác định"
    assert Status("Hãm") is Status.HAM


def test_status_none_maps_to_none_member():
    assert Status(None) is Status.NONE


def test_status_invalid_value_raises():
    with pytest.raises(ValueError):
        Status("khong-hop-le")
