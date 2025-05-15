from src.refactored.element.dia_chi import DiaChi

def test_dia_chi():
    assert len(DiaChi.list_dia_chi()) == 12
    assert DiaChi.Ty - 1 == DiaChi.Hoi
    assert DiaChi.Ty - 11 == DiaChi.Suu
    assert DiaChi.Ty - 36 == DiaChi.Ty
    assert DiaChi.Thin + 3 == DiaChi.Mui
    assert DiaChi.Thin + 11 == DiaChi.Meo
    assert DiaChi.Thin + 36 == DiaChi.Thin
