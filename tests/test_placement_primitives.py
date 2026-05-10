
import pytest

from src.refactored.model.elementary import CircleDirection, DiaChi, ThienCan
from src.refactored.model.prior import Gender, LaSoPrior
from src.refactored.context.natal import NatalContext
from src.refactored.model.cung import NGU_HO_DON_THIEN_CAN, derive_cung_thien_can
from src.refactored.placement.primitives import (
    move_by_attr,
    move_by_birth_month,
    move_by_van_direction,
    move_with,
    position_by_dia_chi_groups,
    position_by_thien_can,
)
@pytest.mark.parametrize(
    "attribute_name, direction, multiplier, expected",
    [
        ("month", CircleDirection.CW, 1, DiaChi.TI),
        ("month", CircleDirection.CCW, 2, DiaChi.THAN),
        ("hour", CircleDirection.CW, 1, DiaChi.TUAT),
    ],
)
def test_move_by_attr(
    attribute_name: str,
    direction: CircleDirection,
    multiplier: int,
    expected: DiaChi,
):
    context = NatalContext.from_prior(
        LaSoPrior(
            hour=DiaChi.THAN,
            date=1,
            month=3,
            year=1984,
            gender=Gender.MALE,
        )
    )

    transform = move_by_attr(
        attribute_name,
        direction=direction,
        step_multiplier=multiplier,
    )

    assert transform(DiaChi.DAN, context) == expected


def test_move_with_uses_context_derived_steps():
    context = NatalContext.from_prior(
        LaSoPrior(
            hour=DiaChi.MEO,
            date=1,
            month=4,
            year=1984,
            gender=Gender.MALE,
        )
    )
    transform = move_with(
        lambda current_context: current_context.prior.month,
        direction=CircleDirection.CW,
    )

    assert transform(DiaChi.DAN, context) == DiaChi.NGO


def test_position_by_thien_can_uses_prior_thien_can():
    context = NatalContext.from_prior(
        LaSoPrior(
            hour=DiaChi.TY,
            date=1,
            month=1,
            year=1960,
            gender=Gender.MALE,
        )
    )
    position_fn = position_by_thien_can(
        {
            ThienCan.GIAP: DiaChi.DAN,
            ThienCan.CANH: DiaChi.THAN,
        }
    )

    assert position_fn(context) == DiaChi.THAN


def test_position_by_dia_chi_groups_uses_group_membership():
    context = NatalContext.from_prior(
        LaSoPrior(
            hour=DiaChi.TY,
            date=1,
            month=1,
            year=1987,
            gender=Gender.MALE,
        )
    )
    position_fn = position_by_dia_chi_groups(
        {
            (DiaChi.DAN, DiaChi.MEO, DiaChi.THIN): DiaChi.TI,
            (DiaChi.TI, DiaChi.NGO, DiaChi.MUI): DiaChi.THAN,
        }
    )

    assert position_fn(context) == DiaChi.TI


@pytest.mark.parametrize(
    "month, direction, expected",
    [
        (1, CircleDirection.CW, DiaChi.DAN),
        (12, CircleDirection.CW, DiaChi.SUU),
        (12, CircleDirection.CCW, DiaChi.MEO),
    ],
)
def test_move_by_birth_month_uses_zero_based_month_offset(
    month: int, direction: CircleDirection, expected: DiaChi
):
    context = NatalContext.from_prior(
        LaSoPrior(
            hour=DiaChi.TY,
            date=1,
            month=month,
            year=1984,
            gender=Gender.MALE,
        )
    )
    transform = move_by_birth_month(direction)

    assert transform(DiaChi.DAN, context) == expected


@pytest.mark.parametrize(
    "gender, expected",
    [
        (Gender.MALE, DiaChi.MEO),
        (Gender.FEMALE, DiaChi.SUU),
    ],
)
def test_move_by_van_direction_uses_chart_direction(
    gender: Gender, expected: DiaChi
):
    context = NatalContext.from_prior(
        LaSoPrior(
            hour=DiaChi.TY,
            date=1,
            month=1,
            year=1984,
            gender=gender,
        )
    )
    transform = move_by_van_direction(lambda _context: 1)

    assert transform(DiaChi.DAN, context) == expected


# Full Ngũ Hổ Độn table from "11.4.4. Phối hợp với mười can".
# Rows: Cung position, columns: paired year Thiên Can.
_NGU_HO_DON_TABLE: dict[DiaChi, dict[ThienCan, ThienCan]] = {
    DiaChi.DAN:  {ThienCan.GIAP: ThienCan.BINH, ThienCan.KY:   ThienCan.BINH, ThienCan.AT:   ThienCan.MAU,  ThienCan.CANH: ThienCan.MAU,  ThienCan.BINH: ThienCan.CANH, ThienCan.TAN:  ThienCan.CANH, ThienCan.DINH: ThienCan.NHAM, ThienCan.NHAM: ThienCan.NHAM, ThienCan.MAU:  ThienCan.GIAP, ThienCan.QUY:  ThienCan.GIAP},
    DiaChi.MEO:  {ThienCan.GIAP: ThienCan.DINH, ThienCan.KY:   ThienCan.DINH, ThienCan.AT:   ThienCan.KY,   ThienCan.CANH: ThienCan.KY,   ThienCan.BINH: ThienCan.TAN,  ThienCan.TAN:  ThienCan.TAN,  ThienCan.DINH: ThienCan.QUY,  ThienCan.NHAM: ThienCan.QUY,  ThienCan.MAU:  ThienCan.AT,   ThienCan.QUY:  ThienCan.AT},
    DiaChi.THIN: {ThienCan.GIAP: ThienCan.MAU,  ThienCan.KY:   ThienCan.MAU,  ThienCan.AT:   ThienCan.CANH, ThienCan.CANH: ThienCan.CANH, ThienCan.BINH: ThienCan.NHAM, ThienCan.TAN:  ThienCan.NHAM, ThienCan.DINH: ThienCan.GIAP, ThienCan.NHAM: ThienCan.GIAP, ThienCan.MAU:  ThienCan.BINH, ThienCan.QUY:  ThienCan.BINH},
    DiaChi.TI:   {ThienCan.GIAP: ThienCan.KY,   ThienCan.KY:   ThienCan.KY,   ThienCan.AT:   ThienCan.TAN,  ThienCan.CANH: ThienCan.TAN,  ThienCan.BINH: ThienCan.QUY,  ThienCan.TAN:  ThienCan.QUY,  ThienCan.DINH: ThienCan.AT,   ThienCan.NHAM: ThienCan.AT,   ThienCan.MAU:  ThienCan.DINH, ThienCan.QUY:  ThienCan.DINH},
    DiaChi.NGO:  {ThienCan.GIAP: ThienCan.CANH, ThienCan.KY:   ThienCan.CANH, ThienCan.AT:   ThienCan.NHAM, ThienCan.CANH: ThienCan.NHAM, ThienCan.BINH: ThienCan.GIAP, ThienCan.TAN:  ThienCan.GIAP, ThienCan.DINH: ThienCan.BINH, ThienCan.NHAM: ThienCan.BINH, ThienCan.MAU:  ThienCan.MAU,  ThienCan.QUY:  ThienCan.MAU},
    DiaChi.MUI:  {ThienCan.GIAP: ThienCan.TAN,  ThienCan.KY:   ThienCan.TAN,  ThienCan.AT:   ThienCan.QUY,  ThienCan.CANH: ThienCan.QUY,  ThienCan.BINH: ThienCan.AT,   ThienCan.TAN:  ThienCan.AT,   ThienCan.DINH: ThienCan.DINH, ThienCan.NHAM: ThienCan.DINH, ThienCan.MAU:  ThienCan.KY,   ThienCan.QUY:  ThienCan.KY},
    DiaChi.THAN: {ThienCan.GIAP: ThienCan.NHAM, ThienCan.KY:   ThienCan.NHAM, ThienCan.AT:   ThienCan.GIAP, ThienCan.CANH: ThienCan.GIAP, ThienCan.BINH: ThienCan.BINH, ThienCan.TAN:  ThienCan.BINH, ThienCan.DINH: ThienCan.MAU,  ThienCan.NHAM: ThienCan.MAU,  ThienCan.MAU:  ThienCan.CANH, ThienCan.QUY:  ThienCan.CANH},
    DiaChi.DAU:  {ThienCan.GIAP: ThienCan.QUY,  ThienCan.KY:   ThienCan.QUY,  ThienCan.AT:   ThienCan.AT,   ThienCan.CANH: ThienCan.AT,   ThienCan.BINH: ThienCan.DINH, ThienCan.TAN:  ThienCan.DINH, ThienCan.DINH: ThienCan.KY,   ThienCan.NHAM: ThienCan.KY,   ThienCan.MAU:  ThienCan.TAN,  ThienCan.QUY:  ThienCan.TAN},
    DiaChi.TUAT: {ThienCan.GIAP: ThienCan.GIAP, ThienCan.KY:   ThienCan.GIAP, ThienCan.AT:   ThienCan.BINH, ThienCan.CANH: ThienCan.BINH, ThienCan.BINH: ThienCan.MAU,  ThienCan.TAN:  ThienCan.MAU,  ThienCan.DINH: ThienCan.CANH, ThienCan.NHAM: ThienCan.CANH, ThienCan.MAU:  ThienCan.NHAM, ThienCan.QUY:  ThienCan.NHAM},
    DiaChi.HOI:  {ThienCan.GIAP: ThienCan.AT,   ThienCan.KY:   ThienCan.AT,   ThienCan.AT:   ThienCan.DINH, ThienCan.CANH: ThienCan.DINH, ThienCan.BINH: ThienCan.KY,   ThienCan.TAN:  ThienCan.KY,   ThienCan.DINH: ThienCan.TAN,  ThienCan.NHAM: ThienCan.TAN,  ThienCan.MAU:  ThienCan.QUY,  ThienCan.QUY:  ThienCan.QUY},
    DiaChi.TY:   {ThienCan.GIAP: ThienCan.BINH, ThienCan.KY:   ThienCan.BINH, ThienCan.AT:   ThienCan.MAU,  ThienCan.CANH: ThienCan.MAU,  ThienCan.BINH: ThienCan.CANH, ThienCan.TAN:  ThienCan.CANH, ThienCan.DINH: ThienCan.NHAM, ThienCan.NHAM: ThienCan.NHAM, ThienCan.MAU:  ThienCan.GIAP, ThienCan.QUY:  ThienCan.GIAP},
    DiaChi.SUU:  {ThienCan.GIAP: ThienCan.DINH, ThienCan.KY:   ThienCan.DINH, ThienCan.AT:   ThienCan.KY,   ThienCan.CANH: ThienCan.KY,   ThienCan.BINH: ThienCan.TAN,  ThienCan.TAN:  ThienCan.TAN,  ThienCan.DINH: ThienCan.QUY,  ThienCan.NHAM: ThienCan.QUY,  ThienCan.MAU:  ThienCan.AT,   ThienCan.QUY:  ThienCan.AT},
}


@pytest.mark.parametrize(
    "year_thien_can, position, expected",
    [
        (year, position, expected)
        for position, row in _NGU_HO_DON_TABLE.items()
        for year, expected in row.items()
    ],
)
def test_derive_cung_thien_can_matches_ngu_ho_don_table(
    year_thien_can: ThienCan, position: DiaChi, expected: ThienCan
):
    assert derive_cung_thien_can(year_thien_can, position) is expected


def test_ngu_ho_don_thien_can_pairs_match_anchor():
    pairs = {
        ThienCan.BINH: (ThienCan.GIAP, ThienCan.KY),
        ThienCan.MAU: (ThienCan.AT, ThienCan.CANH),
        ThienCan.CANH: (ThienCan.BINH, ThienCan.TAN),
        ThienCan.NHAM: (ThienCan.DINH, ThienCan.NHAM),
        ThienCan.GIAP: (ThienCan.MAU, ThienCan.QUY),
    }
    for anchor, year_pair in pairs.items():
        for year in year_pair:
            assert NGU_HO_DON_THIEN_CAN[year] is anchor
