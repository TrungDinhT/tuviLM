from __future__ import annotations

from src.refactored.components.definitions.elementary import ComponentBase
from src.refactored.model.elementary import NguHanh

# Ordered list of 30 ban_menh ids covering a 60-year cycle.
# Each entry spans 2 consecutive years.
_BAN_MENH_CYCLE: list[str] = [
    "tich_lich_hoa",      # e.g. 1948-1949
    "tung_bach_moc",      # e.g. 1950-1951
    "truong_luu_thuy",    # e.g. 1952-1953
    "sa_trung_kim",       # e.g. 1954-1955
    "son_ha_hoa",         # e.g. 1956-1957
    "binh_dia_moc",       # e.g. 1958-1959
    "bich_thuong_tho",    # e.g. 1960-1961
    "kim_bach_kim",       # e.g. 1962-1963
    "phu_dang_hoa",       # e.g. 1964-1965
    "thien_ha_thuy",      # e.g. 1966-1967
    "dai_dich_tho",       # e.g. 1968-1969
    "thoa_xuyen_kim",     # e.g. 1970-1971
    "tang_do_moc",        # e.g. 1972-1973
    "dai_khe_thuy",       # e.g. 1974-1975
    "sa_trung_tho",       # e.g. 1976-1977
    "thien_thuong_hoa",   # e.g. 1978-1979
    "thach_luu_moc",      # e.g. 1980-1981
    "dai_hai_thuy",       # e.g. 1982-1983
    "hai_trung_kim",      # e.g. 1984-1985
    "lo_trung_hoa",       # e.g. 1986-1987
    "dai_lam_moc",        # e.g. 1988-1989
    "lo_bang_tho",        # e.g. 1990-1991
    "kiem_phong_kim",     # e.g. 1992-1993
    "son_dau_hoa",        # e.g. 1994-1995
    "gian_ha_thuy",       # e.g. 1996-1997
    "thanh_dau_tho",      # e.g. 1998-1999
    "bach_lap_kim",       # e.g. 2000-2001
    "duong_lieu_moc",     # e.g. 2002-2003
    "tuyen_trung_thuy",   # e.g. 2004-2005
    "oc_thuong_tho",      # e.g. 2006-2007
]


def compute_ban_menh_id(year: int) -> str:
    """Return the ban_menh component id for a given birth year.

    The cycle is 60 years long (30 entries × 2 years each),
    anchored so that 1948 maps to the first entry.
    """
    index = ((year - 1948) % 60) // 2
    return _BAN_MENH_CYCLE[index]


class BanMenh(ComponentBase):
    model_config = {"frozen": True}

    ngu_hanh: NguHanh
    description: str
