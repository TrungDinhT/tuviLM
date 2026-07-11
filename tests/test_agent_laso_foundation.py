from src.agent.tool.ban_menh.ban_menh_meaning import BAN_MENH_MEANINGS
from src.agent.tool.ban_menh.laso_foundation import build_laso_foundation_payload
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

    assert set(foundation) == {
        "am_duong_thuan_nghich",
        "ban_menh",
        "cuc",
        "menh_cuc_relation",
    }

    am_duong_relation = foundation["am_duong_thuan_nghich"]
    assert am_duong_relation["relation"] == "nghịch lý"
    assert "Lệch pha" in am_duong_relation["environment_alignment"]
    assert "đa luồng" in am_duong_relation["thinking_consistency"]
    assert "status" not in am_duong_relation
    assert "usage" not in am_duong_relation
    assert "scope_note" not in am_duong_relation
    assert "combination_note" not in am_duong_relation

    assert foundation["ban_menh"]["name"] == "Giản Hạ Thủy"
    assert foundation["ban_menh"]["ngu_hanh"] == "Thủy"
    assert foundation["ban_menh"]["meaning"]["symbol"] == "Nước khe suối"
    assert "khó dò" in foundation["ban_menh"]["meaning"]["keywords"]
    assert "sources" not in foundation["ban_menh"]["meaning"]

    assert foundation["cuc"]["name"] == "Hỏa Lục cục"
    assert foundation["cuc"]["ngu_hanh"] == "Hỏa"

    menh_cuc_relation = foundation["menh_cuc_relation"]
    assert menh_cuc_relation == {
        "relation": "Mệnh khắc Cục",
        "meaning": "Người có khả năng thay đổi, cải cách môi trường xung quanh mình.",
    }


def test_laso_foundation_reports_both_am_duong_polarity_relations():
    thuan_ly = build_laso_foundation_payload(
        LaSo.from_prior(
            LaSoPrior(
                hour=DiaChi.TY,
                date=1,
                month=1,
                year=1984,
                gender=Gender.MALE,
            )
        )
    )

    relation = thuan_ly["am_duong_thuan_nghich"]

    assert relation["relation"] == "thuận lý"
    assert "Hòa hợp" in relation["environment_alignment"]
    assert "một dòng mạch lạc" in relation["thinking_consistency"]


def test_laso_foundation_has_ban_menh_meanings_without_source_metadata():
    assert len(BAN_MENH_MEANINGS) == 30

    foundation = build_laso_foundation_payload(
        LaSo.from_prior(
            LaSoPrior(
                hour=DiaChi.MEO,
                date=10,
                month=11,
                year=1998,
                gender=Gender.MALE,
            )
        )
    )

    ban_menh_meaning = foundation["ban_menh"]["meaning"]

    assert foundation["ban_menh"]["name"] == "Thành Đầu Thổ"
    assert "phòng thủ" in ban_menh_meaning["keywords"]
    assert "sources" not in ban_menh_meaning
    assert foundation["menh_cuc_relation"]["relation"] == "Cục khắc Mệnh"
