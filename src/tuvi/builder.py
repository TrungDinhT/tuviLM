from typing import Literal
from src.tuvi.element.types import LIST_DIA_CHI, LIST_ROLES, LIST_THIEN_CAN, TYPE_DIA_CHI
from src.tuvi.birth import TuviTime
from src.tuvi.element.star_registry import make_chinh_tinh, make_phu_tinh
from src.tuvi.element.tuhoa_registry import make_tuhoa
from src.tuvi.search_tool import search_element
from src.tuvi.transform import get_luc_hai, get_nhi_hop, get_xung_chieu
from src.tuvi.tinh_ban import TinhBan
from src.tuvi.element.cuc import LIST_CUC
from src.tuvi.constant import (
    MAP_LOC_TON_POSITION,
    MAP_LUU_HA,
    MAP_THIEN_KHOI,
    MAP_THIEN_PHUC,
    MAP_THIEN_QUAN,
    MAP_THIEN_TRU,
    MAP_THIEN_VIET,
    MAP_TRIET,
    MAP_TUAN,
    MAP_TUHOA,
    VONG_LOCTON,
    VONG_THAI_TUE
)

from src.tuvi.element.trangsinh import MAP_TRANGSINH_POSITION, VONG_TRANG_SINH


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

    def _add_chinh_tinh(self, position: TYPE_DIA_CHI, star_name: str):
        self.tinhBan.map_cung[position].chinhTinh.append(make_chinh_tinh(star_name))

    def _add_phu_tinh(self, position: TYPE_DIA_CHI, star_name: str):
        self.tinhBan.map_cung[position].phuTinh.append(make_phu_tinh(star_name))

    def _add_tuhoa(self, position: TYPE_DIA_CHI, tuhoa_name: str):
        self.tinhBan.map_cung[position].tuhoa.append(make_tuhoa(tuhoa_name))

    # TODO : Fix here to not re-create tinh ban
    def build(self, birthTime: TuviTime) -> TinhBan:
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
        self._build_lavong()
        self._build_dauquan(birthTime)
        self._build_trangsinh()
        self._build_tuhoa(birthTime)
        self._build_tuan_triet(birthTime)
        self._build_age_daivan(birthTime)

        return self.tinhBan

    def build_current_year(self, observed_time: int):
        self

    def _get_menh_position(self, birthTime : TuviTime) -> int:

        # + 2 vì khởi tại cung Dần
        month_position = (2 + birthTime.month - 1) % 12

        hour_position = LIST_DIA_CHI.index(birthTime.hour)

        position = (month_position - hour_position) % 12

        return position

    def _match_cuc_index_by_menh_position(self, cuc_index_order : list[int], menh_position : TYPE_DIA_CHI):
        if menh_position in ["Tý", "Sửu"]:
            return cuc_index_order[0]
        if menh_position in ["Dần", "Mão", "Tuất", "Hợi"]:
            return cuc_index_order[1]
        if menh_position in ["Thìn", "Tị"]:
            return cuc_index_order[2]
        if menh_position in ["Ngọ", "Mùi"]:
            return cuc_index_order[3]
        if menh_position in ["Thân", "Dậu"]:
            return cuc_index_order[4]


    def _get_tuvi_position(self, tinhBan : TinhBan, birthTime : TuviTime) -> TYPE_DIA_CHI:

        cuc_number = tinhBan.cuc.number

        if (mod := birthTime.date % cuc_number) == 0:
            div = birthTime.date // cuc_number

            borrow_number = 0
        else:
            div = birthTime.date // cuc_number + 1

            borrow_number = cuc_number - mod

        if borrow_number % 2 == 0:
            return LIST_DIA_CHI[(2 + div -1 + borrow_number) % 12]

        return LIST_DIA_CHI[(2 + div -1 - borrow_number) % 12]

    def _build_general_info(self, birthTime : TuviTime):

        self.tinhBan.gender = birthTime.gender

        self.tinhBan.am_duong = "Duong" if (LIST_THIEN_CAN.index(birthTime.thien_can) % 2 == 0) else "Am"

        self.tinhBan.direction = 1 if (
            self.tinhBan.gender == "M" and self.tinhBan.am_duong == "Duong"
            ) or (self.tinhBan.gender == "F" and self.tinhBan.am_duong == "Am") else -1

    def _build_role(self, birthTime : TuviTime):
        menh_position = self._get_menh_position(birthTime)

        hour_index = LIST_DIA_CHI.index(birthTime.hour)
        diachi_index = LIST_DIA_CHI.index(birthTime.dia_chi)

        self.tinhBan.cung_than = get_position_by_move(menh_position, hour_index *2, 1)

        self.tinhBan.map_cung[self.tinhBan.cung_than].is_cung_than = True

        thientai_position = get_position_by_move(menh_position, diachi_index, 1)
        thientho_position = get_position_by_move(self.tinhBan.cung_than, diachi_index, 1)


        for idx, role in enumerate(LIST_ROLES):
            position = LIST_DIA_CHI[(menh_position + idx) % 12]
            self.tinhBan.map_cung[position].role = role

            if role == "Tật Ách":
                self._add_phu_tinh(position, "Thiên Sứ")
            if role == "Nô Bộc":
                self._add_phu_tinh(position, "Thiên Thuơng")

        self._add_phu_tinh(thientho_position, "Thiên Thọ")
        self._add_phu_tinh(thientai_position, "Thiên Tài")


    def _build_cuc(self, birthTime : TuviTime):

        menh_position = self.tinhBan.menh_position

        thien_can = birthTime.thien_can

        if thien_can in ["Giấp", "Kỷ"]:
            cuc_index = self._match_cuc_index_by_menh_position([0,4,1,3,2], menh_position)
        if thien_can in ["Ất", "Canh"]:
            cuc_index = self._match_cuc_index_by_menh_position([4,3,2,1,0], menh_position)
        if thien_can in ["Bính", "Tân"]:
            cuc_index = self._match_cuc_index_by_menh_position([3,1,0,2,4], menh_position)
        if thien_can in ["Đinh", "Nhâm"]:
            cuc_index = self._match_cuc_index_by_menh_position([1,2,4,0,3], menh_position)
        if thien_can in ["Mậu", "Quý"]:
            cuc_index = self._match_cuc_index_by_menh_position([2,0,3,4,1], menh_position)
        self.tinhBan.cuc = LIST_CUC[cuc_index]

    def _build_age_daivan(self, birthTime : TuviTime):

        menh_position = LIST_DIA_CHI.index(self.tinhBan.menh_position)
        cuc = self.tinhBan.cuc

        for i in range(12):
            position = LIST_DIA_CHI[(menh_position + i*self.tinhBan.direction) % 12]

            self.tinhBan.map_cung[position].age_daivan = i * 10 + cuc.number


    def _build_chinh_tinh(self, birthTime : TuviTime):

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
        self._add_chinh_tinh(tuvi_position, "Tử Vi")
        self._add_chinh_tinh(thienphu_position, "Thiên Phủ")
        self._add_chinh_tinh(thaiduong_position, "Thái Dương")
        self._add_chinh_tinh(vukhuc_position, "Vũ Khúc")
        self._add_chinh_tinh(liemtrinh_position, "Liêm Trinh")
        self._add_chinh_tinh(thatsat_position, "Thất Sát")
        self._add_chinh_tinh(thamlang_position, "Tham Lang")
        self._add_chinh_tinh(phaquan_position, "Phá Quân")
        self._add_chinh_tinh(thiendong_position, "Thiên Đồng")
        self._add_chinh_tinh(thienco_position, "Thiên Cơ")
        self._add_chinh_tinh(thaiam_position, "Thái Âm")
        self._add_chinh_tinh(thienluong_position, "Thiên Lương")
        self._add_chinh_tinh(cumon_position, "Cự Môn")
        self._add_chinh_tinh(thientuong_position, "Thiên Tướng")


    def _build_by_month(self, birthTime : TuviTime):

        taphu_position = get_position_by_move("Thìn", birthTime.month -1, 1)
        huubat_position = get_position_by_move("Tuất", birthTime.month -1, -1)

        tamthai_position = get_position_by_move(taphu_position, birthTime.date -1, 1)
        battoa_position = get_position_by_move(huubat_position, birthTime.date -1, -1)

        thiengiai_position = get_position_by_move("Thân", birthTime.month -1, 1)
        diagiai_position = get_position_by_move("Mùi", birthTime.month -1, 1)

        thienhinh_position = get_position_by_move("Dậu", birthTime.month -1, 1)
        thiendieu_position = get_position_by_move("Sửu", birthTime.month -1, 1)

        self._add_phu_tinh(taphu_position, "Tả Phù")
        self._add_phu_tinh(huubat_position, "Hữu Bật")
        self._add_phu_tinh(thiengiai_position, "Thiên Giải")
        self._add_phu_tinh(diagiai_position, "Địa Giải")
        self._add_phu_tinh(thienhinh_position, "Thiên Hình")
        self._add_phu_tinh(tamthai_position, "Tam Thai")
        self._add_phu_tinh(battoa_position, "Bát Toạ")
        self._add_phu_tinh(thiendieu_position, "Thiên Diêu")
        self._add_phu_tinh(thiendieu_position, "Thiên Y")

    def _build_by_hour(self, birthTime : TuviTime):

        birthHourIndex = LIST_DIA_CHI.index(birthTime.hour)

        # khởi từ cung hợi
        diakhong_position = get_position_by_move(11, birthHourIndex, -1)
        diaket_position = get_position_by_move(11, birthHourIndex, 1)

        # Khởi từ thìn tuất
        vanxuong_position = get_position_by_move(10, birthHourIndex, -1)
        vankhuc_position = get_position_by_move(4, birthHourIndex, 1)

        anquang_position = get_position_by_move(vanxuong_position, birthTime.date -1 -1, 1)
        thienquy_position = get_position_by_move(vankhuc_position, birthTime.date -1 -1, -1)

        thaiphu_position = get_position_by_move("Ngọ", birthHourIndex , 1)
        phongcao_position = get_position_by_move("Dần", birthHourIndex, 1)

        self._add_phu_tinh(diakhong_position, "Địa Không")
        self._add_phu_tinh(diaket_position, "Địa Kiếp")
        self._add_phu_tinh(vanxuong_position, "Văn Xương")
        self._add_phu_tinh(vankhuc_position, "Văn Khúc")
        self._add_phu_tinh(anquang_position, "Ân Quang")
        self._add_phu_tinh(thienquy_position, "Thiên Quý")

        self._add_phu_tinh(thaiphu_position, "Thai Phụ")
        self._add_phu_tinh(phongcao_position, "Phong Cáo")

    def _build_khoiviet(self, birthTime : TuviTime):

        self._add_phu_tinh(MAP_THIEN_KHOI[birthTime.thien_can], "Thiên Khôi")
        self._add_phu_tinh(MAP_THIEN_VIET[birthTime.thien_can], "Thiên Việt")

    def _build_loc_ton(self, birthTime : TuviTime):

        locton_position = MAP_LOC_TON_POSITION[birthTime.thien_can]
        locton_index = LIST_DIA_CHI.index(locton_position)

        for i in range(12):
            position = LIST_DIA_CHI[(locton_index + i) % 12]
            for star_name in VONG_LOCTON[i]:
                self._add_phu_tinh(position, star_name)

        if self.tinhBan.direction == 1:
            lucsi_position = LIST_DIA_CHI[(locton_index + 1) % 12]
        else:
            lucsi_position = LIST_DIA_CHI[(locton_index - 1) % 12]

        self._add_phu_tinh(lucsi_position, "Lực Sĩ")


    def _build_thai_tue(self, birthTime : TuviTime):

        thaitue_index = LIST_DIA_CHI.index(birthTime.dia_chi)

        # An đẩu quân


        for i in range(12):
            position = LIST_DIA_CHI[(thaitue_index + i) % 12]
            for star_name in VONG_THAI_TUE[i]:
                self._add_phu_tinh(position, star_name)

    def _build_linhhoa(self, birthTime : TuviTime):
        index_diachi = LIST_DIA_CHI.index(birthTime.dia_chi)
        hour_index = LIST_DIA_CHI.index(birthTime.hour)

        # source : http://tuvi.cohoc.net/sao-linh-tinh-hoa-tinh-y-nghia-tai-menh-va-cung-khac-nid-6978.html
        match index_diachi % 4:
            case 0:
                hoatinh_cung_khoi = "Dần"
                linhtinh_cung_khoi = "Tuất"
            case 1:
                hoatinh_cung_khoi = "Mão"
                linhtinh_cung_khoi = "Tuất"
            case 2:
                hoatinh_cung_khoi = "Sửu"
                linhtinh_cung_khoi = "Mão"
            case 3:
                hoatinh_cung_khoi = "Dậu"
                linhtinh_cung_khoi = "Tuất"

        hoatinh_position = get_position_by_move(hoatinh_cung_khoi, hour_index , self.tinhBan.direction)
        linhinh_position = get_position_by_move(linhtinh_cung_khoi, hour_index ,  (-1) * self.tinhBan.direction)

        self._add_phu_tinh(hoatinh_position, "Hỏa Tinh")
        self._add_phu_tinh(linhinh_position, "Linh Tinh")

    def _build_by_map(self, birthTime : TuviTime):

        luuha_position = MAP_LUU_HA[birthTime.thien_can]
        thientru_position = MAP_THIEN_TRU[birthTime.thien_can]
        thienquan_position = MAP_THIEN_QUAN[birthTime.thien_can]
        thienphuc_position = MAP_THIEN_PHUC[birthTime.thien_can]

        self._add_phu_tinh(luuha_position, "Lưu Hà")
        self._add_phu_tinh(thientru_position, "Thiên Trù")
        self._add_phu_tinh(thienquan_position, "Thiên Quan")
        self._add_phu_tinh(thienphuc_position, "Thiên Phúc")

    def _build_cothan_quatu(self, birthTime : TuviTime):

        if birthTime.dia_chi in ["Dần", "Mão", "Thìn"]:
            cothan_position = "Tị"
            quatu_position = "Sửu"
        if birthTime.dia_chi in ["Tị", "Ngọ", "Mùi"]:
            cothan_position = "Thân"
            quatu_position = "Thìn"
        if birthTime.dia_chi in ["Thân", "Dậu", "Tuất"]:
            cothan_position = "Hợi"
            quatu_position = "Dần"
        if birthTime.dia_chi in ["Hợi", "Tý", "Sửu"]:
            cothan_position = "Mùi"
            quatu_position = "Tuất"

        self._add_phu_tinh(cothan_position, "Cô Thần")
        self._add_phu_tinh(quatu_position, "Quả Tú")

    def _build_dauquan(self, birthTime : TuviTime):

        month_position = get_position_by_move(birthTime.dia_chi, birthTime.month -1, -1)

        dauquan_position = get_position_by_move(month_position, LIST_DIA_CHI.index(birthTime.hour), 1)
        self._add_phu_tinh(dauquan_position, "Đẩu Quân")


    def _build_by_diachi(self, birthTime : TuviTime):

        diachi_index = LIST_DIA_CHI.index(birthTime.dia_chi)

        thienhi_position = get_position_by_move("Dậu", diachi_index, -1)
        hongloan_position = get_xung_chieu(thienhi_position)

        giaithan_position = get_position_by_move("Tuất", diachi_index, -1)

        thienkhoc_position = get_position_by_move("Ngọ", diachi_index, -1)

        match diachi_index % 4:
            case 0: # Thân Tý Thìn
                thienma_position = "Dần"
                hoacai_position = "Thìn"
                daohoa_position = "Dậu"
                kiepsat_position = "Tị"
            case 1: # Tị Dậu Sửu
                thienma_position = "Hợi"
                hoacai_position = "Sửu"
                daohoa_position = "Ngọ"
                kiepsat_position = "Dần"
            case 2: # Dần Ngọ Tuất
                thienma_position = "Thân"
                hoacai_position = "Tuất"
                daohoa_position = "Mão"
                kiepsat_position = "Hợi"
            case 3: # Hợi Mão Mùi
                thienma_position = "Tị"
                hoacai_position = "Mùi"
                daohoa_position = "Tý"
                kiepsat_position = "Thân"

        match diachi_index % 3:
            case 0:
                phatoai_position = "Tị"
            case 1:
                phatoai_position = "Sửu"
            case 2:
                phatoai_position = "Dậu"

        self._add_phu_tinh(thienhi_position, "Thiên Hỉ")
        self._add_phu_tinh(hongloan_position, "Hồng Loan")
        self._add_phu_tinh(thienma_position, "Thiên Mã")
        self._add_phu_tinh(giaithan_position, "Giải Thần")
        self._add_phu_tinh(giaithan_position, "Phượng Các")
        self._add_phu_tinh(phatoai_position, "Phá Toái")
        self._add_phu_tinh(hoacai_position, "Hỏa Cái")
        self._add_phu_tinh(daohoa_position, "Đào Hoa")
        self._add_phu_tinh(thienkhoc_position, "Thiên Khốc")
        self._add_phu_tinh(kiepsat_position, "Kiếp Sát")

    def _build_lavong(self):
        self._add_phu_tinh("Thìn", "Thiên La")
        self._add_phu_tinh("Tuất", "Địa Võng")

    def _build_trangsinh(self):

        trangsinh_position = MAP_TRANGSINH_POSITION[self.tinhBan.cuc.elemental]
        trangsinh_index = LIST_DIA_CHI.index(trangsinh_position)

        for idx, dat_trang_sinh in enumerate(VONG_TRANG_SINH):
            position_index = (trangsinh_index + idx) % 12
            self.tinhBan.map_cung[LIST_DIA_CHI[position_index]].trang_sinh = dat_trang_sinh


    def _build_tuhoa(self, birthTime : TuviTime):
        sao_hoa_khi = MAP_TUHOA[birthTime.thien_can]

        hoaloc_position = search_element(self.tinhBan, sao_hoa_khi[0])
        hoaquyen_position = search_element(self.tinhBan, sao_hoa_khi[1])
        hoakhoa_position = search_element(self.tinhBan, sao_hoa_khi[2])
        hoaky_position = search_element(self.tinhBan, sao_hoa_khi[3])

        self._add_tuhoa(hoaloc_position, "Hóa Lộc")
        self._add_tuhoa(hoaquyen_position, "Hóa Quyền")
        self._add_tuhoa(hoakhoa_position, "Hóa Khoa")
        self._add_tuhoa(hoaky_position, "Hóa Kỵ")


    def _build_tuan_triet(self, birthTime : TuviTime):

        triet_positions = MAP_TRIET[birthTime.thien_can]

        dia_chi_index = LIST_DIA_CHI.index(birthTime.dia_chi)
        thien_can_index = LIST_THIEN_CAN.index(birthTime.thien_can)

        tuan_positions = MAP_TUAN[LIST_DIA_CHI[(dia_chi_index - thien_can_index) % 12]]

        self.tinhBan.map_cung[triet_positions[0]].is_triet = True
        self.tinhBan.map_cung[triet_positions[1]].is_triet = True
        self.tinhBan.map_cung[tuan_positions[0]].is_tuan = True
        self.tinhBan.map_cung[tuan_positions[1]].is_tuan = True
