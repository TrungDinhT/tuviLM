from src.refactored.builder.component_catalog import get_default_catalog
from src.refactored.component.cung import Cung, Role
from src.refactored.component.elementary import NguHanh
from src.refactored.component.sao import Sao


def test_default_catalog_loads_cung_and_sao_components():
    catalog = get_default_catalog()

    menh = catalog.get("menh")
    thien_tai = catalog.get("thien_tai")
    ta_phu = catalog.get("ta_phu")
    dia_khong = catalog.get("dia_khong")
    tu_vi = catalog.get("tu_vi")
    loc_ton = catalog.get("loc_ton")

    assert isinstance(menh, Cung)
    assert menh.id == "menh"
    assert menh.name == "Mệnh"
    assert menh.role == Role.MENH

    assert isinstance(thien_tai, Sao)
    assert thien_tai.id == "thien_tai"
    assert thien_tai.name == "Thiên Tài"
    assert thien_tai.ngu_hanh == NguHanh.THO
    assert thien_tai.is_chinh_tinh is False
    assert thien_tai.sao_type == []

    assert isinstance(ta_phu, Sao)
    assert ta_phu.id == "ta_phu"
    assert ta_phu.name == "Tả Phù"
    assert ta_phu.ngu_hanh == NguHanh.THO
    assert ta_phu.is_chinh_tinh is False

    assert isinstance(dia_khong, Sao)
    assert dia_khong.id == "dia_khong"
    assert dia_khong.name == "Địa Không"
    assert dia_khong.ngu_hanh == NguHanh.HOA
    assert dia_khong.is_chinh_tinh is False

    assert isinstance(tu_vi, Sao)
    assert tu_vi.id == "tu_vi"
    assert tu_vi.name == "Tử Vi"
    assert tu_vi.ngu_hanh == NguHanh.THO
    assert tu_vi.is_chinh_tinh is True

    assert isinstance(loc_ton, Sao)
    assert loc_ton.id == "loc_ton"
    assert loc_ton.name == "Lộc Tồn"
    assert loc_ton.ngu_hanh == NguHanh.THO
    assert loc_ton.is_chinh_tinh is False


def test_default_catalog_get_many_preserves_requested_order():
    catalog = get_default_catalog()

    components = catalog.get_many(["thien_tho", "menh"])

    assert [component.name for component in components] == ["Thiên Thọ", "Mệnh"]
