import pytest

from src.refactored.element.dia_chi import DiaChi
from src.refactored.transform import (
    get_luc_hai,
    get_nhi_hop,
    get_tam_hop,
    get_tam_hop_nghich,
    get_tam_hop_thuan,
    get_xung_chieu,
)


def test_get_xung_chieu():
    assert get_xung_chieu(DiaChi.Ty) == DiaChi.Ngo
    assert get_xung_chieu(DiaChi.Suu) == DiaChi.Mui
    assert get_xung_chieu(DiaChi.Dan) == DiaChi.Than
    assert get_xung_chieu(DiaChi.Meo) == DiaChi.Dau
    assert get_xung_chieu(DiaChi.Thin) == DiaChi.Tuat
    assert get_xung_chieu(DiaChi.Ti) == DiaChi.Hoi
    assert get_xung_chieu(DiaChi.Ngo) == DiaChi.Ty
    assert get_xung_chieu(DiaChi.Mui) == DiaChi.Suu
    assert get_xung_chieu(DiaChi.Than) == DiaChi.Dan
    assert get_xung_chieu(DiaChi.Dau) == DiaChi.Meo
    assert get_xung_chieu(DiaChi.Tuat) == DiaChi.Thin
    assert get_xung_chieu(DiaChi.Hoi) == DiaChi.Ti


def test_get_nhi_hop():
    assert get_nhi_hop(DiaChi.Ty) == DiaChi.Suu
    assert get_nhi_hop(DiaChi.Suu) == DiaChi.Ty
    assert get_nhi_hop(DiaChi.Dan) == DiaChi.Hoi
    assert get_nhi_hop(DiaChi.Meo) == DiaChi.Tuat
    assert get_nhi_hop(DiaChi.Thin) == DiaChi.Dau
    assert get_nhi_hop(DiaChi.Ti) == DiaChi.Than
    assert get_nhi_hop(DiaChi.Ngo) == DiaChi.Mui
    assert get_nhi_hop(DiaChi.Mui) == DiaChi.Ngo
    assert get_nhi_hop(DiaChi.Than) == DiaChi.Ti
    assert get_nhi_hop(DiaChi.Dau) == DiaChi.Thin
    assert get_nhi_hop(DiaChi.Tuat) == DiaChi.Meo
    assert get_nhi_hop(DiaChi.Hoi) == DiaChi.Dan


def test_get_luc_hai():
    assert get_luc_hai(DiaChi.Ty) == DiaChi.Mui
    assert get_luc_hai(DiaChi.Suu) == DiaChi.Ngo
    assert get_luc_hai(DiaChi.Dan) == DiaChi.Ti
    assert get_luc_hai(DiaChi.Meo) == DiaChi.Thin
    assert get_luc_hai(DiaChi.Thin) == DiaChi.Meo
    assert get_luc_hai(DiaChi.Ti) == DiaChi.Dan
    assert get_luc_hai(DiaChi.Ngo) == DiaChi.Suu
    assert get_luc_hai(DiaChi.Mui) == DiaChi.Ty
    assert get_luc_hai(DiaChi.Than) == DiaChi.Hoi
    assert get_luc_hai(DiaChi.Dau) == DiaChi.Tuat
    assert get_luc_hai(DiaChi.Tuat) == DiaChi.Dau
    assert get_luc_hai(DiaChi.Hoi) == DiaChi.Than


def test_get_tam_hop_thuan():
    assert get_tam_hop_thuan(DiaChi.Ty) == DiaChi.Thin
    assert get_tam_hop_thuan(DiaChi.Suu) == DiaChi.Ti
    assert get_tam_hop_thuan(DiaChi.Dan) == DiaChi.Ngo
    assert get_tam_hop_thuan(DiaChi.Meo) == DiaChi.Mui
    assert get_tam_hop_thuan(DiaChi.Thin) == DiaChi.Than
    assert get_tam_hop_thuan(DiaChi.Ti) == DiaChi.Dau
    assert get_tam_hop_thuan(DiaChi.Ngo) == DiaChi.Tuat
    assert get_tam_hop_thuan(DiaChi.Mui) == DiaChi.Hoi
    assert get_tam_hop_thuan(DiaChi.Than) == DiaChi.Ty
    assert get_tam_hop_thuan(DiaChi.Dau) == DiaChi.Suu
    assert get_tam_hop_thuan(DiaChi.Tuat) == DiaChi.Dan
    assert get_tam_hop_thuan(DiaChi.Hoi) == DiaChi.Meo


def test_get_tam_hop_nghich():
    assert get_tam_hop_nghich(DiaChi.Ty) == DiaChi.Than
    assert get_tam_hop_nghich(DiaChi.Suu) == DiaChi.Dau
    assert get_tam_hop_nghich(DiaChi.Dan) == DiaChi.Tuat
    assert get_tam_hop_nghich(DiaChi.Meo) == DiaChi.Hoi
    assert get_tam_hop_nghich(DiaChi.Thin) == DiaChi.Ty
    assert get_tam_hop_nghich(DiaChi.Ti) == DiaChi.Suu
    assert get_tam_hop_nghich(DiaChi.Ngo) == DiaChi.Dan
    assert get_tam_hop_nghich(DiaChi.Mui) == DiaChi.Meo
    assert get_tam_hop_nghich(DiaChi.Than) == DiaChi.Thin
    assert get_tam_hop_nghich(DiaChi.Dau) == DiaChi.Ti
    assert get_tam_hop_nghich(DiaChi.Tuat) == DiaChi.Ngo
    assert get_tam_hop_nghich(DiaChi.Hoi) == DiaChi.Mui


@pytest.mark.parametrize("position", DiaChi.list_dia_chi())
def test_get_tam_hop(position: DiaChi):
    assert get_tam_hop(position) == (
        get_tam_hop_thuan(position),
        get_tam_hop_nghich(position),
    )
