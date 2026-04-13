import pytest

from src.refactored.component.elementary import DiaChi
from src.refactored.placement.transforms import (
    get_luc_hai,
    get_nhi_hop,
    get_tam_hop,
    get_tam_hop_nghich,
    get_tam_hop_thuan,
    get_xung_chieu,
)


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


def test_get_tam_hop_thuan():
    assert get_tam_hop_thuan(DiaChi.TY) == DiaChi.THIN
    assert get_tam_hop_thuan(DiaChi.SUU) == DiaChi.TI
    assert get_tam_hop_thuan(DiaChi.DAN) == DiaChi.NGO
    assert get_tam_hop_thuan(DiaChi.MEO) == DiaChi.MUI
    assert get_tam_hop_thuan(DiaChi.THIN) == DiaChi.THAN
    assert get_tam_hop_thuan(DiaChi.TI) == DiaChi.DAU
    assert get_tam_hop_thuan(DiaChi.NGO) == DiaChi.TUAT
    assert get_tam_hop_thuan(DiaChi.MUI) == DiaChi.HOI
    assert get_tam_hop_thuan(DiaChi.THAN) == DiaChi.TY
    assert get_tam_hop_thuan(DiaChi.DAU) == DiaChi.SUU
    assert get_tam_hop_thuan(DiaChi.TUAT) == DiaChi.DAN
    assert get_tam_hop_thuan(DiaChi.HOI) == DiaChi.MEO


def test_get_tam_hop_nghich():
    assert get_tam_hop_nghich(DiaChi.TY) == DiaChi.THAN
    assert get_tam_hop_nghich(DiaChi.SUU) == DiaChi.DAU
    assert get_tam_hop_nghich(DiaChi.DAN) == DiaChi.TUAT
    assert get_tam_hop_nghich(DiaChi.MEO) == DiaChi.HOI
    assert get_tam_hop_nghich(DiaChi.THIN) == DiaChi.TY
    assert get_tam_hop_nghich(DiaChi.TI) == DiaChi.SUU
    assert get_tam_hop_nghich(DiaChi.NGO) == DiaChi.DAN
    assert get_tam_hop_nghich(DiaChi.MUI) == DiaChi.MEO
    assert get_tam_hop_nghich(DiaChi.THAN) == DiaChi.THIN
    assert get_tam_hop_nghich(DiaChi.DAU) == DiaChi.TI
    assert get_tam_hop_nghich(DiaChi.TUAT) == DiaChi.NGO
    assert get_tam_hop_nghich(DiaChi.HOI) == DiaChi.MUI


@pytest.mark.parametrize("position", DiaChi.list_dia_chi())
def test_get_tam_hop(position: DiaChi):
    assert get_tam_hop(position) == (
        get_tam_hop_thuan(position),
        get_tam_hop_nghich(position),
    )
