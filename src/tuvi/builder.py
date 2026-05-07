from typing import Literal

from src.tuvi.element.types import LIST_DIA_CHI, LIST_ROLES, LIST_THIEN_CAN, TYPE_DIA_CHI
from src.tuvi.birth import TuviTime
from src.tuvi.element.star_registry import make_chinh_tinh, make_phu_tinh
from src.tuvi.element.tuhoa_registry import make_tuhoa
from src.tuvi.star_rules import (
    get_chinh_tinh_positions,
    get_hour_star_positions,
    get_month_star_positions,
    get_star_by_dia_chi_position,
    get_star_by_thien_can_position
)
from src.tuvi.search_tool import search_element
from src.tuvi.star_rules.dia_chi_star import get_hong_loan_position, get_thien_khoc_position, get_thien_ma_position
from src.tuvi.star_rules.hour_star import get_van_khuc_position, get_van_xuong_position
from src.tuvi.star_rules.linh_hoa import get_hoatinh_position, get_linhtinh_position
from src.tuvi.star_rules.thai_tue import get_thien_hu_position, get_vong_thai_tue_positions
from src.tuvi.star_rules.thien_can_star import get_loc_ton_position, get_thien_khoi_position, get_thien_viet_position
from src.tuvi.tinh_ban import TinhBan
from src.tuvi.element.cuc import LIST_CUC
from src.tuvi.constant import (
    MAP_TRIET,
    MAP_TUAN,
    MAP_TUHOA
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

    def __init__(self, tinh_ban: TinhBan | None = None) -> None:
        self.tinhBan = tinh_ban or TinhBan.init_empty_plate()

    def _add_chinh_tinh(self, position: TYPE_DIA_CHI, star_name: str):
        self.tinhBan.map_cung[position].chinhTinh.append(make_chinh_tinh(star_name))

    def _add_phu_tinh(self, position: TYPE_DIA_CHI, star_name: str):
        self.tinhBan.map_cung[position].phuTinh.append(make_phu_tinh(star_name))

    def _add_sao_luu(self, position: TYPE_DIA_CHI, star_name: str):
        self.tinhBan.map_cung[position].saoLuu.append(make_phu_tinh(star_name))

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
        self._build_by_thien_can(birthTime)
        self._build_thai_tue(birthTime)
        self._build_linhhoa(birthTime)
        self._build_by_diachi(birthTime)
        self._build_lavong()
        self._build_dauquan(birthTime)
        self._build_trangsinh()
        self._build_tuhoa(birthTime)
        self._build_tuan_triet(birthTime)
        self._build_age_daivan(birthTime)

        return self.tinhBan

    def build_current_year(self, observed_time: TuviTime):
        for cung in self.tinhBan.map_cung.values():
            cung.saoLuu.clear()

        vanxuong_position = get_van_xuong_position(observed_time.hour)
        vankhuc_position = get_van_khuc_position(observed_time.hour)

        thienkhoi_position = get_thien_khoi_position(observed_time.thien_can)
        thienviet_position = get_thien_viet_position(observed_time.thien_can)

        hongloan_position = get_hong_loan_position(observed_time.dia_chi)
        thienma_position = get_thien_ma_position(observed_time.dia_chi)

        thienkhoc_position = get_thien_khoc_position(observed_time.dia_chi)
        locton_position = get_loc_ton_position(observed_time.thien_can)

        thienhu_position = get_thien_hu_position(observed_time.dia_chi)

        map_sao_position = {
            "Văn Xương": vanxuong_position,
            "Văn Khúc": vankhuc_position,
            "Thiên Khôi": thienkhoi_position,
            "Thiên Việt": thienviet_position,
            "Hồng Loan": hongloan_position,
            "Thiên Mã": thienma_position,
            "Thiên Khốc": thienkhoc_position,
            "Lộc Tồn": locton_position,
            "Thiên Hư": thienhu_position
        }

        for star_name, position in map_sao_position.items():
            self._add_sao_luu(position, star_name)

        return self.tinhBan


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

        self.tinhBan.year_can = birthTime.thien_can
        self.tinhBan.year_chi = birthTime.dia_chi

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
        tuvi_position = self._get_tuvi_position(self.tinhBan, birthTime)
        for star_name, position in get_chinh_tinh_positions(tuvi_position):
            self._add_chinh_tinh(position, star_name)


    def _build_by_month(self, birthTime : TuviTime):
        for star_name, position in get_month_star_positions(birthTime.month, birthTime.date):
            self._add_phu_tinh(position, star_name)

    def _build_by_hour(self, birthTime : TuviTime):
        for star_name, position in get_hour_star_positions(birthTime.hour, birthTime.date):
            self._add_phu_tinh(position, star_name)

    def _build_by_thien_can(self, birthTime : TuviTime):

        for star_name, position in get_star_by_thien_can_position(birthTime.thien_can, self.tinhBan.direction):
            self._add_phu_tinh(position, star_name)

    def _build_thai_tue(self, birthTime : TuviTime):

        for star_name, position in get_vong_thai_tue_positions(birthTime.dia_chi):
            self._add_phu_tinh(position, star_name)

    def _build_linhhoa(self, birthTime : TuviTime):
        hoatinh_position = get_hoatinh_position(birthTime, self.tinhBan.direction)
        linhinh_position = get_linhtinh_position(birthTime, self.tinhBan.direction)

        self._add_phu_tinh(hoatinh_position, "Hỏa Tinh")
        self._add_phu_tinh(linhinh_position, "Linh Tinh")

    def _build_dauquan(self, birthTime : TuviTime):

        month_position = get_position_by_move(birthTime.dia_chi, birthTime.month -1, -1)

        dauquan_position = get_position_by_move(month_position, LIST_DIA_CHI.index(birthTime.hour), 1)
        self._add_phu_tinh(dauquan_position, "Đẩu Quân")


    def _build_by_diachi(self, birthTime : TuviTime):
        for star_name, position in get_star_by_dia_chi_position(birthTime.dia_chi):
            self._add_phu_tinh(position, star_name)

    def _build_lavong(self):
        self._add_phu_tinh("Thìn", "Thiên La")
        self._add_phu_tinh("Tuất", "Địa Võng")

    def _build_trangsinh(self):

        trangsinh_position = MAP_TRANGSINH_POSITION[self.tinhBan.cuc.elemental]
        trangsinh_index = LIST_DIA_CHI.index(trangsinh_position)

        for idx, dat_trang_sinh in enumerate(VONG_TRANG_SINH):
            position_index = (trangsinh_index + idx * self.tinhBan.direction) % 12
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
