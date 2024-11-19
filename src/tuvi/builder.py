from typing import Literal
from src.tuvi.types import LIST_DIA_CHI, LIST_ROLES, LIST_THIEN_CAN, TYPE_DIA_CHI
from src.tuvi.birth import BirthTime
from src.tuvi.sao import ChinhTinh, PhuTinh
from src.tuvi.transform import get_luc_hai, get_nhi_hop, get_xung_chieu
from src.tuvi.tinh_ban import TinhBan
from src.tuvi.cuc import LIST_CUC
from src.tuvi.constant import MAP_LOC_TON_POSITION, MAP_LUU_HA, MAP_THIEN_KHOI, MAP_THIEN_TRU, MAP_THIEN_VIET, VONG_LOCTON, VONG_THAI_TUE


def get_position_by_move(
    begin_position : TYPE_DIA_CHI | int,
    offset : int,
    direction : Literal[1, -1]
) -> TYPE_DIA_CHI:
    if isinstance(begin_position, str):
        begin_position = LIST_DIA_CHI.index(begin_position)

    return LIST_DIA_CHI[(begin_position + direction * offset) % 12]


class Builder:

    def __init__(self) -> None:
        self.tinhBan = TinhBan.init_empty_plate()

    # TODO : Fix here to not re-create tinh ban
    def build(self, birthTime: BirthTime) -> TinhBan:
        self._build_general_info(birthTime)
        self._build_role(birthTime)
        self._build_cuc(birthTime)
        self._build_chinh_tinh(birthTime)
        self._build_by_month(birthTime)
        self._build_by_hour(birthTime)
        self._build_loc_ton(birthTime)
        self._build_thai_tue(birthTime)
        self._build_khoiviet(birthTime)
        self._build_linhhoa(birthTime)
        self._build_by_map(birthTime)
        self._build_cothan_quatu(birthTime)
        self._build_by_diachi(birthTime)
        self._build_lavong(birthTime)

        return self.tinhBan

    def _get_menh_position(self, birthTime : BirthTime) -> int:

        # + 2 vì khởi tại cung Dần
        month_position = (2 + birthTime.month - 1) % 12

        hour_position = LIST_DIA_CHI.index(birthTime.hour)

        position = (month_position - hour_position) % 12

        return position

    def _match_cuc_index_by_menh_position(self, cuc_index_order : list[int], menh_position : TYPE_DIA_CHI):
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


    def _get_tuvi_position(self, tinhBan : TinhBan, birthTime : BirthTime) -> TYPE_DIA_CHI:

        cuc_number = tinhBan.cuc.number

        if (mod := birthTime.date % cuc_number) == 0:
            div = birthTime.date // cuc_number

            borrow_number = 0
        else:
            div = birthTime.date // cuc_number + 1

            borrow_number = cuc_number - mod

        if div % 2 == 0:
            return LIST_DIA_CHI[(2 + div -1 + borrow_number) % 12]

        return LIST_DIA_CHI[(2 + div -1 - borrow_number) % 12]

    def _build_general_info(self, birthTime : BirthTime):

        self.tinhBan.gender = birthTime.gender

        self.tinhBan.am_duong = "Duong" if (LIST_THIEN_CAN.index(birthTime.thien_can) % 2 == 0) else "Am"

        self.tinhBan.direction = 1 if (
            self.tinhBan.gender == "M" and self.tinhBan.am_duong == "Duong"
            ) or (self.tinhBan.gender == "F" and self.tinhBan.am_duong == "Am") else -1

    def _build_role(self, birthTime : BirthTime):
        menh_position = self._get_menh_position(birthTime)

        for idx, role in enumerate(LIST_ROLES):
            position = LIST_DIA_CHI[(menh_position + idx) % 12]
            self.tinhBan.map_cung[position].role = role

            if role == "Tat Ach":
                self.tinhBan.map_cung[position].phuTinh.append(PhuTinh(name="Thiên Sứ", elemental="Thuy"))
            if role == "No Boc":
                self.tinhBan.map_cung[position].phuTinh.append(PhuTinh(name="Thien Thuong", elemental="Tho"))

    def _build_cuc(self, birthTime : BirthTime):

        menh_position = self.tinhBan.menh_position

        thien_can = birthTime.thien_can

        if thien_can in ["Giap", "Ky"]:
            cuc_index = self._match_cuc_index_by_menh_position([0,4,1,3,2], menh_position)
        if thien_can in ["At", "Canh"]:
            cuc_index = self._match_cuc_index_by_menh_position([4,3,2,1,0], menh_position)
        if thien_can in ["Binh", "Tan"]:
            cuc_index = self._match_cuc_index_by_menh_position([3,1,0,2,4], menh_position)
        if thien_can in ["Dinh", "Nham"]:
            cuc_index = self._match_cuc_index_by_menh_position([1,2,4,0,3], menh_position)
        if thien_can in ["Mau", "Quy"]:
            cuc_index = self._match_cuc_index_by_menh_position([2,0,3,4,1], menh_position)
        self.tinhBan.cuc = LIST_CUC[cuc_index]


    def _build_chinh_tinh(self, birthTime : BirthTime):

        # An tử vi
        tuvi_position = self._get_tuvi_position(self.tinhBan, birthTime)
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
        self.tinhBan.map_cung[tuvi_position].chinhTinh.append(ChinhTinh(name="Tử  vi", elemental="Tho"))
        self.tinhBan.map_cung[thienphu_position].chinhTinh.append(ChinhTinh(name="Thiên phủ", elemental="Tho"))
        self.tinhBan.map_cung[thaiduong_position].chinhTinh.append(ChinhTinh(name="Thái Dương", elemental="Hoa"))
        self.tinhBan.map_cung[vukhuc_position].chinhTinh.append(ChinhTinh(name="Vũ Khúc", elemental="Kim"))
        self.tinhBan.map_cung[liemtrinh_position].chinhTinh.append(ChinhTinh(name="Liêm Trinh", elemental="Hoa"))
        self.tinhBan.map_cung[thatsat_position].chinhTinh.append(ChinhTinh(name="Thất sát", elemental="Kim"))
        self.tinhBan.map_cung[thamlang_position].chinhTinh.append(ChinhTinh(name="Tham Lang", elemental="Thuy"))
        self.tinhBan.map_cung[phaquan_position].chinhTinh.append(ChinhTinh(name="Phá Quân", elemental="Thuy"))
        self.tinhBan.map_cung[thiendong_position].chinhTinh.append(ChinhTinh(name="Thiên Đồng", elemental="Thuy"))
        self.tinhBan.map_cung[thienco_position].chinhTinh.append(ChinhTinh(name="Thiên Cơ", elemental="Moc"))
        self.tinhBan.map_cung[thaiam_position].chinhTinh.append(ChinhTinh(name="Thai Am", elemental="Thuy"))
        self.tinhBan.map_cung[thienluong_position].chinhTinh.append(ChinhTinh(name="Thiên Lương", elemental="Moc"))
        self.tinhBan.map_cung[cumon_position].chinhTinh.append(ChinhTinh(name="Cự Môn", elemental="Thuy"))
        self.tinhBan.map_cung[thientuong_position].chinhTinh.append(ChinhTinh(name="Thiên Tướng", elemental="Thuy"))


    def _build_by_month(self, birthTime : BirthTime):

        taphu_position = get_position_by_move(4, birthTime.month -1, 1)
        huubat_position = get_position_by_move(10, birthTime.month -1, -1)

        thiengiai_position = get_position_by_move("Than", birthTime.month -1, 1)
        diagiai_position = get_position_by_move("Mui", birthTime.month -1, 1)

        self.tinhBan.map_cung[taphu_position].phuTinh.append(PhuTinh(name="Tả Phù", elemental="Tho"))
        self.tinhBan.map_cung[huubat_position].phuTinh.append(PhuTinh(name="Hữu Bật", elemental="Thuy"))
        self.tinhBan.map_cung[thiengiai_position].phuTinh.append(PhuTinh(name="Thiên Giải", elemental="Hoa"))
        self.tinhBan.map_cung[diagiai_position].phuTinh.append(PhuTinh(name="Địa Giải", elemental="Tho"))

    def _build_by_hour(self, birthTime : BirthTime):

        birthHourIndex = LIST_DIA_CHI.index(birthTime.hour)

        # khởi từ cung hợi
        diakhong_position = get_position_by_move(11, birthHourIndex, -1)
        diaket_position = get_position_by_move(11, birthHourIndex, 1)

        # Khởi từ thìn tuất
        vanxuong_position = get_position_by_move(10, birthHourIndex, -1)
        vankhuc_position = get_position_by_move(4, birthHourIndex, 1)

        anquang_position = get_position_by_move(vanxuong_position, birthTime.date -1 -1, 1)
        thienquy_position = get_position_by_move(vankhuc_position, birthTime.date -1 -1, -1)



        thaiphu_position = get_position_by_move("Ngo", birthHourIndex , 1)
        phongcao_position = get_position_by_move("Dan", birthHourIndex, 1)

        self.tinhBan.map_cung[diakhong_position].phuTinh.append(PhuTinh(name="Địa Không", elemental="Hoa"))
        self.tinhBan.map_cung[diaket_position].phuTinh.append(PhuTinh(name="Địa Kiếp", elemental="Hoa"))
        self.tinhBan.map_cung[vanxuong_position].phuTinh.append(PhuTinh(name="Văn Xương", elemental="Kim"))
        self.tinhBan.map_cung[vankhuc_position].phuTinh.append(PhuTinh(name="Văn Khúc", elemental="Thuy"))
        self.tinhBan.map_cung[anquang_position].phuTinh.append(PhuTinh(name="Ân Quang", elemental="Moc"))
        self.tinhBan.map_cung[thienquy_position].phuTinh.append(PhuTinh(name="Thiên Quý", elemental="Tho"))

        self.tinhBan.map_cung[thaiphu_position].phuTinh.append(PhuTinh(name="Thai Phụ", elemental="Kim"))
        self.tinhBan.map_cung[phongcao_position].phuTinh.append(PhuTinh(name="Phong Cáo", elemental="Tho"))

    def _build_khoiviet(self, birthTime : BirthTime):

        self.tinhBan.map_cung[MAP_THIEN_KHOI[birthTime.thien_can]].phuTinh.append(PhuTinh(name="Thiên Khôi", elemental="Hoa"))
        self.tinhBan.map_cung[MAP_THIEN_VIET[birthTime.thien_can]].phuTinh.append(PhuTinh(name="Thiên Việt", elemental="Hoa"))

    def _build_loc_ton(self, birthTime : BirthTime):

        locton_position = MAP_LOC_TON_POSITION[birthTime.thien_can]
        locton_index = LIST_DIA_CHI.index(locton_position)

        for i in range(12):
            self.tinhBan.map_cung[
                LIST_DIA_CHI[(locton_index + i) % 12]
            ].phuTinh.extend(VONG_LOCTON[i])

        if self.tinhBan.direction == 1:
            lucsi_position = LIST_DIA_CHI[(locton_index + 1) % 12]
        else:
            lucsi_position = LIST_DIA_CHI[(locton_index - 1) % 12]

        self.tinhBan.map_cung[lucsi_position].phuTinh.append(PhuTinh(name="Lực Sĩ", elemental="Thuy"))


    def _build_thai_tue(self, birthTime : BirthTime):

        thaitue_index = LIST_DIA_CHI.index(birthTime.dia_chi)

        for i in range(12):
            self.tinhBan.map_cung[
                LIST_DIA_CHI[(thaitue_index + i) % 12]
            ].phuTinh.extend(VONG_THAI_TUE[i])

    def _build_linhhoa(self, birthTime : BirthTime):
        index_diachi = LIST_DIA_CHI.index(birthTime.dia_chi)
        hour_index = LIST_DIA_CHI.index(birthTime.hour)

        # source : http://tuvi.cohoc.net/sao-linh-tinh-hoa-tinh-y-nghia-tai-menh-va-cung-khac-nid-6978.html
        match index_diachi % 4:
            case 0:
                hoatinh_cung_khoi = "Dan"
                linhtinh_cung_khoi = "Tuat"
            case 1:
                hoatinh_cung_khoi = "Mao"
                linhtinh_cung_khoi = "Tuat"
            case 2:
                hoatinh_cung_khoi = "Suu"
                linhtinh_cung_khoi = "Mao"
            case 3:
                hoatinh_cung_khoi = "Dau"
                linhtinh_cung_khoi = "Tuat"

        hoatinh_position = get_position_by_move(hoatinh_cung_khoi, hour_index , self.tinhBan.direction)
        linhinh_position = get_position_by_move(linhtinh_cung_khoi, hour_index ,  (-1) * self.tinhBan.direction)

        self.tinhBan.map_cung[hoatinh_position].phuTinh.append(PhuTinh(name="Hỏa Tinh", elemental="Hoa"))
        self.tinhBan.map_cung[linhinh_position].phuTinh.append(PhuTinh(name="Linh Tinh", elemental="Hoa"))


    def _build_by_map(self, birthTime : BirthTime):

        luuha_position = MAP_LUU_HA[birthTime.thien_can]
        thientru_position = MAP_THIEN_TRU[birthTime.thien_can]

        self.tinhBan.map_cung[luuha_position].phuTinh.append(PhuTinh(name="Lưu Hà", elemental="Thuy"))
        self.tinhBan.map_cung[thientru_position].phuTinh.append(PhuTinh(name="Thiên Trù", elemental="Tho"))

    def _build_cothan_quatu(self, birthTime : BirthTime):

        if birthTime.dia_chi in ["Dan", "Mao", "Thin"]:
            cothan_position = "Ti"
            quatu_position = "Suu"
        if birthTime.dia_chi in ["Ti", "Ngo", "Mui"]:
            cothan_position = "Than"
            quatu_position = "Thin"
        if birthTime.dia_chi in ["Than", "Dau", "Tuat"]:
            cothan_position = "Hoi"
            quatu_position = "Dan"
        if birthTime.dia_chi in ["Hoi", "Ty", "Suu"]:
            cothan_position = "Mui"
            quatu_position = "Tuat"

        self.tinhBan.map_cung[cothan_position].phuTinh.append(PhuTinh(name="Cô Thần", elemental="Tho"))
        self.tinhBan.map_cung[quatu_position].phuTinh.append(PhuTinh(name="Quả Tú", elemental="Tho"))


    def _build_by_diachi(self, birthTime : BirthTime):

        diachi_index = LIST_DIA_CHI.index(birthTime.dia_chi)

        thienhi_position = get_position_by_move("Dau", diachi_index, -1)
        hongloan_position = get_xung_chieu(thienhi_position)

        nguyetduc_position = get_position_by_move("Ti", diachi_index, 1)

        giaithan_position = get_position_by_move("Tuat", diachi_index, -1)

        match diachi_index % 4:
            case 0:
                thienma_position = "Dan"
            case 1:
                thienma_position = "Hoi"
            case 2:
                thienma_position = "Than"
            case 3:
                thienma_position = "Ti"

        match diachi_index % 3:
            case 0:
                phatoai_position = "Ti"
            case 1:
                phatoai_position = "Suu"
            case 2:
                phatoai_position = "Dau"

        self.tinhBan.map_cung[thienhi_position].phuTinh.append(PhuTinh(name="Thiên Hỉ", elemental="Hoa"))
        self.tinhBan.map_cung[hongloan_position].phuTinh.append(PhuTinh(name="Hồng Loan", elemental="Thuy"))
        self.tinhBan.map_cung[nguyetduc_position].phuTinh.append(PhuTinh(name="Nguyệt Đức", elemental="Hoa"))
        self.tinhBan.map_cung[thienma_position].phuTinh.append(PhuTinh(name="Thiên Mã", elemental="Hoa"))
        self.tinhBan.map_cung[giaithan_position].phuTinh.append(PhuTinh(name="Giải Thần", elemental="Moc"))
        self.tinhBan.map_cung[giaithan_position].phuTinh.append(PhuTinh(name="Phượng Các", elemental="Tho"))
        self.tinhBan.map_cung[phatoai_position].phuTinh.append(PhuTinh(name="Phá Toái", elemental="Hoa"))

    def _build_lavong(self, birthTime: BirthTime):
        self.tinhBan.map_cung["Thin"].phuTinh.append(PhuTinh(name="Thiên La", elemental="Kim"))
        self.tinhBan.map_cung["Tuat"].phuTinh.append(PhuTinh(name="Địa Võng", elemental="Kim"))
