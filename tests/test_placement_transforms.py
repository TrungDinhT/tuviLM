import pytest

from src.refactored.model.elementary import CircleDirection, DiaChi
from src.refactored.placement.transforms import (
    get_luc_hai,
    get_nhi_hop,
    get_tam_hop,
    get_xung_chieu,
    mirror_across,
)


@pytest.mark.parametrize(
    "axis, position, expected",
    [
        *[
            ((DiaChi.DAN, DiaChi.THAN), position, expected)
            for position, expected in {
                DiaChi.DAN: DiaChi.DAN,
                DiaChi.MEO: DiaChi.SUU,
                DiaChi.THIN: DiaChi.TY,
                DiaChi.TI: DiaChi.HOI,
                DiaChi.NGO: DiaChi.TUAT,
                DiaChi.MUI: DiaChi.DAU,
                DiaChi.THAN: DiaChi.THAN,
                DiaChi.DAU: DiaChi.MUI,
                DiaChi.TUAT: DiaChi.NGO,
                DiaChi.HOI: DiaChi.TI,
                DiaChi.TY: DiaChi.THIN,
                DiaChi.SUU: DiaChi.MEO,
            }.items()
        ],
        *[
            ((DiaChi.TI, DiaChi.HOI), position, expected)
            for position, expected in {
                DiaChi.TI: DiaChi.TI,
                DiaChi.NGO: DiaChi.THIN,
                DiaChi.MUI: DiaChi.MEO,
                DiaChi.THAN: DiaChi.DAN,
                DiaChi.DAU: DiaChi.SUU,
                DiaChi.TUAT: DiaChi.TY,
                DiaChi.HOI: DiaChi.HOI,
                DiaChi.TY: DiaChi.TUAT,
                DiaChi.SUU: DiaChi.DAU,
                DiaChi.DAN: DiaChi.THAN,
                DiaChi.MEO: DiaChi.MUI,
                DiaChi.THIN: DiaChi.NGO,
            }.items()
        ],
    ],
)
def test_mirror_across_axis_expected_mapping(
    axis: tuple[DiaChi, DiaChi], position: DiaChi, expected: DiaChi
):
    assert mirror_across(position, axis) == expected


@pytest.mark.parametrize(
    "position, axis",
    [
        (position, axis)
        for axis in (
            (DiaChi.DAN, DiaChi.THAN),
            (DiaChi.TI, DiaChi.HOI),
        )
        for position in DiaChi
    ],
)
def test_mirror_across_is_involution(
    position: DiaChi, axis: tuple[DiaChi, DiaChi]
):
    assert mirror_across(mirror_across(position, axis), axis) == position


def test_mirror_across_rejects_non_opposite_axis():
    with pytest.raises(ValueError):
        mirror_across(DiaChi.TY, (DiaChi.DAN, DiaChi.DAU))


def test_get_xung_chieu():
    assert get_xung_chieu(DiaChi.TY) == DiaChi.NGO
    assert get_xung_chieu(DiaChi.SUU) == DiaChi.MUI
    assert get_xung_chieu(DiaChi.DAN) == DiaChi.THAN
    assert get_xung_chieu(DiaChi.MEO) == DiaChi.DAU
    assert get_xung_chieu(DiaChi.THIN) == DiaChi.TUAT
    assert get_xung_chieu(DiaChi.TI) == DiaChi.HOI
    assert get_xung_chieu(DiaChi.NGO) == DiaChi.TY
    assert get_xung_chieu(DiaChi.MUI) == DiaChi.SUU
    assert get_xung_chieu(DiaChi.THAN) == DiaChi.DAN
    assert get_xung_chieu(DiaChi.DAU) == DiaChi.MEO
    assert get_xung_chieu(DiaChi.TUAT) == DiaChi.THIN
    assert get_xung_chieu(DiaChi.HOI) == DiaChi.TI


def test_get_nhi_hop():
    assert get_nhi_hop(DiaChi.TY) == DiaChi.SUU
    assert get_nhi_hop(DiaChi.SUU) == DiaChi.TY
    assert get_nhi_hop(DiaChi.DAN) == DiaChi.HOI
    assert get_nhi_hop(DiaChi.MEO) == DiaChi.TUAT
    assert get_nhi_hop(DiaChi.THIN) == DiaChi.DAU
    assert get_nhi_hop(DiaChi.TI) == DiaChi.THAN
    assert get_nhi_hop(DiaChi.NGO) == DiaChi.MUI
    assert get_nhi_hop(DiaChi.MUI) == DiaChi.NGO
    assert get_nhi_hop(DiaChi.THAN) == DiaChi.TI
    assert get_nhi_hop(DiaChi.DAU) == DiaChi.THIN
    assert get_nhi_hop(DiaChi.TUAT) == DiaChi.MEO
    assert get_nhi_hop(DiaChi.HOI) == DiaChi.DAN


def test_get_luc_hai():
    assert get_luc_hai(DiaChi.TY) == DiaChi.MUI
    assert get_luc_hai(DiaChi.SUU) == DiaChi.NGO
    assert get_luc_hai(DiaChi.DAN) == DiaChi.TI
    assert get_luc_hai(DiaChi.MEO) == DiaChi.THIN
    assert get_luc_hai(DiaChi.THIN) == DiaChi.MEO
    assert get_luc_hai(DiaChi.TI) == DiaChi.DAN
    assert get_luc_hai(DiaChi.NGO) == DiaChi.SUU
    assert get_luc_hai(DiaChi.MUI) == DiaChi.TY
    assert get_luc_hai(DiaChi.THAN) == DiaChi.HOI
    assert get_luc_hai(DiaChi.DAU) == DiaChi.TUAT
    assert get_luc_hai(DiaChi.TUAT) == DiaChi.DAU
    assert get_luc_hai(DiaChi.HOI) == DiaChi.THAN


@pytest.mark.parametrize(
    "direction, position, expected",
    [
        *[
            (CircleDirection.CW, position, expected)
            for position, expected in {
                DiaChi.TY: DiaChi.THIN,
                DiaChi.SUU: DiaChi.TI,
                DiaChi.DAN: DiaChi.NGO,
                DiaChi.MEO: DiaChi.MUI,
                DiaChi.THIN: DiaChi.THAN,
                DiaChi.TI: DiaChi.DAU,
                DiaChi.NGO: DiaChi.TUAT,
                DiaChi.MUI: DiaChi.HOI,
                DiaChi.THAN: DiaChi.TY,
                DiaChi.DAU: DiaChi.SUU,
                DiaChi.TUAT: DiaChi.DAN,
                DiaChi.HOI: DiaChi.MEO,
            }.items()
        ],
        *[
            (CircleDirection.CCW, position, expected)
            for position, expected in {
                DiaChi.TY: DiaChi.THAN,
                DiaChi.SUU: DiaChi.DAU,
                DiaChi.DAN: DiaChi.TUAT,
                DiaChi.MEO: DiaChi.HOI,
                DiaChi.THIN: DiaChi.TY,
                DiaChi.TI: DiaChi.SUU,
                DiaChi.NGO: DiaChi.DAN,
                DiaChi.MUI: DiaChi.MEO,
                DiaChi.THAN: DiaChi.THIN,
                DiaChi.DAU: DiaChi.TI,
                DiaChi.TUAT: DiaChi.NGO,
                DiaChi.HOI: DiaChi.MUI,
            }.items()
        ],
    ],
)
def test_get_tam_hop(
    direction: CircleDirection, position: DiaChi, expected: DiaChi
):
    assert get_tam_hop(position, direction) == expected
