from src.refactored.builder.component_catalog import get_default_catalog
from src.refactored.component.cung import Cung, Role
from src.refactored.component.elementary import NguHanh
from src.refactored.component.sao import Sao


def test_default_catalog_loads_cung_and_sao_components():
    catalog = get_default_catalog()

    menh = catalog.get("menh")
    thien_tai = catalog.get("thien_tai")

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


def test_default_catalog_get_many_preserves_requested_order():
    catalog = get_default_catalog()

    components = catalog.get_many(["thien_tho", "menh"])

    assert [component.name for component in components] == ["Thiên Thọ", "Mệnh"]
