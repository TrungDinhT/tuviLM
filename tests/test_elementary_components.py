from src.refactored.component.elementary import DiaChi

def test_dia_chi():
    assert len(DiaChi.list_dia_chi()) == 12
    assert DiaChi.TY - 1 == DiaChi.HOI
    assert DiaChi.TY - 11 == DiaChi.SUU
    assert DiaChi.TY - 36 == DiaChi.TY
    assert DiaChi.THIN + 3 == DiaChi.MUI
    assert DiaChi.THIN + 11 == DiaChi.MEO
    assert DiaChi.THIN + 36 == DiaChi.THIN
