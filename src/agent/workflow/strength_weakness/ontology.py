"""Candidate capability vocabulary for the strength/weakness workflow.

The ontology names conclusions.  It deliberately contains no mapping from a
Tử Vi star, Cách Cục, or palace to a capability.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType

CAPABILITY_ONTOLOGY_VERSION = "0.2-candidate"


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

CAPABILITY_DESCRIPTIONS = MappingProxyType(
    {
        "quan_sat_chi_tiet": "Nhận ra các chi tiết nhỏ, sai lệch tinh vi hoặc yếu tố dễ bị bỏ sót trong thông tin hay tình huống.",
        "nhan_dien_bat_thuong": "Phát hiện điểm khác thường, lệch chuẩn hoặc không khớp với trạng thái và quy luật thông thường.",
        "nhan_dien_mau_thuan": "Nhận ra các thông tin, lập luận, mục tiêu hoặc hành vi xung đột hay không nhất quán với nhau.",
        "nhan_dien_tin_hieu_quan_trong": "Tách được tín hiệu có giá trị khỏi nhiễu và nhận ra yếu tố nào đáng chú ý nhất.",
        "phan_tich_van_de": "Tách một vấn đề thành các thành phần để hiểu cấu trúc, quan hệ và điểm cần xử lý.",
        "phan_tich_nguyen_nhan": "Truy tìm các nguyên nhân và cơ chế tạo ra một kết quả, thay vì chỉ mô tả hiện tượng.",
        "lap_luan_logic": "Suy luận theo chuỗi tiền đề–kết luận nhất quán, hạn chế bước nhảy hoặc mâu thuẫn logic.",
        "phan_bien": "Kiểm tra giả định, tìm lỗ hổng và đánh giá độ vững của một nhận định trước khi chấp nhận.",
        "so_sanh_gia_thuyet": "Đặt nhiều cách giải thích cạnh nhau và cân bằng chứng để chọn giả thuyết hợp lý hơn.",
        "xu_ly_nhieu_bien_so": "Theo dõi và cân nhắc đồng thời nhiều yếu tố có tương tác mà không làm mất bức tranh chung.",
        "tiep_thu_kien_thuc": "Hiểu và ghi nhận kiến thức mới khi được học, đọc hoặc hướng dẫn.",
        "hoc_nhanh": "Rút ngắn thời gian cần thiết để nắm một lĩnh vực, kỹ năng hoặc quy tắc mới.",
        "hoc_tu_kinh_nghiem": "Biến trải nghiệm thực tế, kể cả sai lầm, thành hiểu biết dùng được cho lần sau.",
        "nhan_dien_quy_luat": "Nhận ra mẫu lặp, cấu trúc hoặc quy luật ẩn từ nhiều quan sát riêng lẻ.",
        "ket_noi_kien_thuc": "Liên kết kiến thức từ các nguồn hoặc lĩnh vực khác nhau để tạo hiểu biết hữu ích hơn.",
        "tong_hop_thong_tin": "Gom nhiều mảnh thông tin thành một bức tranh cô đọng, nhất quán và có ý nghĩa.",
        "he_thong_hoa_tri_thuc": "Sắp xếp kiến thức thành hệ thống khái niệm, nhóm và quan hệ để dễ hiểu và tái sử dụng.",
        "khai_quat_hoa": "Rút ra nguyên tắc hoặc kết luận chung từ nhiều trường hợp cụ thể mà không lệ thuộc vào chi tiết.",
        "nhin_da_chieu": "Xem cùng một vấn đề từ nhiều góc nhìn, lợi ích hoặc hệ quy chiếu trước khi kết luận.",
        "nghien_cuu_chuyen_sau": "Duy trì việc tìm hiểu có hệ thống đến mức chuyên sâu, tích lũy kiến thức dày và chắc.",
        "dao_sau_van_de": "Không dừng ở lời giải bề mặt; tiếp tục hỏi và truy xét để chạm đến bản chất hoặc lớp nguyên nhân sâu.",
        "nhin_truoc_he_qua": "Ước lượng những hệ quả có thể phát sinh sau một lựa chọn, gồm cả tác động gián tiếp và dài hạn.",
        "tien_lieu_dien_bien": "Hình dung cách một tình huống có thể phát triển theo thời gian từ các dấu hiệu hiện có.",
        "nhan_dien_rui_ro": "Phát hiện khả năng xảy ra kết quả bất lợi và các điểm dễ làm kế hoạch thất bại.",
        "lap_phuong_an_du_phong": "Chuẩn bị trước phương án thay thế hoặc biện pháp giảm thiệt hại khi kế hoạch chính gặp sự cố.",
        "tu_duy_kich_ban": "Xây dựng nhiều kịch bản tương lai có điều kiện khác nhau để chuẩn bị cách phản ứng tương ứng.",
        "phan_doan_tinh_huong": "Đọc đúng trạng thái hiện tại của tình huống và nhận định điều gì đang thực sự diễn ra.",
        "can_nhac_loi_hai": "So sánh mặt lợi và mặt hại của một lựa chọn trước khi quyết định.",
        "danh_gia_trade_off": "Nhận ra thứ phải hy sinh để đổi lấy thứ khác và đánh giá mức đánh đổi có chấp nhận được hay không.",
        "xac_dinh_uu_tien": "Xác định điều gì quan trọng hoặc cấp thiết hơn khi nhiều mục tiêu cùng cạnh tranh.",
        "danh_gia_thoi_diem": "Nhận biết lúc nào nên hành động, chờ đợi, tăng tốc hoặc rút lui để đạt hiệu quả tốt hơn.",
        "dua_ra_quyet_dinh": "Đi đến một lựa chọn rõ ràng sau khi đã cân nhắc thông tin và phương án.",
        "quyet_doan": "Ra quyết định dứt khoát và không kéo dài do dự khi đã đủ cơ sở cần thiết.",
        "quyet_dinh_trong_bat_dinh": "Vẫn lựa chọn hợp lý khi kết quả, xác suất hoặc hoàn cảnh tương lai còn nhiều bất định.",
        "chot_khi_thong_tin_chua_day_du": "Biết ngừng thu thập thêm dữ liệu và cam kết lựa chọn khi thông tin không thể đầy đủ hoàn toàn.",
        "chap_nhan_danh_doi": "Chấp nhận có chủ ý phần mất mát hoặc bất lợi cần thiết để đạt mục tiêu ưu tiên hơn.",
        "khoi_dong_hanh_dong": "Bắt tay vào việc thay vì mắc kẹt ở suy nghĩ, chuẩn bị hoặc trì hoãn.",
        "bien_y_tuong_thanh_hanh_dong": "Chuyển một ý tưởng hoặc ý định thành bước thực thi cụ thể trong thực tế.",
        "giai_quyet_cong_viec": "Đưa công việc qua các trở ngại thực tế để tạo ra kết quả cần thiết.",
        "hoan_thanh_cong_viec": "Theo việc đến điểm kết thúc và đóng được đầu việc thay vì để dang dở.",
        "duy_tri_tien_do": "Giữ công việc tiếp tục tiến về mục tiêu qua thời gian, kể cả khi gặp trì hoãn hoặc trở ngại.",
        "phan_ung_nhanh": "Rút ngắn thời gian từ lúc nhận tín hiệu đến lúc đưa ra phản ứng phù hợp.",
        "xu_ly_tinh_huong_bat_ngo": "Giải quyết sự cố hoặc thay đổi không được dự kiến trước mà không cần kế hoạch có sẵn.",
        "hanh_dong_trong_bat_dinh": "Vẫn có thể triển khai bước hành động hữu ích khi chưa biết chắc kết quả hoặc điều kiện tương lai.",
        "xu_ly_khung_hoang": "Ưu tiên, ổn định và xử lý tình huống nghiêm trọng khi thời gian, thông tin hoặc nguồn lực đều bị hạn chế.",
        "phat_sinh_y_tuong": "Tạo ra nhiều ý tưởng hoặc khả năng mới thay vì chỉ dùng phương án quen thuộc.",
        "tao_phuong_an_moi": "Thiết kế một phương án chưa có sẵn để đáp ứng mục tiêu hoặc ràng buộc cụ thể.",
        "tim_cach_giai_khac": "Tìm đường giải thay thế khi cách tiếp cận thông thường không hiệu quả hoặc bị bế tắc.",
        "ket_hop_y_tuong": "Ghép các ý tưởng, khái niệm hoặc phương pháp khác nhau thành một cách làm mới có ích.",
        "tai_dinh_khung_van_de": "Đổi cách đặt câu hỏi hoặc góc nhìn về vấn đề để mở ra hướng giải khác.",
        "cai_tien_cach_lam": "Nâng cấp một cách làm đang có để hiệu quả, đơn giản hoặc phù hợp hơn.",
        "thu_nghiem_phuong_an": "Sẵn sàng thử ở quy mô phù hợp để kiểm chứng một ý tưởng thay vì chỉ suy đoán.",
        "ung_bien": "Điều chỉnh tức thời cách xử lý theo diễn biến thực tế khi không thể bám hoàn toàn vào kế hoạch.",
        "thich_nghi_voi_hoan_canh": "Thay đổi cách làm hoặc kỳ vọng để vẫn hoạt động hiệu quả trong điều kiện mới.",
        "chuyen_huong_khi_can": "Đổi mục tiêu trung gian hoặc hướng tiếp cận khi bằng chứng cho thấy đường hiện tại không còn phù hợp.",
        "bo_cach_lam_khong_hieu_qua": "Dừng một phương pháp đã chứng tỏ không hiệu quả thay vì tiếp tục vì quán tính hoặc tiếc công.",
        "dieu_chinh_theo_feedback": "Sửa cách làm đang diễn ra dựa trên phản hồi hoặc kết quả quan sát được.",
        "tai_cau_truc": "Thiết kế lại cấu trúc của một cách làm, kế hoạch hoặc hệ thống khi chỉnh sửa nhỏ không còn đủ.",
        "hoat_dong_trong_moi_truong_bien_dong": "Duy trì hiệu quả khi bối cảnh, ưu tiên hoặc điều kiện thay đổi thường xuyên và khó dự báo.",
        "cau_truc_hoa": "Biến vấn đề hoặc thông tin rời rạc thành cấu trúc rõ ràng gồm phần, quan hệ và thứ tự.",
        "chia_muc_tieu_thanh_buoc": "Phân rã một mục tiêu lớn thành các bước nhỏ có thể thực hiện và kiểm soát.",
        "lap_ke_hoach_thuc_hien": "Xác định trước các bước, trình tự, nguồn lực và mốc cần thiết để đưa mục tiêu vào thực tế.",
        "sap_xep_uu_tien": "Sắp thứ tự thực thi các đầu việc theo mức quan trọng, cấp thiết và phụ thuộc.",
        "quan_ly_phu_thuoc": "Nhận diện và điều phối các việc phải xảy ra trước, sau hoặc phụ thuộc lẫn nhau.",
        "quan_ly_nhieu_dau_viec": "Theo dõi và xử lý đồng thời nhiều đầu việc mà không để mất kiểm soát hoặc bỏ quên việc quan trọng.",
        "phan_bo_nguon_luc": "Phân chia thời gian, người, tiền hoặc năng lực cho các mục tiêu theo mức cần thiết và ưu tiên.",
        "xay_dung_quy_trinh": "Thiết kế chuỗi bước lặp lại rõ ràng để công việc được thực hiện nhất quán và ít phụ thuộc vào ngẫu hứng.",
        "giu_trat_tu_trong_complexity": "Giữ được cấu trúc, thứ tự và khả năng kiểm soát khi hệ thống có nhiều phần và quan hệ chồng chéo.",
        "theo_doi_tien_do": "Quan sát trạng thái, mốc và độ lệch so với kế hoạch để biết công việc đang tiến triển ra sao.",
        "duy_tri_he_thong": "Giữ một hệ thống hoặc quy trình hoạt động ổn định qua thời gian bằng kiểm tra và bảo trì cần thiết.",
        "tai_to_chuc_he_thong": "Sắp xếp lại thành phần, vai trò hoặc luồng công việc của hệ thống để hoạt động tốt hơn.",
        "dieu_phoi_hoat_dong": "Đồng bộ người, việc và thời điểm để nhiều hoạt động riêng cùng phục vụ một mục tiêu chung.",
        "phan_cong": "Chia công việc cho các thành viên theo phạm vi và trách nhiệm phù hợp.",
        "giao_viec": "Truyền đạt một nhiệm vụ cho người khác với yêu cầu, kỳ vọng và quyền thực hiện đủ rõ.",
        "phan_quyen": "Trao quyền quyết định và mức tự chủ phù hợp thay vì giữ mọi quyết định ở một đầu mối.",
        "dien_dat_ro_rang": "Truyền đạt ý tưởng bằng ngôn ngữ dễ hiểu, ít mơ hồ và giảm khả năng bị hiểu sai.",
        "trinh_bay_co_cau_truc": "Sắp xếp nội dung theo trình tự và cấu trúc giúp người nghe theo dõi lập luận dễ dàng.",
        "giai_thich": "Làm cho người khác hiểu một khái niệm, cơ chế hoặc lý do bằng cách nối nó với điều họ có thể nắm bắt.",
        "lam_ro_van_de": "Gỡ mơ hồ bằng câu hỏi, định nghĩa hoặc diễn đạt lại để xác định chính xác điều đang được bàn tới.",
        "lap_luan_bang_loi": "Trình bày chuỗi lý do và bằng chứng bằng lời để bảo vệ hoặc giải thích một kết luận.",
        "tranh_bien": "Đối đáp trực tiếp với lập luận khác, chỉ ra điểm yếu và bảo vệ quan điểm của mình.",
        "thuyet_phuc": "Làm tăng khả năng người khác chấp nhận một quan điểm hoặc hành động thông qua lý lẽ và cách trình bày.",
        "tao_anh_huong_bang_ngon_ngu": "Dùng cách nói, framing và thông điệp để định hình cách người khác chú ý, cảm nhận hoặc hành động.",
        "dam_phan": "Tìm thỏa thuận giữa các bên có lợi ích khác nhau bằng trao đổi điều kiện, nhượng bộ và giới hạn.",
        "nhan_biet_phan_ung_nguoi_khac": "Nhận ra người khác đang đồng thuận, khó chịu, do dự hoặc thay đổi thái độ qua tín hiệu họ thể hiện.",
        "doc_dong_co_nguoi_khac": "Suy ra lợi ích, nhu cầu hoặc mục đích có khả năng đứng sau hành vi của người khác.",
        "dieu_chinh_cach_giao_tiep": "Thay đổi cách nói, mức chi tiết hoặc thái độ theo người nghe và phản ứng của họ.",
        "nhan_biet_bau_khong_khi_nhom": "Cảm nhận trạng thái chung của nhóm như căng thẳng, đồng thuận, chia rẽ, hứng thú hoặc dè dặt.",
        "hop_tac": "Làm việc cùng người khác theo hướng cùng đóng góp và cùng hướng tới kết quả chung.",
        "phoi_hop_nhom": "Ăn khớp hành động của bản thân với vai trò, nhịp làm việc và nhu cầu của các thành viên khác.",
        "chia_se_quyen_kiem_soat": "Chấp nhận để người khác cùng tham gia quyết định và ảnh hưởng đến cách công việc được tiến hành.",
        "tao_dong_thuan": "Thu hẹp khác biệt để nhóm đạt được mức thống nhất đủ cho quyết định hoặc hành động chung.",
        "giai_quyet_xung_dot": "Xử lý bất đồng giữa các bên để giảm đối đầu và tìm cách tiếp tục hợp tác hoặc phân định rõ ràng.",
        "dinh_huong_nhom": "Giúp nhóm hiểu mục tiêu, ưu tiên và hướng đi chung khi có nhiều khả năng hoặc sự mơ hồ.",
        "huy_dong_nguoi_khac": "Khiến người khác thực sự tham gia, đóng góp nguồn lực hoặc hành động cho một mục tiêu chung.",
        "tao_cam_ket": "Biến sự đồng ý ban đầu thành mức cam kết đủ rõ để người khác sẵn sàng theo đuổi trách nhiệm.",
        "duy_tri_dong_luc_tap_the": "Giữ năng lượng và ý chí hành động của nhóm qua thời gian, đặc biệt khi tiến độ chậm hoặc gặp khó.",
        "dung_ra_nhan_trach_nhiem": "Sẵn sàng đứng tên, chịu trách nhiệm và xử lý hậu quả khi một việc chung cần người gánh trách nhiệm.",
        "duy_tri_tap_trung": "Giữ sự chú ý vào nhiệm vụ quan trọng trong thời gian đủ dài dù có nhiễu hoặc cám dỗ chuyển việc.",
        "kien_tri": "Tiếp tục nỗ lực qua khó khăn, chậm kết quả hoặc thất bại tạm thời thay vì bỏ cuộc sớm.",
        "ky_luat_hanh_dong": "Thực hiện điều cần làm theo nguyên tắc hoặc cam kết dù động lực tức thời không cao.",
        "duy_tri_nhip_do": "Giữ mức độ làm việc tương đối đều và bền, tránh kiểu bùng lên rồi nhanh chóng hụt hơi.",
        "kiem_soat_xung_dong": "Không để thôi thúc tức thời dẫn thẳng thành hành động khi cần dừng lại để cân nhắc.",
        "tu_dieu_chinh": "Theo dõi trạng thái và hành vi của bản thân rồi chủ động điều chỉnh để phù hợp mục tiêu hoặc hoàn cảnh.",
        "kiem_soat_phan_ung_cam_xuc": "Giữ cảm xúc mạnh không chi phối quá mức lời nói, quyết định hoặc hành động.",
        "biet_dung_khi_can": "Nhận ra lúc tiếp tục không còn hợp lý và có thể chủ động dừng một hành động, kế hoạch hoặc cuộc theo đuổi.",
        "biet_buong_mot_van_de": "Ngừng bám giữ về mặt tâm trí hoặc hành vi vào một vấn đề đã qua hay không còn đáng đầu tư.",
        "giu_chuc_nang_duoi_ap_luc": "Vẫn suy nghĩ, quyết định và thực hiện công việc ở mức hữu dụng khi chịu áp lực cao.",
        "chiu_dung_bat_dinh": "Chấp nhận trạng thái chưa rõ ràng trong một thời gian mà không vội phản ứng chỉ để xóa cảm giác bất an.",
        "binh_tinh_trong_khung_hoang": "Giữ được độ ổn định cảm xúc và đầu óc đủ sáng khi tình huống trở nên nghiêm trọng hoặc hỗn loạn.",
        "khoi_phuc_quyen_chu_dong": "Sau khi bị động hoặc mất kiểm soát, nhanh chóng xác định phần mình còn tác động được và bắt đầu hành động.",
        "phuc_hoi_sau_kho_khan": "Trở lại trạng thái hoạt động và tinh thần hữu dụng sau giai đoạn căng thẳng, tổn thất hoặc trở ngại.",
        "tai_tham_gia_sau_that_bai": "Quay lại thử, làm việc hoặc cạnh tranh sau một thất bại thay vì né tránh lâu dài.",
        "rut_kinh_nghiem_sau_that_bai": "Phân tích thất bại để rút ra bài học cụ thể có thể dùng cho quyết định và hành động sau này.",
        "dieu_chinh_sau_feedback": "Tiếp nhận phản hồi về bản thân hoặc kết quả đã có rồi thay đổi thói quen, chiến lược hoặc hành vi cho lần sau.",
    }
)


@dataclass(frozen=True, slots=True)
class CapabilityDefinition:
    id: str
    label: str
    description: str
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
            description=CAPABILITY_DESCRIPTIONS[capability_id],
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
    """Render capability meanings for selection, never astrology mappings."""
    lines = [
        "## Danh mục năng lực (ontology vocabulary)",
        f"Phiên bản: {CAPABILITY_ONTOLOGY_VERSION}.",
        (
            "Chỉ dùng các ID dưới đây để gọi tên kết luận. Danh mục chỉ định nghĩa "
            "ý nghĩa của năng lực; nó không chứa mapping từ sao/cách cục/cung sang "
            "năng lực."
        ),
        "",
        "### Nguyên tắc chọn năng lực",
        (
            "- Đọc phần mô tả để xác định năng lực nào khớp trực tiếp với ý nghĩa "
            "của evidence; không chọn chỉ vì label nghe gần giống."
        ),
        (
            "- Ưu tiên năng lực cụ thể nhất có đủ bằng chứng. Không chọn đồng thời "
            "nhiều năng lực gần nghĩa nếu chúng chỉ diễn đạt cùng một tín hiệu."
        ),
        (
            "- Phân biệt năng lực với mức độ: cùng một capability ID có thể là "
            "điểm mạnh hoặc điểm yếu tùy chiều của evidence."
        ),
        (
            "- Nếu evidence chỉ hỗ trợ một khái niệm rộng, chọn capability rộng "
            "phù hợp; không tự suy diễn sang capability hẹp hơn."
        ),
        (
            "- Ontology này là vocabulary của kết luận, không phải luật Tử Vi. "
            "Việc sao/cách cục/cung nào tạo evidence phải đến từ logic hoặc tool khác."
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
            lines.append(
                f"  - `{definition.id}` — {definition.label}: {definition.description}"
            )
    return "\n".join(lines)


__all__ = [
    "CAPABILITY_BY_ID",
    "CAPABILITY_DEFINITIONS",
    "CAPABILITY_DESCRIPTIONS",
    "CAPABILITY_ONTOLOGY_VERSION",
    "CapabilityDefinition",
    "CapabilityGroup",
    "build_capability_ontology_instruction",
    "get_capability_definition",
]
