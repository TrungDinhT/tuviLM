"""Scope expansion for cach_cuc star relationships."""

from __future__ import annotations

from src.refactored.model.elementary import DiaChi


NHI_HOP_PAIRS: dict[DiaChi, DiaChi] = {
    DiaChi.TY: DiaChi.SUU,
    DiaChi.SUU: DiaChi.TY,
    DiaChi.DAN: DiaChi.HOI,
    DiaChi.HOI: DiaChi.DAN,
    DiaChi.MEO: DiaChi.TUAT,
    DiaChi.TUAT: DiaChi.MEO,
    DiaChi.THIN: DiaChi.DAU,
    DiaChi.DAU: DiaChi.THIN,
    DiaChi.TI: DiaChi.THAN,
    DiaChi.THAN: DiaChi.TI,
    DiaChi.NGO: DiaChi.MUI,
    DiaChi.MUI: DiaChi.NGO,
}


def positions_for_scope(anchor: DiaChi, scope: str) -> frozenset[DiaChi]:
    """Expand a scope name into concrete positions relative to an anchor."""
    if scope == "dong_cung":
        return frozenset((anchor,))
    if scope == "xung_chieu":
        return frozenset((anchor + 6,))
    if scope == "dong_hoac_xung":
        return frozenset((anchor, anchor + 6))
    if scope == "tam_hop":
        return frozenset((anchor, anchor + 4, anchor + 8))
    if scope == "hoi_hop":
        return frozenset((anchor, anchor + 4, anchor + 8, anchor + 6))
    if scope == "giap":
        return frozenset((anchor - 1, anchor + 1))
    if scope == "nhi_hop":
        return frozenset((NHI_HOP_PAIRS[anchor],))
    raise ValueError(f"Unsupported cach_cuc scope: {scope}")
