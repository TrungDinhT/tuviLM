from src.refactored.components.repository import get_default_repository
from src.refactored.components.definitions.ban_menh import BanMenh
from src.refactored.components.definitions.cung_role import CungRole, Role
from src.refactored.model.elementary import DiaChi, NguHanh, ThienCan
from src.refactored.components.definitions.sao import ChinhPhuTinh, TuanTriet, TuHoa


def test_default_catalog_loads_cung_and_sao_components():
    catalog = get_default_repository()

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
    catalog = get_default_repository()

    components = catalog.get_many(["thien_tho", "menh"])

    assert [component.name for component in components] == ["Thiên Thọ", "Mệnh"]


def test_default_catalog_loads_structural_entities():
    catalog = get_default_repository()

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


def test_default_catalog_loads_tuan_triet_entries():
    catalog = get_default_repository()

    tuan = catalog.get("tuan_1")

    assert isinstance(tuan, TuanTriet)
    assert tuan.name == "Tuần"
    assert catalog.get("triet_1").name == "Triệt"


def test_default_catalog_loads_ban_menh_entries():
    catalog = get_default_repository()

    bach_lap_kim = catalog.get("bach_lap_kim")

    assert isinstance(bach_lap_kim, BanMenh)
    assert bach_lap_kim.id == "bach_lap_kim"
    assert bach_lap_kim.name == "Bạch Lạp Kim"
    assert bach_lap_kim.ngu_hanh == NguHanh.KIM
    assert bach_lap_kim.description == "Vàng trong nến trắng: Tinh khiết, thanh cao, nhưng dễ tan chảy trước nghịch cảnh"

    sa_trung_kim = catalog.get("sa_trung_kim")
    assert isinstance(sa_trung_kim, BanMenh)
    assert sa_trung_kim.ngu_hanh == NguHanh.KIM

    tung_bach_moc = catalog.get("tung_bach_moc")
    assert isinstance(tung_bach_moc, BanMenh)
    assert tung_bach_moc.ngu_hanh == NguHanh.MOC

    truong_luu_thuy = catalog.get("truong_luu_thuy")
    assert isinstance(truong_luu_thuy, BanMenh)
    assert truong_luu_thuy.ngu_hanh == NguHanh.THUY

    son_ha_hoa = catalog.get("son_ha_hoa")
    assert isinstance(son_ha_hoa, BanMenh)
    assert son_ha_hoa.ngu_hanh == NguHanh.HOA

    bich_thuong_tho = catalog.get("bich_thuong_tho")
    assert isinstance(bich_thuong_tho, BanMenh)
    assert bich_thuong_tho.ngu_hanh == NguHanh.THO
