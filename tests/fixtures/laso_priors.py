"""Shared birth priors and hand-checked expectation snapshots for refactored tests.

Values for ``EXPECTED_A`` were aligned with ``PlacementBuilder`` / legacy chart runs
for the corresponding solar datetime.
"""

from __future__ import annotations

import datetime as dt

from src.refactored.component.cuc import NguHanh
from src.refactored.component.elementary import CircleDirection, DiaChi, ThienCan
from src.refactored.context.prior import Gender, LaSoPrior

# Canonical happy-path birth (Nam, same instant as placement regression tests).
_SOLAR_A = dt.datetime(1990, 5, 15, 10, 30)

FIXTURE_PRIOR_A: LaSoPrior = LaSoPrior.from_solar_day(_SOLAR_A, Gender.MALE)

# Same instant as A; female chart uses opposite vận direction for this year branch.
FIXTURE_PRIOR_FEMALE_AM: LaSoPrior = LaSoPrior.from_solar_day(_SOLAR_A, Gender.FEMALE)

# Nam + Dương (same chart as A for this solar date).
FIXTURE_PRIOR_MALE_DUONG: LaSoPrior = LaSoPrior.from_solar_day(_SOLAR_A, Gender.MALE)

EXPECTED_A: dict[str, object] = {
    "menh_position": DiaChi.TY,
    "cuc_number": 6,
    "cuc_ngu_hanh": NguHanh.HOA,
    "tu_vi_position": DiaChi.THAN,
    "thien_phu_position": DiaChi.THAN,
    "loc_ton_position": DiaChi.THAN,
    "cung_than_position": DiaChi.TUAT,
    "thai_tue_position": DiaChi.NGO,
    "year_dia_chi": DiaChi.NGO,
    "year_thien_can": ThienCan.CANH,
    "van_direction": CircleDirection.CW,
}

EXPECTED_FEMALE_AM: dict[str, object] = {
    "van_direction": CircleDirection.CCW,
}

EXPECTED_MALE_DUONG: dict[str, object] = {
    "van_direction": CircleDirection.CW,
}
