from __future__ import annotations

from dataclasses import dataclass

from src.refactored.component.cuc import Cuc, LIST_CUC
from src.refactored.component.elementary import CircleDirection, DiaChi, LuongNghi, ThienCan
from src.refactored.context.prior import Gender, LaSoPrior


def _get_menh_position(prior: LaSoPrior) -> DiaChi:
    month_anchor = DiaChi.DAN + (prior.month - 1)
    return month_anchor - prior.hour.index


def _match_cuc_group(menh_position: DiaChi) -> int:
    if menh_position in (DiaChi.TY, DiaChi.SUU):
        return 0
    if menh_position in (DiaChi.DAN, DiaChi.MEO, DiaChi.TUAT, DiaChi.HOI):
        return 1
    if menh_position in (DiaChi.THIN, DiaChi.TI):
        return 2
    if menh_position in (DiaChi.NGO, DiaChi.MUI):
        return 3
    if menh_position in (DiaChi.THAN, DiaChi.DAU):
        return 4
    raise ValueError(f"Unsupported menh position for cuc: {menh_position}")


def _get_cuc(prior: LaSoPrior, menh_position: DiaChi) -> Cuc:
    cuc_index_orders = {
        ThienCan.GIAP: [0, 4, 1, 3, 2],
        ThienCan.KY: [0, 4, 1, 3, 2],
        ThienCan.AT: [4, 3, 2, 1, 0],
        ThienCan.CANH: [4, 3, 2, 1, 0],
        ThienCan.BINH: [3, 1, 0, 2, 4],
        ThienCan.TAN: [3, 1, 0, 2, 4],
        ThienCan.DINH: [1, 2, 4, 0, 3],
        ThienCan.NHAM: [1, 2, 4, 0, 3],
        ThienCan.MAU: [2, 0, 3, 4, 1],
        ThienCan.QUY: [2, 0, 3, 4, 1],
    }
    cuc_group = _match_cuc_group(menh_position)
    cuc_index = cuc_index_orders[prior.get_thien_can()][cuc_group]
    return LIST_CUC[cuc_index]


@dataclass(frozen=True)
class NatalContext:
    """Natal (birth) placement context: prior birth data + derived chart anchors."""

    prior: LaSoPrior
    menh_position: DiaChi

    @classmethod
    def from_prior(cls, prior: LaSoPrior) -> NatalContext:
        menh_position = _get_menh_position(prior)
        return cls(prior=prior, menh_position=menh_position)

    @property
    def dia_chi(self) -> DiaChi:
        return self.prior.year.dia_chi

    @property
    def thien_can(self) -> ThienCan:
        return self.prior.year.thien_can

    @property
    def am_duong(self) -> LuongNghi:
        return LuongNghi(self.prior.year.dia_chi.index % 2)

    @property
    def van_direction(self) -> CircleDirection:
        return (
            CircleDirection.CW
            if (
                self.prior.gender == Gender.MALE
                and self.am_duong == LuongNghi.DUONG
            )
            or (
                self.prior.gender == Gender.FEMALE
                and self.am_duong == LuongNghi.AM
            )
            else CircleDirection.CCW
        )

    @property
    def cuc(self) -> Cuc:
        return _get_cuc(self.prior, self.menh_position)
