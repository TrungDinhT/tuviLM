from src.agent.tool.thai_tue import (
    THAI_TUE_RING_STAR_IDS,
    build_vong_thai_tue_payload,
)
from src.refactored.la_so import LaSo
from src.refactored.model.elementary import DiaChi
from src.refactored.model.prior import Gender, LaSoPrior
from tests.fixtures.laso_priors import FIXTURE_PRIOR_A


def test_vong_thai_tue_identifies_star_and_group_at_menh():
    payload = build_vong_thai_tue_payload(LaSo.from_prior(FIXTURE_PRIOR_A))

    assert payload["menh"]["position"]["name"] == "Tý"
    assert payload["menh"]["thai_tue_star"] == {
        "id": "tue_pha",
        "name": "Tuế Phá",
        "ngu_hanh": "Hỏa",
    }
    assert payload["menh"]["group"]["id"] == "doi_lap"
    assert payload["menh"]["group"]["name"] == "Nhóm Đối Lập"
    assert "phản nghịch" in payload["menh"]["star_meaning"]["keywords"]

    thien_ma = payload["technical_support"]["thien_ma"]
    assert thien_ma["lens"]["element"] == "Kim"
    assert thien_ma["tuan_triet"] == []
    assert "tuan_triet_at_menh" not in payload["technical_support"]
    assert "khong_kiep_at_menh" not in payload["technical_support"]
    assert "thai_tue_sat_tinh_at_menh" not in payload["technical_support"]


def test_vong_thai_tue_payload_omits_workflow_and_full_ring_metadata():
    payload = build_vong_thai_tue_payload(LaSo.from_prior(FIXTURE_PRIOR_A))

    assert set(payload) == {"menh", "technical_support"}
    assert "scope" not in payload
    assert "reading_steps" not in payload
    assert "ring_positions" not in payload


def test_vong_thai_tue_group_meanings_include_core_notes():
    group_payloads = {
        "doi_lap": _payload_for_1984_hour(DiaChi.TY)["menh"]["group"],
        "khon_ngoan": _payload_for_1984_hour(DiaChi.SUU)["menh"]["group"],
        "chinh_phai": _payload_for_1984_hour(DiaChi.DAN)["menh"]["group"],
        "nhuong_nhin": _payload_for_1984_hour(DiaChi.MEO)["menh"]["group"],
    }

    chinh_phai = _combined_group_text(group_payloads["chinh_phai"])
    assert "Người Quân tử" in group_payloads["chinh_phai"]["archetype"]
    assert "chính danh" in chinh_phai
    assert "cô độc" in chinh_phai

    khon_ngoan = _combined_group_text(group_payloads["khon_ngoan"])
    assert "Sắc tức thị Không" in group_payloads["khon_ngoan"]["archetype"]
    assert "lấn lướt" in khon_ngoan
    assert "Thiên Không" in khon_ngoan
    assert "Zero" in khon_ngoan

    doi_lap = _combined_group_text(group_payloads["doi_lap"])
    assert "Sức mạnh nghịch cảnh" in group_payloads["doi_lap"]["archetype"]
    assert "star_ids" not in group_payloads["doi_lap"]
    assert "bàn ra" in doi_lap
    assert "Thiên Mã" in doi_lap

    nhuong_nhin = _combined_group_text(group_payloads["nhuong_nhin"])
    assert "Sự nhẹ dạ" in group_payloads["nhuong_nhin"]["archetype"]
    assert "cam chịu" in nhuong_nhin
    assert "tôn chỉ sống" in nhuong_nhin
    assert "đào giếng" in nhuong_nhin


def test_vong_thai_tue_star_meanings_include_new_character_notes():
    thai_tue = _payload_for_1984_hour(DiaChi.DAN)["menh"]["star_meaning"]
    assert "quân tử" in thai_tue["reading_hint"]
    assert "tình cảm" in thai_tue["shadow"]
    assert "Không/Kiếp/Hỏa/Linh" in thai_tue["reading_hint"]

    thieu_duong = _payload_for_1984_hour(DiaChi.SUU)["menh"]["star_meaning"]
    assert "Đường Tăng" in thieu_duong["reading_hint"]
    assert "Đào Hoa/Hồng Loan" in thieu_duong["shadow"]

    tue_pha = build_vong_thai_tue_payload(
        LaSo.from_prior(
            LaSoPrior(
                hour=DiaChi.THAN,
                date=1,
                month=1,
                year=1984,
                gender=Gender.MALE,
            )
        )
    )["menh"]["star_meaning"]
    assert "Tôn Ngộ Không" in tue_pha["at_menh"]
    assert "Thiên Mã" in tue_pha["reading_hint"]

    thieu_am = build_vong_thai_tue_payload(
        LaSo.from_prior(
            LaSoPrior(
                hour=DiaChi.HOI,
                date=1,
                month=1,
                year=1984,
                gender=Gender.MALE,
            )
        )
    )["menh"]["star_meaning"]
    assert "Trư Bát Giới" in thieu_am["at_menh"]
    assert "lợi ích nhỏ trước mắt" in thieu_am["keywords"]


def test_vong_thai_tue_uses_sao_phuc_duc_not_cung_phuc_duc():
    la_so = LaSo.from_prior(
        LaSoPrior(
            hour=DiaChi.TI,
            date=1,
            month=1,
            year=1984,
            gender=Gender.MALE,
        )
    )

    payload = build_vong_thai_tue_payload(la_so)

    assert "sao_phuc_duc" in THAI_TUE_RING_STAR_IDS
    assert "phuc_duc" not in THAI_TUE_RING_STAR_IDS
    assert payload["menh"]["thai_tue_star"]["id"] == "sao_phuc_duc"
    assert payload["menh"]["thai_tue_star"]["name"] == "Phúc Đức"
    assert payload["menh"]["group"]["id"] == "khon_ngoan"

    assert "thien_ma" not in payload["technical_support"]
    assert "tuan_triet_at_menh" not in payload["technical_support"]
    assert "khong_kiep_at_menh" not in payload["technical_support"]
    assert "thai_tue_sat_tinh_at_menh" not in payload["technical_support"]


def test_vong_thai_tue_only_reports_sat_tinh_when_thai_tue_meets_it():
    la_so = LaSo.from_prior(
        LaSoPrior(
            hour=DiaChi.HOI,
            date=1,
            month=10,
            year=1900,
            gender=Gender.MALE,
        )
    )

    payload = build_vong_thai_tue_payload(la_so)

    assert payload["menh"]["thai_tue_star"]["id"] == "thai_tue"
    assert "thien_ma" not in payload["technical_support"]
    assert "khong_kiep_at_menh" not in payload["technical_support"]

    sat_tinh = payload["technical_support"]["thai_tue_sat_tinh_at_menh"]
    assert sat_tinh["stars"] == [
        {"id": "dia_khong", "name": "Địa Không", "ngu_hanh": "Hỏa"}
    ]


def test_vong_thai_tue_reports_hoa_linh_as_sat_tinh_when_they_meet_thai_tue():
    payload = build_vong_thai_tue_payload(
        LaSo.from_prior(
            LaSoPrior(
                hour=DiaChi.TUAT,
                date=1,
                month=9,
                year=1900,
                gender=Gender.MALE,
            )
        )
    )

    assert payload["menh"]["thai_tue_star"]["id"] == "thai_tue"
    sat_tinh = payload["technical_support"]["thai_tue_sat_tinh_at_menh"]
    assert sat_tinh["stars"] == [
        {"id": "hoa_tinh", "name": "Hỏa Tinh", "ngu_hanh": "Hỏa"},
        {"id": "linh_tinh", "name": "Linh Tinh", "ngu_hanh": "Hỏa"},
    ]


def _payload_for_1984_hour(hour: DiaChi) -> dict[str, object]:
    return build_vong_thai_tue_payload(
        LaSo.from_prior(
            LaSoPrior(
                hour=hour,
                date=1,
                month=1,
                year=1984,
                gender=Gender.MALE,
            )
        )
    )


def _combined_group_text(group: dict[str, object]) -> str:
    return " ".join(
        str(group[field])
        for field in ("overview", "reading_lens", "trap")
    )
