"""Regression checks for shared ``tests/fixtures/laso_priors`` data."""

from src.refactored.builder.placement_builder import PlacementBuilder
from src.refactored.context.natal import NatalContext
from src.refactored.placement.rules import get_default_placement_rule_compiler
from tests.fixtures.laso_priors import (
    EXPECTED_A,
    EXPECTED_FEMALE_AM,
    EXPECTED_MALE_DUONG,
    FIXTURE_PRIOR_A,
    FIXTURE_PRIOR_FEMALE_AM,
    FIXTURE_PRIOR_MALE_DUONG,
)


def test_fixture_prior_a_matches_expected_positions():
    ctx = NatalContext.from_prior(FIXTURE_PRIOR_A)
    assert ctx.menh_position == EXPECTED_A["menh_position"]
    assert ctx.cuc.number == EXPECTED_A["cuc_number"]
    assert ctx.cuc.ngu_hanh == EXPECTED_A["cuc_ngu_hanh"]
    assert ctx.van_direction == EXPECTED_A["van_direction"]

    builder = PlacementBuilder(ctx, compiler=get_default_placement_rule_compiler())
    positions = builder.resolve_all()
    assert positions["tu_vi"] == EXPECTED_A["tu_vi_position"]
    assert positions["thien_phu"] == EXPECTED_A["thien_phu_position"]
    assert positions["loc_ton"] == EXPECTED_A["loc_ton_position"]
    assert positions["cung_than"] == EXPECTED_A["cung_than_position"]
    assert positions["thai_tue"] == EXPECTED_A["thai_tue_position"]
    assert ctx.dia_chi == EXPECTED_A["year_dia_chi"]
    assert ctx.thien_can == EXPECTED_A["year_thien_can"]


def test_fixture_female_am_and_male_duong_van_directions():
    ctx_f = NatalContext.from_prior(FIXTURE_PRIOR_FEMALE_AM)
    ctx_m = NatalContext.from_prior(FIXTURE_PRIOR_MALE_DUONG)
    assert ctx_f.van_direction == EXPECTED_FEMALE_AM["van_direction"]
    assert ctx_m.van_direction == EXPECTED_MALE_DUONG["van_direction"]
