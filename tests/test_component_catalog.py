from src.refactored.component_catalog import get_default_catalog
from src.refactored.component.cung import CungRole, Role
from src.refactored.component.elementary import DiaChi, NguHanh, ThienCan
from src.refactored.component.sao import ChinhPhuTinh, TuHoa


def test_default_catalog_loads_cung_and_sao_components():
    catalog = get_default_catalog()

    menh = catalog.get("menh")
    thien_tai = catalog.get("thien_tai")
    ta_phu = catalog.get("ta_phu")
    thien_khoi = catalog.get("thien_khoi")
    co_than = catalog.get("co_than")
    dau_quan = catalog.get("dau_quan")
    hoa_tinh = catalog.get("hoa_tinh")
    dia_khong = catalog.get("dia_khong")
    tu_vi = catalog.get("tu_vi")
    loc_ton = catalog.get("loc_ton")
    hoa_loc = catalog.get("hoa_loc")
    hoa_quyen = catalog.get("hoa_quyen")
    hoa_khoa = catalog.get("hoa_khoa")
    hoa_ky = catalog.get("hoa_ky")

    assert isinstance(menh, CungRole)
    assert menh.id == "menh"
    assert menh.name == "Mệnh"
    assert menh.role == Role.MENH

    assert isinstance(thien_tai, ChinhPhuTinh)
    assert thien_tai.id == "thien_tai"
    assert thien_tai.name == "Thiên Tài"
    assert thien_tai.ngu_hanh == NguHanh.THO
    assert thien_tai.is_chinh_tinh is False
    assert thien_tai.sao_type == []

    assert isinstance(ta_phu, ChinhPhuTinh)
    assert ta_phu.id == "ta_phu"
    assert ta_phu.name == "Tả Phù"
    assert ta_phu.ngu_hanh == NguHanh.THO
    assert ta_phu.is_chinh_tinh is False

    assert isinstance(thien_khoi, ChinhPhuTinh)
    assert thien_khoi.id == "thien_khoi"
    assert thien_khoi.name == "Thiên Khôi"
    assert thien_khoi.ngu_hanh == NguHanh.HOA
    assert thien_khoi.is_chinh_tinh is False

    assert isinstance(co_than, ChinhPhuTinh)
    assert co_than.id == "co_than"
    assert co_than.name == "Cô Thần"
    assert co_than.ngu_hanh == NguHanh.THO
    assert co_than.is_chinh_tinh is False

    assert isinstance(dau_quan, ChinhPhuTinh)
    assert dau_quan.id == "dau_quan"
    assert dau_quan.name == "Đẩu Quân"
    assert dau_quan.ngu_hanh == NguHanh.HOA
    assert dau_quan.is_chinh_tinh is False

    assert isinstance(hoa_tinh, ChinhPhuTinh)
    assert hoa_tinh.id == "hoa_tinh"
    assert hoa_tinh.name == "Hỏa Tinh"
    assert hoa_tinh.ngu_hanh == NguHanh.HOA
    assert hoa_tinh.is_chinh_tinh is False

    assert isinstance(dia_khong, ChinhPhuTinh)
    assert dia_khong.id == "dia_khong"
    assert dia_khong.name == "Địa Không"
    assert dia_khong.ngu_hanh == NguHanh.HOA
    assert dia_khong.is_chinh_tinh is False

    assert isinstance(tu_vi, ChinhPhuTinh)
    assert tu_vi.id == "tu_vi"
    assert tu_vi.name == "Tử Vi"
    assert tu_vi.ngu_hanh == NguHanh.THO
    assert tu_vi.is_chinh_tinh is True

    assert isinstance(loc_ton, ChinhPhuTinh)
    assert loc_ton.id == "loc_ton"
    assert loc_ton.name == "Lộc Tồn"
    assert loc_ton.ngu_hanh == NguHanh.THO
    assert loc_ton.is_chinh_tinh is False

    assert isinstance(hoa_loc, TuHoa)
    assert hoa_loc.id == "hoa_loc"
    assert hoa_loc.name == "Hóa Lộc"
    assert hoa_loc.ngu_hanh == NguHanh.THO

    assert isinstance(hoa_quyen, TuHoa)
    assert hoa_quyen.id == "hoa_quyen"
    assert hoa_quyen.name == "Hóa Quyền"
    assert hoa_quyen.ngu_hanh == NguHanh.MOC

    assert isinstance(hoa_khoa, TuHoa)
    assert hoa_khoa.id == "hoa_khoa"
    assert hoa_khoa.name == "Hóa Khoa"
    assert hoa_khoa.ngu_hanh == NguHanh.THUY

    assert isinstance(hoa_ky, TuHoa)
    assert hoa_ky.id == "hoa_ky"
    assert hoa_ky.name == "Hóa Kỵ"
    assert hoa_ky.ngu_hanh == NguHanh.THUY


def test_default_catalog_get_many_preserves_requested_order():
    catalog = get_default_catalog()

    components = catalog.get_many(["thien_tho", "menh"])

    assert [component.name for component in components] == ["Thiên Thọ", "Mệnh"]


def test_default_catalog_loads_structural_entities():
    catalog = get_default_catalog()

    ty = catalog.get_dia_chi(DiaChi.TY)
    giap = catalog.get_thien_can(ThienCan.GIAP)

    assert ty.id == "ty"
    assert ty.name == "Tý"
    assert ty.value == DiaChi.TY
    assert ty.ngu_hanh == NguHanh.THUY

    assert giap.id == "giap"
    assert giap.name == "Giáp"
    assert giap.value == ThienCan.GIAP
    assert giap.ngu_hanh == NguHanh.MOC
