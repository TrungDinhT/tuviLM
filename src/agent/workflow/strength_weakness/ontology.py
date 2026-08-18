"""Candidate capability vocabulary for the strength/weakness workflow.

The ontology names conclusions.  It deliberately contains no mapping from a
Tử Vi star, Cách Cục, or palace to a capability.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType

CAPABILITY_ONTOLOGY_VERSION = "0.1-candidate"


class CapabilityGroup(StrEnum):
    NHAN_THUC_HOC_HOI = "nhan_thuc_hoc_hoi"
    PHAN_DOAN_HANH_DONG = "phan_doan_hanh_dong"
    SANG_TAO_THICH_NGHI = "sang_tao_thich_nghi"
    TO_CHUC_VAN_HANH = "to_chuc_van_hanh"
    GIAO_TIEP_CON_NGUOI = "giao_tiep_con_nguoi"
    TU_QUAN_LY = "tu_quan_ly"


GROUP_LABELS = MappingProxyType(
    {
        CapabilityGroup.NHAN_THUC_HOC_HOI: "Nhận thức và học hỏi",
        CapabilityGroup.PHAN_DOAN_HANH_DONG: "Phán đoán và hành động",
        CapabilityGroup.SANG_TAO_THICH_NGHI: "Sáng tạo và thích nghi",
        CapabilityGroup.TO_CHUC_VAN_HANH: "Tổ chức và vận hành",
        CapabilityGroup.GIAO_TIEP_CON_NGUOI: "Giao tiếp và con người",
        CapabilityGroup.TU_QUAN_LY: "Tự quản lý",
    }
)


@dataclass(frozen=True, slots=True)
class CapabilityDefinition:
    id: str
    label: str
    group: CapabilityGroup
    category: str


def _definitions(
    group: CapabilityGroup,
    category: str,
    items: tuple[tuple[str, str], ...],
) -> tuple[CapabilityDefinition, ...]:
    return tuple(
        CapabilityDefinition(
            id=capability_id,
            label=label,
            group=group,
            category=category,
        )
        for capability_id, label in items
    )


CAPABILITY_DEFINITIONS = (
    *_definitions(
        CapabilityGroup.NHAN_THUC_HOC_HOI,
        "Quan sát và phát hiện",
        (
            ("quan_sat_chi_tiet", "Quan sát chi tiết"),
            ("nhan_dien_bat_thuong", "Nhận diện bất thường"),
            ("nhan_dien_mau_thuan", "Nhận diện mâu thuẫn"),
            ("nhan_dien_tin_hieu_quan_trong", "Nhận diện tín hiệu quan trọng"),
        ),
    ),
    *_definitions(
        CapabilityGroup.NHAN_THUC_HOC_HOI,
        "Phân tích và suy luận",
        (
            ("phan_tich_van_de", "Phân tích vấn đề"),
            ("phan_tich_nguyen_nhan", "Phân tích nguyên nhân"),
            ("lap_luan_logic", "Lập luận logic"),
            ("phan_bien", "Phản biện"),
            ("so_sanh_gia_thuyet", "So sánh giả thuyết"),
            ("xu_ly_nhieu_bien_so", "Xử lý nhiều biến số"),
        ),
    ),
    *_definitions(
        CapabilityGroup.NHAN_THUC_HOC_HOI,
        "Học hỏi",
        (
            ("tiep_thu_kien_thuc", "Tiếp thu kiến thức"),
            ("hoc_nhanh", "Học nhanh"),
            ("hoc_tu_kinh_nghiem", "Học từ kinh nghiệm"),
            ("nhan_dien_quy_luat", "Nhận diện quy luật"),
            ("ket_noi_kien_thuc", "Kết nối kiến thức"),
        ),
    ),
    *_definitions(
        CapabilityGroup.NHAN_THUC_HOC_HOI,
        "Tổng hợp và chiều sâu",
        (
            ("tong_hop_thong_tin", "Tổng hợp thông tin"),
            ("he_thong_hoa_tri_thuc", "Hệ thống hóa tri thức"),
            ("khai_quat_hoa", "Khái quát hóa"),
            ("nhin_da_chieu", "Nhìn đa chiều"),
            ("nghien_cuu_chuyen_sau", "Nghiên cứu chuyên sâu"),
            ("dao_sau_van_de", "Đào sâu vấn đề"),
        ),
    ),
    *_definitions(
        CapabilityGroup.PHAN_DOAN_HANH_DONG,
        "Nhìn trước",
        (
            ("nhin_truoc_he_qua", "Nhìn trước hệ quả"),
            ("tien_lieu_dien_bien", "Tiên liệu diễn biến"),
            ("nhan_dien_rui_ro", "Nhận diện rủi ro"),
            ("lap_phuong_an_du_phong", "Lập phương án dự phòng"),
            ("tu_duy_kich_ban", "Tư duy kịch bản"),
        ),
    ),
    *_definitions(
        CapabilityGroup.PHAN_DOAN_HANH_DONG,
        "Phán đoán",
        (
            ("phan_doan_tinh_huong", "Phán đoán tình huống"),
            ("can_nhac_loi_hai", "Cân nhắc lợi hại"),
            ("danh_gia_trade_off", "Đánh giá đánh đổi"),
            ("xac_dinh_uu_tien", "Xác định ưu tiên"),
            ("danh_gia_thoi_diem", "Đánh giá thời điểm"),
        ),
    ),
    *_definitions(
        CapabilityGroup.PHAN_DOAN_HANH_DONG,
        "Quyết định",
        (
            ("dua_ra_quyet_dinh", "Đưa ra quyết định"),
            ("quyet_doan", "Quyết đoán"),
            ("quyet_dinh_trong_bat_dinh", "Quyết định trong bất định"),
            ("chot_khi_thong_tin_chua_day_du", "Chốt khi thông tin chưa đầy đủ"),
            ("chap_nhan_danh_doi", "Chấp nhận đánh đổi"),
        ),
    ),
    *_definitions(
        CapabilityGroup.PHAN_DOAN_HANH_DONG,
        "Hành động",
        (
            ("khoi_dong_hanh_dong", "Khởi động hành động"),
            ("bien_y_tuong_thanh_hanh_dong", "Biến ý tưởng thành hành động"),
            ("giai_quyet_cong_viec", "Giải quyết công việc"),
            ("hoan_thanh_cong_viec", "Hoàn thành công việc"),
            ("duy_tri_tien_do", "Duy trì tiến độ"),
            ("phan_ung_nhanh", "Phản ứng nhanh"),
            ("xu_ly_tinh_huong_bat_ngo", "Xử lý tình huống bất ngờ"),
            ("hanh_dong_trong_bat_dinh", "Hành động trong bất định"),
            ("xu_ly_khung_hoang", "Xử lý khủng hoảng"),
        ),
    ),
    *_definitions(
        CapabilityGroup.SANG_TAO_THICH_NGHI,
        "Sáng tạo",
        (
            ("phat_sinh_y_tuong", "Phát sinh ý tưởng"),
            ("tao_phuong_an_moi", "Tạo phương án mới"),
            ("tim_cach_giai_khac", "Tìm cách giải khác"),
            ("ket_hop_y_tuong", "Kết hợp ý tưởng"),
            ("tai_dinh_khung_van_de", "Tái định khung vấn đề"),
            ("cai_tien_cach_lam", "Cải tiến cách làm"),
            ("thu_nghiem_phuong_an", "Thử nghiệm phương án"),
        ),
    ),
    *_definitions(
        CapabilityGroup.SANG_TAO_THICH_NGHI,
        "Thích nghi",
        (
            ("ung_bien", "Ứng biến"),
            ("thich_nghi_voi_hoan_canh", "Thích nghi với hoàn cảnh"),
            ("chuyen_huong_khi_can", "Chuyển hướng khi cần"),
            ("bo_cach_lam_khong_hieu_qua", "Bỏ cách làm không hiệu quả"),
            ("dieu_chinh_theo_feedback", "Điều chỉnh theo phản hồi"),
            ("tai_cau_truc", "Tái cấu trúc"),
            (
                "hoat_dong_trong_moi_truong_bien_dong",
                "Hoạt động trong môi trường biến động",
            ),
        ),
    ),
    *_definitions(
        CapabilityGroup.TO_CHUC_VAN_HANH,
        "Tạo cấu trúc",
        (
            ("cau_truc_hoa", "Cấu trúc hóa"),
            ("chia_muc_tieu_thanh_buoc", "Chia mục tiêu thành bước"),
            ("lap_ke_hoach_thuc_hien", "Lập kế hoạch thực hiện"),
            ("sap_xep_uu_tien", "Sắp xếp ưu tiên"),
            ("quan_ly_phu_thuoc", "Quản lý phụ thuộc"),
        ),
    ),
    *_definitions(
        CapabilityGroup.TO_CHUC_VAN_HANH,
        "Quản lý độ phức tạp",
        (
            ("quan_ly_nhieu_dau_viec", "Quản lý nhiều đầu việc"),
            ("phan_bo_nguon_luc", "Phân bổ nguồn lực"),
            ("xay_dung_quy_trinh", "Xây dựng quy trình"),
            ("giu_trat_tu_trong_complexity", "Giữ trật tự trong độ phức tạp"),
            ("theo_doi_tien_do", "Theo dõi tiến độ"),
            ("duy_tri_he_thong", "Duy trì hệ thống"),
            ("tai_to_chuc_he_thong", "Tái tổ chức hệ thống"),
        ),
    ),
    *_definitions(
        CapabilityGroup.TO_CHUC_VAN_HANH,
        "Điều phối",
        (
            ("dieu_phoi_hoat_dong", "Điều phối hoạt động"),
            ("phan_cong", "Phân công"),
            ("giao_viec", "Giao việc"),
            ("phan_quyen", "Phân quyền"),
        ),
    ),
    *_definitions(
        CapabilityGroup.GIAO_TIEP_CON_NGUOI,
        "Diễn đạt",
        (
            ("dien_dat_ro_rang", "Diễn đạt rõ ràng"),
            ("trinh_bay_co_cau_truc", "Trình bày có cấu trúc"),
            ("giai_thich", "Giải thích"),
            ("lam_ro_van_de", "Làm rõ vấn đề"),
        ),
    ),
    *_definitions(
        CapabilityGroup.GIAO_TIEP_CON_NGUOI,
        "Lập luận và ảnh hưởng",
        (
            ("lap_luan_bang_loi", "Lập luận bằng lời"),
            ("tranh_bien", "Tranh biện"),
            ("thuyet_phuc", "Thuyết phục"),
            ("tao_anh_huong_bang_ngon_ngu", "Tạo ảnh hưởng bằng ngôn ngữ"),
            ("dam_phan", "Đàm phán"),
        ),
    ),
    *_definitions(
        CapabilityGroup.GIAO_TIEP_CON_NGUOI,
        "Đọc và điều chỉnh theo người khác",
        (
            ("nhan_biet_phan_ung_nguoi_khac", "Nhận biết phản ứng người khác"),
            ("doc_dong_co_nguoi_khac", "Đọc động cơ người khác"),
            ("dieu_chinh_cach_giao_tiep", "Điều chỉnh cách giao tiếp"),
            ("nhan_biet_bau_khong_khi_nhom", "Nhận biết bầu không khí nhóm"),
        ),
    ),
    *_definitions(
        CapabilityGroup.GIAO_TIEP_CON_NGUOI,
        "Hợp tác",
        (
            ("hop_tac", "Hợp tác"),
            ("phoi_hop_nhom", "Phối hợp nhóm"),
            ("chia_se_quyen_kiem_soat", "Chia sẻ quyền kiểm soát"),
            ("tao_dong_thuan", "Tạo đồng thuận"),
            ("giai_quyet_xung_dot", "Giải quyết xung đột"),
        ),
    ),
    *_definitions(
        CapabilityGroup.GIAO_TIEP_CON_NGUOI,
        "Dẫn dắt",
        (
            ("dinh_huong_nhom", "Định hướng nhóm"),
            ("huy_dong_nguoi_khac", "Huy động người khác"),
            ("tao_cam_ket", "Tạo cam kết"),
            ("duy_tri_dong_luc_tap_the", "Duy trì động lực tập thể"),
            ("dung_ra_nhan_trach_nhiem", "Đứng ra nhận trách nhiệm"),
        ),
    ),
    *_definitions(
        CapabilityGroup.TU_QUAN_LY,
        "Duy trì bản thân",
        (
            ("duy_tri_tap_trung", "Duy trì tập trung"),
            ("kien_tri", "Kiên trì"),
            ("ky_luat_hanh_dong", "Kỷ luật hành động"),
            ("duy_tri_nhip_do", "Duy trì nhịp độ"),
        ),
    ),
    *_definitions(
        CapabilityGroup.TU_QUAN_LY,
        "Tự điều chỉnh",
        (
            ("kiem_soat_xung_dong", "Kiểm soát xung động"),
            ("tu_dieu_chinh", "Tự điều chỉnh"),
            ("kiem_soat_phan_ung_cam_xuc", "Kiểm soát phản ứng cảm xúc"),
            ("biet_dung_khi_can", "Biết dừng khi cần"),
            ("biet_buong_mot_van_de", "Biết buông một vấn đề"),
        ),
    ),
    *_definitions(
        CapabilityGroup.TU_QUAN_LY,
        "Dưới áp lực",
        (
            ("giu_chuc_nang_duoi_ap_luc", "Giữ chức năng dưới áp lực"),
            ("chiu_dung_bat_dinh", "Chịu đựng bất định"),
            ("binh_tinh_trong_khung_hoang", "Bình tĩnh trong khủng hoảng"),
            ("khoi_phuc_quyen_chu_dong", "Khôi phục quyền chủ động"),
        ),
    ),
    *_definitions(
        CapabilityGroup.TU_QUAN_LY,
        "Phục hồi và học sau thất bại",
        (
            ("phuc_hoi_sau_kho_khan", "Phục hồi sau khó khăn"),
            ("tai_tham_gia_sau_that_bai", "Tái tham gia sau thất bại"),
            ("rut_kinh_nghiem_sau_that_bai", "Rút kinh nghiệm sau thất bại"),
            ("dieu_chinh_sau_feedback", "Điều chỉnh sau phản hồi"),
        ),
    ),
)


CAPABILITY_BY_ID = MappingProxyType(
    {definition.id: definition for definition in CAPABILITY_DEFINITIONS}
)


def get_capability_definition(capability_id: str) -> CapabilityDefinition:
    try:
        return CAPABILITY_BY_ID[capability_id]
    except KeyError as exc:
        raise ValueError(f"Unknown capability id {capability_id!r}.") from exc


def build_capability_ontology_instruction() -> str:
    """Render the candidate ontology as vocabulary, never as astrology rules."""
    lines = [
        "## Danh mục năng lực (vocabulary only)",
        f"Phiên bản: {CAPABILITY_ONTOLOGY_VERSION}.",
        (
            "Chỉ dùng các ID dưới đây để gọi tên kết luận. Danh mục không chứa "
            "mapping từ sao/cách cục sang năng lực."
        ),
    ]
    for group in CapabilityGroup:
        lines.append(f"\n### {GROUP_LABELS[group]}")
        current_category: str | None = None
        for definition in CAPABILITY_DEFINITIONS:
            if definition.group != group:
                continue
            if definition.category != current_category:
                current_category = definition.category
                lines.append(f"- {current_category}:")
            lines.append(f"  - `{definition.id}` — {definition.label}")
    return "\n".join(lines)


__all__ = [
    "CAPABILITY_BY_ID",
    "CAPABILITY_DEFINITIONS",
    "CAPABILITY_ONTOLOGY_VERSION",
    "CapabilityDefinition",
    "CapabilityGroup",
    "build_capability_ontology_instruction",
    "get_capability_definition",
]
