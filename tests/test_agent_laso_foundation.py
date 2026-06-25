from src.agent.tool import build_laso_foundation_payload
from src.refactored.la_so import LaSo
from src.refactored.model.elementary import DiaChi
from src.refactored.model.prior import Gender, LaSoPrior


def test_laso_foundation_projects_root_chart_factors():
    la_so = LaSo.from_prior(
        LaSoPrior(
            hour=DiaChi.MEO,
            date=10,
            month=11,
            year=1996,
            gender=Gender.MALE,
        )
    )

    foundation = build_laso_foundation_payload(la_so)

    assert foundation["birth_year"] == 1996
    assert foundation["lunar_year"] == "Bính Tý"
    assert foundation["thien_can_year"]["name"] == "Bính"
    assert foundation["thien_can_year"]["am_duong"] == "Dương"
    assert foundation["thien_can_year"]["ngu_hanh"] == "Hỏa"
    assert foundation["dia_chi_year"]["name"] == "Tý"
    assert foundation["dia_chi_year"]["am_duong"] == "Dương"
    assert foundation["dia_chi_year"]["ngu_hanh"] == "Thủy"
    assert foundation["gender_polarity"] == "Dương Nam"
    assert foundation["van_direction"] == "thuận"
    assert foundation["menh_position"]["id"] == "dau"
    assert foundation["menh_position"]["name"] == "Dậu"
    assert foundation["menh_position"]["year_menh_polarity_relation"] == "nghịch lý"
    assert foundation["ban_menh"]["name"] == "Giản Hạ Thủy"
    assert foundation["cuc"]["name"] == "Hỏa Lục cục"
    assert foundation["cuc"]["number"] == 6
    assert foundation["menh_cuc_relation"]["label"] == "Mệnh khắc cục"
    assert "giảm độ số" in foundation["menh_cuc_relation"]["interpretation"]

    first_dai_han, second_dai_han = foundation["dai_han_ranges"][:2]
    assert first_dai_han["start_age"] == 6
    assert first_dai_han["end_age"] == 15
    assert first_dai_han["focus_position_id"] == "dau"
    assert second_dai_han["start_age"] == 16
    assert second_dai_han["focus_position_id"] == "tuat"


def test_laso_foundation_reports_all_gender_polarity_directions():
    female_duong = build_laso_foundation_payload(
        LaSo.from_prior(
            LaSoPrior(
                hour=DiaChi.MEO,
                date=10,
                month=11,
                year=1996,
                gender=Gender.FEMALE,
            )
        )
    )
    female_am = build_laso_foundation_payload(
        LaSo.from_prior(
            LaSoPrior(
                hour=DiaChi.TY,
                date=1,
                month=1,
                year=1985,
                gender=Gender.FEMALE,
            )
        )
    )
    male_am = build_laso_foundation_payload(
        LaSo.from_prior(
            LaSoPrior(
                hour=DiaChi.TY,
                date=1,
                month=1,
                year=1985,
                gender=Gender.MALE,
            )
        )
    )

    assert female_duong["gender_polarity"] == "Dương Nữ"
    assert female_duong["van_direction"] == "nghịch"
    assert female_am["gender_polarity"] == "Âm Nữ"
    assert female_am["van_direction"] == "thuận"
    assert male_am["gender_polarity"] == "Âm Nam"
    assert male_am["van_direction"] == "nghịch"


def test_laso_foundation_keeps_source_notes_for_agent_citations():
    foundation = build_laso_foundation_payload(
        LaSo.from_prior(
            LaSoPrior(
                hour=DiaChi.MEO,
                date=10,
                month=11,
                year=1996,
                gender=Gender.MALE,
            )
        )
    )

    source_ids = {source["id"] for source in foundation["source_notes"]}

    assert "tuvitanbien_2_tim_ban_menh" in source_ids
    assert "tuvitanbien_7_lap_cuc" in source_ids
    assert "tuvitanbien_1_4_ban_menh_cuc" in source_ids
    assert foundation["foundation_effects"]
    assert foundation["interpretation_order"][0].startswith("Xác định can-chi")
