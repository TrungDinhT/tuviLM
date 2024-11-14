import pydantic

from src.tuvi.cung import Cung
from src.tuvi.birth import BirthTime
from src.tuvi.sao import ChinhTinh
from src.tuvi.transform import get_luc_hai, get_nhi_hop, get_xung_chieu
from src.tuvi.types import LIST_CUC, LIST_DIA_CHI, LIST_ROLES, TYPE_DIA_CHI


class TinhBan(pydantic.BaseModel):

    map_cung : dict[TYPE_DIA_CHI, Cung]

    cuc : str | None = None

    @classmethod
    def from_birthtime(cls, birthTime : BirthTime):
        pass

    @classmethod
    def init_empty_plate(cls):

        return cls(
            map_cung={
                dia_chi : Cung(
                    sign="Am" if idx % 2 == 1 else "Duong"
                ) for idx, dia_chi in enumerate(LIST_DIA_CHI)}
        )

    @property
    def menh_position(self):
        for dia_chi, cung in self.map_cung.items():
            if cung.role == "Menh":
                return dia_chi

        raise ValueError("Non role tinh ban")


def get_menh_position(birthTime : BirthTime) -> int:

    # + 2 vì khởi tại cung Dần
    month_position = (2 + birthTime.month - 1) % 12

    hour_position = LIST_DIA_CHI.index(birthTime.hour)

    position = (month_position - hour_position) % 12

    return position

def build_role(tinhBan : TinhBan, birthTime : BirthTime) -> TinhBan:

    menh_position = get_menh_position(birthTime)

    for idx, role in enumerate(LIST_ROLES):
        tinhBan.map_cung[LIST_DIA_CHI[(menh_position + idx) % 12]].role = role

    return tinhBan

def match_cuc_index_by_menh_position(cuc_index_order : list[int], menh_position : TYPE_DIA_CHI):
    if menh_position in ["Ty", "Suu"]:
        return cuc_index_order[0]
    if menh_position in ["Dan", "Mao", "Tuat", "Hoi"]:
        return cuc_index_order[1]
    if menh_position in ["Thin", "Ti"]:
        return cuc_index_order[2]
    if menh_position in ["Ngo", "Mui"]:
        return cuc_index_order[3]
    if menh_position in ["Than", "Dau"]:
        return cuc_index_order[4]

def set_cuc(tinhBan : TinhBan, birthTime : BirthTime) -> int:

    menh_position = tinhBan.menh_position

    thien_can = birthTime.thien_can

    if thien_can in ["Giap", "Ky"]:
        cuc_index = match_cuc_index_by_menh_position([0,4,1,3,2], menh_position)
    if thien_can in ["At", "Canh"]:
        cuc_index = match_cuc_index_by_menh_position([4,3,2,1,0], menh_position)
    if thien_can in ["Binh", "Tan"]:
        cuc_index = match_cuc_index_by_menh_position([3,1,0,2,4], menh_position)
    if thien_can in ["Dinh", "Nham"]:
        cuc_index = match_cuc_index_by_menh_position([1,2,4,0,3], menh_position)
    if thien_can in ["Mau", "Quy"]:
        cuc_index = match_cuc_index_by_menh_position([2,0,3,4,1], menh_position)
    tinhBan.cuc = LIST_CUC[cuc_index]

    return tinhBan

def get_tuvi_position(tinhBan : TinhBan, birthTime : BirthTime) -> TYPE_DIA_CHI:

    cuc_number = LIST_CUC.index(tinhBan.cuc) + 2

    if (mod := birthTime.date % cuc_number) == 0:
        div = birthTime.date // cuc_number

        borrow_number = 0
    else:
        div = birthTime.date // cuc_number + 1

        borrow_number = cuc_number - mod

    if div % 2 == 0:
        return LIST_DIA_CHI[(2 + div -1 + borrow_number) % 12]

    return LIST_DIA_CHI[(2 + div -1 - borrow_number) % 12]

def build_chinh_tinh(tinhBan : TinhBan, birthTime : BirthTime) -> TinhBan:

    # An tử vi
    tuvi_position = get_tuvi_position(tinhBan, birthTime)
    tuvi_index = LIST_DIA_CHI.index(tuvi_position)

    # An thiên phủ
    thienphu_index = (2 - (tuvi_index - 2)) % 12
    thienphu_position = LIST_DIA_CHI[thienphu_index]

    # An sao thái dương, vũ khúc, liem trinh
    thaiduong_position = get_nhi_hop(thienphu_position)
    vukhuc_position = LIST_DIA_CHI[(tuvi_index - 4) % 12]
    liemtrinh_position = LIST_DIA_CHI[(tuvi_index + 4) % 12]


    # An sao sát phá tham
    thatsat_position = get_xung_chieu(thienphu_position)

    thamlang_index = (LIST_DIA_CHI.index(thatsat_position) - 4) % 12
    phaquan_index = (LIST_DIA_CHI.index(thatsat_position) + 4) % 12

    thamlang_position = LIST_DIA_CHI[thamlang_index]
    phaquan_position = LIST_DIA_CHI[phaquan_index]

    # An Cơ Nguyệt Đồng Lương
    thiendong_position = get_nhi_hop(thamlang_position)
    thienco_position = get_nhi_hop(phaquan_position)
    thaiam_position = get_nhi_hop(vukhuc_position)
    thienluong_position = get_nhi_hop(liemtrinh_position)

    # An Cự môn, Thiên Tướng
    cumon_position = get_luc_hai(tuvi_position)
    thientuong_position = get_xung_chieu(phaquan_position)

    # Sắp xếp sao
    tinhBan.map_cung[tuvi_position].chinhTinh.append(ChinhTinh(name="Tử  vi", elemental="Tho"))
    tinhBan.map_cung[thienphu_position].chinhTinh.append(ChinhTinh(name="Thiên phủ", elemental="Tho"))
    tinhBan.map_cung[thaiduong_position].chinhTinh.append(ChinhTinh(name="Thái Dương", elemental="Hoa"))
    tinhBan.map_cung[vukhuc_position].chinhTinh.append(ChinhTinh(name="Vũ Khúc", elemental="Kim"))
    tinhBan.map_cung[liemtrinh_position].chinhTinh.append(ChinhTinh(name="Liêm Trinh", elemental="Hoa"))
    tinhBan.map_cung[thatsat_position].chinhTinh.append(ChinhTinh(name="Thất sát", elemental="Kim"))
    tinhBan.map_cung[thamlang_position].chinhTinh.append(ChinhTinh(name="Tham Lang", elemental="Thuy"))
    tinhBan.map_cung[phaquan_position].chinhTinh.append(ChinhTinh(name="Phá Quân", elemental="Thuy"))
    tinhBan.map_cung[thiendong_position].chinhTinh.append(ChinhTinh(name="Thiên Đồng", elemental="Thuy"))
    tinhBan.map_cung[thienco_position].chinhTinh.append(ChinhTinh(name="Thiên Cơ", elemental="Moc"))
    tinhBan.map_cung[thaiam_position].chinhTinh.append(ChinhTinh(name="Thai Am", elemental="Thuy"))
    tinhBan.map_cung[thienluong_position].chinhTinh.append(ChinhTinh(name="Thiên Lương", elemental="Moc"))
    tinhBan.map_cung[cumon_position].chinhTinh.append(ChinhTinh(name="Cự Môn", elemental="Thuy"))
    tinhBan.map_cung[thientuong_position].chinhTinh.append(ChinhTinh(name="Thiên Tướng", elemental="Thuy"))

    return tinhBan
