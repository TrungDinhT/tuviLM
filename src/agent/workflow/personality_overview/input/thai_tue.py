"""Overview-only hypotheses from the user's research, not book quotations.

The shared Thái Tuế tool is used only to identify the natal star at Mệnh.
Its traditional interpretations and technical support never enter this payload.
"""

from pydantic import BaseModel, ConfigDict

from src.agent.tool.thai_tue import build_vong_thai_tue_payload
from src.refactored.la_so import LaSo


class ThaiTueGroupMeaning(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    name: str
    overview: str
    tension: str


class ThaiTueStarMeaning(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    group_id: str
    expression: str
    reading_hint: str = ""


class ThaiTueEvidence(BaseModel):
    source: str = "Nghiên cứu do người dùng cung cấp; giả thuyết cho personality_overview"
    star_id: str
    star_name: str
    group_meaning: ThaiTueGroupMeaning
    star_meaning: ThaiTueStarMeaning


THAI_TUE_GROUP_MEANINGS = {
    "trach_nhiem": ThaiTueGroupMeaning(
        id="trach_nhiem",
        name="Thái Tuế – Quan Phù – Bạch Hổ",
        overview=(
            "Có xu hướng chủ động can dự vào việc mình xem là cần làm, có lập trường "
            "và nhận trách nhiệm với kết quả. Trọng tâm là cảm giác mình có vai trò "
            "và nên hành động từ vai trò đó, không phải luôn đúng về đạo đức."
        ),
        tension=(
            "Cảm giác cần đứng ra và chịu trách nhiệm có thể khiến nhận quá nhiều "
            "việc về mình hoặc khó để việc diễn ra ngoài sự can dự của mình."
        ),
    ),
    "chenh_lech_hien_trang": ThaiTueGroupMeaning(
        id="chenh_lech_hien_trang",
        name="Tang Môn – Tuế Phá – Điếu Khách",
        overview=(
            "Có xu hướng chú ý đến khoảng cách giữa hiện trạng và điều mình cho "
            "là hợp lý hơn. Khoảng cách đó thúc đẩy nhu cầu xem xét hoặc phản ứng, "
            "không đồng nghĩa luôn bất mãn hay nhận định của mình luôn đúng."
        ),
        tension=(
            "Sự chú ý vào phần chưa ổn có thể khiến khó ghi nhận điều đã đủ tốt "
            "hoặc khó hài lòng với hiện trạng."
        ),
    ),
    "kha_nang_khac": ThaiTueGroupMeaning(
        id="kha_nang_khac",
        name="Thiếu Dương – Tử Phù – Phúc Đức",
        overview=(
            "Có xu hướng tìm thấy khả năng, mối liên hệ hoặc cách tiếp cận khác "
            "và cân nhắc cách sử dụng điều mình nhận ra. Đây là khuynh hướng chú ý "
            "và xử lý, không phải khẳng định thông minh hơn người khác."
        ),
        tension=(
            "Chú ý nhiều khả năng có thể khiến khó chọn một hướng hoặc bỏ qua "
            "giới hạn thực tế khi bị cuốn theo một cách đi có vẻ hứa hẹn."
        ),
    ),
    "thich_nghi": ThaiTueGroupMeaning(
        id="thich_nghi",
        name="Thiếu Âm – Long Đức – Trực Phù",
        overview=(
            "Có xu hướng tiếp nhận con người và hoàn cảnh, điều chỉnh mình để "
            "duy trì quan hệ hoặc cân bằng hơn là ép hoàn cảnh vận hành theo mình. "
            "Không mặc định yếu đuối, cam chịu hay bị đời bạc đãi."
        ),
        tension=(
            "Điều chỉnh theo hoàn cảnh quá nhiều có thể khiến nhu cầu và ranh "
            "giới của bản thân bị đặt xuống thấp."
        ),
    ),
}


THAI_TUE_STAR_MEANINGS = {
    "thai_tue": ThaiTueStarMeaning(
        id="thai_tue", group_id="trach_nhiem",
        expression=(
            "Thường xác lập quan điểm tương đối rõ và cảm thấy mình nên đứng ra "
            "hoặc nhận trách nhiệm; có thể quá chắc rằng cách nhìn của mình đúng."
        ),
        reading_hint="Có lập trường không đồng nghĩa đúng hơn người khác hoặc có năng lực lãnh đạo.",
    ),
    "quan_phuf": ThaiTueStarMeaning(
        id="quan_phuf", group_id="trach_nhiem",
        expression=(
            "Thường suy xét cách làm, logic, quy tắc và hệ quả trước khi hành động; "
            "mong muốn làm cho thỏa đáng có thể kéo dài thời gian cân nhắc."
        ),
        reading_hint="Chú ý nhu cầu làm cho hợp lý; chậm hành động không tự nó là né trách nhiệm.",
    ),
    "bach_ho": ThaiTueStarMeaning(
        id="bach_ho", group_id="trach_nhiem",
        expression=(
            "Khi đã xác định mục tiêu, có xu hướng dồn sức thực hiện và theo việc "
            "đến cùng; sự cam kết đó có thể khiến khó nhận ra lúc nên dừng."
        ),
        reading_hint="Theo việc đến cùng là khuynh hướng hành động, không bảo đảm hoàn thành hoặc thành công.",
    ),
    "tue_pha": ThaiTueStarMeaning(
        id="tue_pha", group_id="chenh_lech_hien_trang",
        expression=(
            "Có xu hướng trực tiếp phản biện, sửa đổi hoặc tác động vào điều thấy "
            "chưa hợp lý; đôi khi phản ứng trước khi tìm hiểu đủ vấn đề."
        ),
        reading_hint="Đọc cách tác động vào vấn đề, không mặc định chống đối trong mọi hoàn cảnh.",
    ),
    "dieu_khach": ThaiTueStarMeaning(
        id="dieu_khach", group_id="chenh_lech_hien_trang",
        expression=(
            "Thường xử lý bất đồng bằng phân tích, giải thích, tranh luận hoặc "
            "thuyết phục; nhu cầu nói rõ có thể khiến tranh luận kéo dài."
        ),
        reading_hint="Dùng lời để xử lý bất đồng không đồng nghĩa nói giỏi hoặc thuyết phục thành công.",
    ),
    "tang_mon": ThaiTueStarMeaning(
        id="tang_mon", group_id="chenh_lech_hien_trang",
        expression=(
            "Thường mang vấn đề vào suy nghĩ, dự liệu diễn biến và cân nhắc hệ quả "
            "trước khi phản ứng; dự liệu có thể kéo dài thành lo xa hoặc mắc kẹt trong suy nghĩ."
        ),
        reading_hint="Ít thể hiện bất đồng ra ngoài không có nghĩa đã đồng ý hoặc không quan tâm.",
    ),
    "thieu_duong": ThaiTueStarMeaning(
        id="thieu_duong", group_id="kha_nang_khac",
        expression=(
            "Có xu hướng nhanh chú ý đến điểm mấu chốt, khả năng hoặc phương án "
            "mới; có thể quá tin vào phán đoán ban đầu."
        ),
        reading_hint="Phản xạ nhận ra phương án không bảo đảm phương án đúng hoặc khả thi.",
    ),
    "tu_phu": ThaiTueStarMeaning(
        id="tu_phu", group_id="kha_nang_khac",
        expression=(
            "Có thể nhận ra vấn đề hoặc hướng đi nhưng còn khoảng cách giữa điều "
            "nhìn thấy và bước thực hiện; dễ vướng ở việc chuyển nhận thức thành hành động."
        ),
        reading_hint=(
            "Đây là giả thuyết nhận thức–thực hiện từ nghiên cứu, không phải bản dịch "
            "tương đương của nhận định truyền thống về thiệt thòi; không suy ra thiếu năng lực."
        ),
    ),
    "sao_phuc_duc": ThaiTueStarMeaning(
        id="sao_phuc_duc", group_id="kha_nang_khac",
        expression=(
            "Thường cân nhắc hậu quả, giới hạn hoặc giá trị trước khi tận dụng "
            "điều mình nhận ra; tự điều tiết quá mức có thể khiến chậm lựa chọn."
        ),
        reading_hint="Cân nhắc giá trị không mặc định đức độ hơn hoặc luôn được người khác yêu mến.",
    ),
    "thieu_am": ThaiTueStarMeaning(
        id="thieu_am", group_id="thich_nghi",
        expression=(
            "Có xu hướng hiểu và tiếp nhận tín hiệu từ người khác trước khi phản "
            "ứng, ít mặc định đối đầu; sự cởi mở có thể thành quá dễ tin."
        ),
        reading_hint="Giữ tiếp nhận làm lõi; không mặc định cả tin hoặc không có lập trường.",
    ),
    "long_duc": ThaiTueStarMeaning(
        id="long_duc", group_id="thich_nghi",
        expression=(
            "Có xu hướng giữ hòa khí, quan hệ hoặc nguyên tắc cá nhân hơn là cố "
            "thắng; ưu tiên hòa hợp có thể thành né tránh xung đột cần thiết."
        ),
        reading_hint="Không tranh phần thắng có thể là lựa chọn, không chứng minh yếu thế.",
    ),
    "truc_phu": ThaiTueStarMeaning(
        id="truc_phu", group_id="thich_nghi",
        expression=(
            "Thường chú ý làm phần việc của mình và đóng góp thực tế, ít chủ động "
            "đòi vị trí hoặc ghi nhận; nhu cầu cá nhân có thể không được nói rõ."
        ),
        reading_hint="Ít đòi ghi nhận không chứng minh đóng góp nhiều hơn hoặc bị người khác hưởng thành quả.",
    ),
}


def build_overview_thai_tue(la_so: LaSo) -> ThaiTueEvidence:
    star = build_vong_thai_tue_payload(la_so)["menh"]["thai_tue_star"]
    meaning = THAI_TUE_STAR_MEANINGS[star["id"]]
    return ThaiTueEvidence(
        star_id=star["id"],
        star_name=star["name"],
        group_meaning=THAI_TUE_GROUP_MEANINGS[meaning.group_id],
        star_meaning=meaning,
    )
