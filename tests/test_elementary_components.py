import pytest

from src.refactored.components.definitions.elementary import (
    DiaChiEntity,
    ThienCanEntity,
)
from src.refactored.model.elementary import (
    DiaChi,
    NguHanh,
    ThienCan,
)


def test_dia_chi():
    assert len(DiaChi.list_dia_chi()) == 12
    assert DiaChi.TY - 1 == DiaChi.HOI
    assert DiaChi.TY - 11 == DiaChi.SUU
    assert DiaChi.TY - 36 == DiaChi.TY
    assert DiaChi.THIN + 3 == DiaChi.MUI
    assert DiaChi.THIN + 11 == DiaChi.MEO
    assert DiaChi.THIN + 36 == DiaChi.THIN


def test_cyclic_same_type_subtraction_returns_int_offset():
    assert DiaChi.DAN - DiaChi.DAN == 0
    assert DiaChi.MEO - DiaChi.DAN == 1
    assert DiaChi.SUU - DiaChi.DAN == 11
    assert DiaChi.TY - DiaChi.DAN == 10

    assert ThienCan.GIAP - ThienCan.GIAP == 0
    assert ThienCan.AT - ThienCan.GIAP == 1
    assert ThienCan.GIAP - ThienCan.QUY == 1
    assert ThienCan.QUY - ThienCan.GIAP == 9


def test_cyclic_subtraction_rejects_other_types():
    with pytest.raises(TypeError):
        _ = DiaChi.DAN - ThienCan.GIAP
    with pytest.raises(TypeError):
        _ = DiaChi.DAN - "dan"


def test_dia_chi_str_enum_and_cyclic_index():
    assert DiaChi.TY.value == "ty"
    assert str(DiaChi.TY) == "ty"
    assert DiaChi.TY.index == 0
    assert DiaChi("ty") == DiaChi.TY
    assert DiaChi.from_index(12) == DiaChi.TY
    assert DiaChi.from_index(-1) == DiaChi.HOI
    assert DiaChi.DAN.index == 2


def test_thien_can_str_enum_and_cyclic_index():
    assert ThienCan.GIAP.value == "giap"
    assert str(ThienCan.GIAP) == "giap"
    assert ThienCan.GIAP.index == 0
    assert ThienCan("giap") == ThienCan.GIAP
    assert ThienCan.from_index(10) == ThienCan.GIAP
    assert ThienCan.from_index(-1) == ThienCan.QUY
    assert ThienCan.CANH.index == 6
    assert ThienCan.GIAP + 1 == ThienCan.AT
    assert ThienCan.GIAP - 1 == ThienCan.QUY
    assert ThienCan.QUY + 30 == ThienCan.QUY


def test_ngu_hanh_str_enum_without_cyclic_arithmetic():
    assert NguHanh.KIM.value == "Kim"
    assert str(NguHanh.KIM) == "Kim"
    assert NguHanh("Kim") == NguHanh.KIM
    assert NguHanh.KIM.index == 1

    with pytest.raises(TypeError):
        _ = NguHanh.KIM + 1

    with pytest.raises(TypeError):
        _ = NguHanh.KIM - 1


def test_ngu_hanh_directional_relationships():
    assert NguHanh.HOA.sinh_xuat(NguHanh.THO)
    assert NguHanh.THO.sinh_nhap(NguHanh.HOA)
    assert not NguHanh.THO.sinh_xuat(NguHanh.HOA)
    assert not NguHanh.HOA.sinh_nhap(NguHanh.THO)

    assert NguHanh.THO.khac_xuat(NguHanh.THUY)
    assert NguHanh.THUY.khac_nhap(NguHanh.THO)
    assert not NguHanh.THUY.khac_xuat(NguHanh.THO)
    assert not NguHanh.THO.khac_nhap(NguHanh.THUY)

    assert NguHanh.HOA.tuong_sinh(NguHanh.THO)
    assert NguHanh.THO.tuong_sinh(NguHanh.HOA)
    assert NguHanh.THO.tuong_khac(NguHanh.THUY)
    assert NguHanh.THUY.tuong_khac(NguHanh.THO)


def test_thien_can_entity_missing_id_raises():
    with pytest.raises(Exception):
        ThienCanEntity(name="Giáp", ngu_hanh=NguHanh.MOC)


def test_thien_can_entity_missing_name_raises():
    with pytest.raises(Exception):
        ThienCanEntity(id="giap", ngu_hanh=NguHanh.MOC)


def test_dia_chi_entity_missing_id_raises():
    with pytest.raises(Exception):
        DiaChiEntity(name="Tý", ngu_hanh=NguHanh.THUY)


def test_dia_chi_entity_missing_name_raises():
    with pytest.raises(Exception):
        DiaChiEntity(id="ty", ngu_hanh=NguHanh.THUY)
