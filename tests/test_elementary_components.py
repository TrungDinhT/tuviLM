from src.refactored.component.elementary import DiaChi, ThienCan


def test_dia_chi():
    assert len(DiaChi.list_dia_chi()) == 12
    assert DiaChi.TY - 1 == DiaChi.HOI
    assert DiaChi.TY - 11 == DiaChi.SUU
    assert DiaChi.TY - 36 == DiaChi.TY
    assert DiaChi.THIN + 3 == DiaChi.MUI
    assert DiaChi.THIN + 11 == DiaChi.MEO
    assert DiaChi.THIN + 36 == DiaChi.THIN


def test_dia_chi_str_enum_and_cyclic_index():
    assert DiaChi.TY.value == "Tý"
    assert str(DiaChi.TY) == "Tý"
    assert DiaChi.TY.index == 0
    assert DiaChi("Tý") == DiaChi.TY
    assert DiaChi.from_index(12) == DiaChi.TY
    assert DiaChi.from_index(-1) == DiaChi.HOI
    assert DiaChi.DAN.index == 2


def test_thien_can_str_enum_and_cyclic_index():
    assert ThienCan.GIAP.value == "Giáp"
    assert str(ThienCan.GIAP) == "Giáp"
    assert ThienCan.GIAP.index == 0
    assert ThienCan("Giáp") == ThienCan.GIAP
    assert ThienCan.from_index(10) == ThienCan.GIAP
    assert ThienCan.from_index(-1) == ThienCan.QUY
    assert ThienCan.CANH.index == 6
    assert ThienCan.GIAP + 1 == ThienCan.AT
    assert ThienCan.GIAP - 1 == ThienCan.QUY
    assert ThienCan.QUY + 30 == ThienCan.QUY
