from __future__ import annotations

from dataclasses import dataclass

from src.refactored.model.elementary import NguHanh
from src.refactored.model.menh_cuc_relation import MenhCucRelationType


@dataclass(frozen=True)
class BanMenhMeaning:
    name: str
    symbol: str
    keywords: tuple[str, ...]
    nature: str
    reading_hint: str
    aliases: tuple[str, ...] = ()

    def as_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "symbol": self.symbol,
            "keywords": list(self.keywords),
            "nature": self.nature,
            "reading_hint": self.reading_hint,
        }
        if self.aliases:
            payload["aliases"] = list(self.aliases)
        return payload


def _meaning(
    name: str,
    symbol: str,
    keywords: tuple[str, ...],
    nature: str,
    reading_hint: str,
    ngu_hanh: NguHanh,
    aliases: tuple[str, ...] = (),
) -> BanMenhMeaning:
    return BanMenhMeaning(
        name=name,
        symbol=symbol,
        keywords=keywords,
        nature=nature,
        reading_hint=reading_hint,
        aliases=aliases,
    )


BAN_MENH_MEANINGS: dict[str, BanMenhMeaning] = {
    "hai_trung_kim": _meaning(
        name="Hải Trung Kim",
        symbol="Vàng dưới biển",
        keywords=("ẩn tàng", "tiềm năng", "khó lộ", "chờ khai phá"),
        nature=(
            "Kim khí bị che giấu trong môi trường biển rộng: có giá trị và nội "
            "lực, nhưng không dễ hiện ra ngay."
        ),
        reading_hint=(
            "Khi luận Bản Mệnh, ưu tiên khả năng tích lũy kín, cần duyên hoặc "
            "đúng môi trường mới phát lộ rõ."
        ),
        ngu_hanh=NguHanh.KIM,
    ),
    "kim_bach_kim": _meaning(
        name="Kim Bạch Kim",
        symbol="Vàng pha bạc",
        keywords=("tinh luyện", "mỏng dẻo", "trang sức", "thể diện"),
        nature=(
            "Kim đã qua rèn luyện thành lớp mỏng, đẹp ở bề mặt và có độ dẻo "
            "chịu, nhưng dễ nghiêng về hình thức."
        ),
        reading_hint=(
            "Đọc theo hướng bản lĩnh đã được mài giũa, hợp việc cần hình ảnh, "
            "chuẩn mực và khả năng làm tăng giá trị bên ngoài."
        ),
        ngu_hanh=NguHanh.KIM,
    ),
    "bach_lap_kim": _meaning(
        name="Bạch Lạp Kim",
        symbol="Vàng chân đèn",
        keywords=("sơ luyện", "thuần chất", "cần rèn", "tiềm lực"),
        nature=(
            "Kim vừa thành sơ chất, còn mềm và chưa thật cứng rắn; điểm mạnh là "
            "độ tinh thuần và khả năng được tinh luyện thêm."
        ),
        reading_hint=(
            "Khi luận, xem đây là nền Kim cần được tôi luyện bằng hoàn cảnh, kỷ "
            "luật và trải nghiệm để thành dụng."
        ),
        ngu_hanh=NguHanh.KIM,
    ),
    "sa_trung_kim": _meaning(
        name="Sa Trung Kim",
        symbol="Vàng trong cát",
        keywords=("ẩn trong cát", "phân tán", "khiêm tốn", "cần đãi lọc"),
        nature=(
            "Kim quý nhưng lẫn trong cát, khí chất không ổn định, dễ tản mạn "
            "nếu thiếu quá trình chọn lọc."
        ),
        reading_hint=(
            "Ưu tiên luận khả năng tìm ra giá trị thật trong môi trường pha "
            "tạp; cần tụ lực và giảm tư duy vụn vặt."
        ),
        ngu_hanh=NguHanh.KIM,
    ),
    "kiem_phong_kim": _meaning(
        name="Kiếm Phong Kim",
        symbol="Vàng mũi kiếm",
        keywords=("sắc bén", "quyết đoán", "tranh biện", "khí thế mạnh"),
        nature=(
            "Kim khí thịnh và lộ phong: mạnh, bén, có sức cắt gọt và tạo ảnh "
            "hưởng trực tiếp."
        ),
        reading_hint=(
            "Khi luận, dùng như nền quyết đoán và năng lực cạnh tranh; cần xét "
            "các sao tiết chế để tránh quá cứng hoặc quá hiếu thắng."
        ),
        ngu_hanh=NguHanh.KIM,
    ),
    "thoa_xuyen_kim": _meaning(
        name="Thoa Xuyến Kim",
        symbol="Vàng trang sức",
        keywords=("thanh tú", "trang nhã", "ẩn lực", "kiên cường"),
        nature=(
            "Kim đã biến thành trang sức: bề ngoài mềm đẹp, khí chất thanh, "
            "nhưng bên trong vẫn giữ độ bền của Kim."
        ),
        reading_hint=(
            "Đọc theo hướng duyên dáng, có sức hút và biết giữ giá trị; nội lực "
            "thường không bộc lộ theo kiểu thô cứng."
        ),
        ngu_hanh=NguHanh.KIM,
    ),
    "tang_do_moc": _meaning(
        name="Tang Đố Mộc",
        symbol="Cây dâu tằm",
        keywords=("hữu dụng", "thực tế", "đa tài", "nuôi dưỡng"),
        nature=(
            "Mộc gắn với cây dâu, có tính sinh kế và công dụng rõ: lá, vỏ, thân "
            "đều có thể tạo giá trị."
        ),
        reading_hint=(
            "Khi luận, ưu tiên tính thực dụng, chăm chỉ, đa năng và khả năng "
            "nuôi dưỡng người hoặc việc quanh mình."
        ),
        ngu_hanh=NguHanh.MOC,
    ),
    "tung_bach_moc": _meaning(
        name="Tùng Bách Mộc",
        symbol="Cây tùng già",
        keywords=("bền bỉ", "khí tiết", "chịu nghịch cảnh", "vững chãi"),
        nature=(
            "Mộc vượng ở phương chính, hình tượng cây tùng bách sống được trong "
            "hoàn cảnh xấu và càng khó càng lộ độ bền."
        ),
        reading_hint=(
            "Đọc như nền nguyên tắc, chịu áp lực và giữ khí tiết; rất cần xem "
            "cách cục có cho phép thành trụ cột hay thành cố chấp."
        ),
        ngu_hanh=NguHanh.MOC,
    ),
    "dai_lam_moc": _meaning(
        name="Đại Lâm Mộc",
        symbol="Cây rừng lớn",
        keywords=("rừng lớn", "sinh trưởng", "che chở", "quy mô"),
        nature=(
            "Mộc ở dạng rừng lớn, thiên về sức sống rộng, khả năng bao phủ và "
            "phát triển thành hệ sinh thái."
        ),
        reading_hint=(
            "Khi luận, chú ý năng lực phát triển theo tập thể, xây môi trường "
            "và che chở, hơn là chỉ thành tựu đơn độc."
        ),
        ngu_hanh=NguHanh.MOC,
    ),
    "duong_lieu_moc": _meaning(
        name="Dương Liễu Mộc",
        symbol="Cây dương liễu",
        keywords=("mềm dẻo", "nhạy cảm", "dễ lay động", "bền dai"),
        nature=(
            "Mộc mềm, cành rủ và dễ động theo gió; bề ngoài yếu nhưng vẫn có "
            "độ sống dai và khả năng thích nghi."
        ),
        reading_hint=(
            "Đọc theo hướng mềm mại, linh hoạt, giàu cảm nhận; cần xét thêm sao "
            "để biết là thích nghi khéo hay thiếu lập trường."
        ),
        ngu_hanh=NguHanh.MOC,
    ),
    "thach_luu_moc": _meaning(
        name="Thạch Lựu Mộc",
        symbol="Cây thạch lựu",
        keywords=("kiên cường", "chịu nghịch cảnh", "cứng rắn", "kết quả"),
        nature=(
            "Mộc có khả năng sống trong thời tiết khắc nghiệt, thân chắc và "
            "sức chịu đựng cao."
        ),
        reading_hint=(
            "Khi luận, ưu tiên khả năng bền trong nghịch cảnh, có thành quả rõ "
            "sau va đập; mặt trái là dễ cứng hoặc thô."
        ),
        ngu_hanh=NguHanh.MOC,
    ),
    "binh_dia_moc": _meaning(
        name="Bình Địa Mộc",
        symbol="Cây đồng bằng",
        keywords=("mầm non", "ôn hòa", "cần nuôi dưỡng", "tránh biến động"),
        nature=(
            "Mộc mới đâm chồi ở bình địa, thích mưa nhỏ và môi trường bao bọc, "
            "không hợp phong ba quá mạnh."
        ),
        reading_hint=(
            "Đọc như nền phát triển cần dưỡng đều, hợp tăng trưởng ổn định; "
            "biến động quá mạnh dễ làm lệch nhịp."
        ),
        ngu_hanh=NguHanh.MOC,
    ),
    "gian_ha_thuy": _meaning(
        name="Giản Hạ Thủy",
        symbol="Nước khe suối",
        keywords=("thanh tịnh", "linh hoạt", "khó dò", "tích tiểu thành đại"),
        nature=(
            "Thủy ở khe hẹp, tụ từ dòng nhỏ; trong trẻo, chuyển hướng bất định "
            "và khó thấy hết nông sâu."
        ),
        reading_hint=(
            "Khi luận, chú ý khả năng gom việc nhỏ thành dòng lớn, trực giác "
            "tốt nhưng hướng đi cần được định rõ."
        ),
        ngu_hanh=NguHanh.THUY,
    ),
    "dai_khe_thuy": _meaning(
        name="Đại Khê Thủy",
        symbol="Nước suối lớn",
        keywords=("mạnh dòng", "biến hóa", "hướng biển", "thực tế"),
        nature=(
            "Thủy ở khe lớn miền núi, dòng mạnh và luôn tìm đường chảy về nơi "
            "rộng hơn."
        ),
        reading_hint=(
            "Đọc theo hướng hành động linh hoạt, sức đẩy mạnh, có khả năng đổi "
            "hướng theo địa thế để đạt mục tiêu."
        ),
        ngu_hanh=NguHanh.THUY,
    ),
    "truong_luu_thuy": _meaning(
        name="Trường Lưu Thủy",
        symbol="Nước sông dài",
        keywords=("liên tục", "bền dòng", "rộng đường", "dễ thỏa mãn"),
        nature=(
            "Thủy ở dòng sông dài, có tính tiếp nối, chảy đều và ít giấu kín "
            "tham vọng bên trong."
        ),
        reading_hint=(
            "Khi luận, ưu tiên năng lực đi đường dài, duy trì nhịp bền; cần xem "
            "thêm cách cục để tránh tâm lý dễ tự đủ."
        ),
        ngu_hanh=NguHanh.THUY,
    ),
    "thien_ha_thuy": _meaning(
        name="Thiên Hà Thủy",
        symbol="Nước trên trời",
        keywords=("ban phát", "nuôi dưỡng", "lan tỏa", "khó đoán"),
        nature=(
            "Thủy ở trời cao như mưa, lan rộng và nuôi dưỡng nhiều nơi, nhưng "
            "cũng có mặt lạnh và khó lường."
        ),
        reading_hint=(
            "Đọc theo hướng có khả năng giúp rộng, ảnh hưởng lan xa; cần xét "
            "tính ổn định vì khí Thủy này biến hóa theo thời."
        ),
        ngu_hanh=NguHanh.THUY,
    ),
    "tuyen_trung_thuy": _meaning(
        name="Tỉnh Tuyền Thủy",
        symbol="Nước trong giếng",
        keywords=("trầm tĩnh", "sâu kín", "bền nguồn", "nuôi dưỡng"),
        nature=(
            "Thủy ở giếng sâu, nguồn kín mà đều, ít phô trương nhưng có khả "
            "năng duy trì và cấp dưỡng."
        ),
        reading_hint=(
            "Khi luận, chú ý chiều sâu kín đáo, khả năng tích trữ tri thức hoặc "
            "nguồn lực; người ngoài khó đọc hết."
        ),
        ngu_hanh=NguHanh.THUY,
        aliases=("Tuyền Trung Thủy",),
    ),
    "dai_hai_thuy": _meaning(
        name="Đại Hải Thủy",
        symbol="Nước biển lớn",
        keywords=("bao dung", "hùng vĩ", "dung nạp", "sóng lớn"),
        nature=(
            "Thủy ở biển lớn, dung nạp nhiều dòng, độ chứa rộng và sức mạnh có "
            "thể nâng đỡ hoặc cuốn chìm."
        ),
        reading_hint=(
            "Đọc như nền rộng lượng, tầm nhìn lớn và sức chứa cao; cần xem sao "
            "để biết thành bao dung hay thành quá tràn."
        ),
        ngu_hanh=NguHanh.THUY,
    ),
    "tich_lich_hoa": _meaning(
        name="Tích Lịch Hỏa",
        symbol="Lửa sấm sét",
        keywords=("bộc phát", "tốc độ", "uy lực", "mau nguội"),
        nature=(
            "Hỏa phát như sấm chớp, nhanh, mạnh và biến hóa đột ngột; khí đến "
            "nhanh rồi cũng dễ qua nhanh."
        ),
        reading_hint=(
            "Khi luận, chú ý năng lực tạo biến cố, ra quyết định nhanh và phát "
            "tiết mạnh; cần kênh ổn định để tránh nóng lạnh thất thường."
        ),
        ngu_hanh=NguHanh.HOA,
    ),
    "lo_trung_hoa": _meaning(
        name="Lư Trung Hỏa",
        symbol="Lửa trong lò",
        keywords=("bền nhiệt", "tích lũy", "kế hoạch", "cần nhiên liệu"),
        nature=(
            "Hỏa trong lò không bùng một lần, mà mạnh dần nhờ nhiên liệu đều "
            "và khả năng giữ nhiệt."
        ),
        reading_hint=(
            "Đọc như nền kiên trì, biết tích lũy kinh nghiệm và làm việc theo "
            "quy trình; cần nguồn lực liên tục."
        ),
        ngu_hanh=NguHanh.HOA,
        aliases=("Lộ Trung Hỏa",),
    ),
    "phu_dang_hoa": _meaning(
        name="Phúc Đăng Hỏa",
        symbol="Lửa đèn chụp",
        keywords=("soi sáng", "âm thầm", "hy sinh", "dẫn đường"),
        nature=(
            "Hỏa của đèn nhỏ, ánh sáng không rực đại chúng nhưng có giá trị "
            "soi đường trong tối."
        ),
        reading_hint=(
            "Khi luận, ưu tiên khả năng phục vụ, chỉ dẫn và làm sáng việc kín; "
            "sức mạnh nằm ở sự bền bỉ hơn là phô trương."
        ),
        ngu_hanh=NguHanh.HOA,
        aliases=("Phú Đăng Hỏa",),
    ),
    "thien_thuong_hoa": _meaning(
        name="Thiên Thượng Hỏa",
        symbol="Lửa trên trời",
        keywords=("quang minh", "công bằng", "hào sảng", "ban phát"),
        nature=(
            "Hỏa của trời cao như mặt trời, mặt trăng: sáng rộng, công khai, "
            "có khuynh hướng chiếu rọi và giúp nhiều người."
        ),
        reading_hint=(
            "Đọc theo hướng chính trực, rộng rãi, có trách nhiệm với cộng đồng; "
            "cần xét thêm sao để biết ánh sáng có thành quyền uy hay áp lực."
        ),
        ngu_hanh=NguHanh.HOA,
    ),
    "son_ha_hoa": _meaning(
        name="Sơn Hạ Hỏa",
        symbol="Lửa dưới núi",
        keywords=("ẩn sáng", "bảo vệ", "chủ quan", "cần tri ngộ"),
        nature=(
            "Hỏa ở dưới núi, sức sáng bị che một phần, không phô hết nhưng vẫn "
            "giữ nhiệt và tính bảo vệ."
        ),
        reading_hint=(
            "Khi luận, chú ý năng lực âm thầm và nhu cầu được nhận ra đúng; nếu "
            "bí bách dễ thành chủ quan hoặc bộc phát."
        ),
        ngu_hanh=NguHanh.HOA,
    ),
    "son_dau_hoa": _meaning(
        name="Sơn Đầu Hỏa",
        symbol="Lửa đầu núi",
        keywords=("rực xa", "hoang dã", "mạnh bùng", "dễ tàn"),
        nature=(
            "Hỏa trên đỉnh núi, có thể sáng xa và bùng mạnh, nhưng dạng lửa này "
            "cũng dễ biến mất nhanh."
        ),
        reading_hint=(
            "Đọc như năng lực tạo tín hiệu lớn, nổi bật khi đúng thời; cần nền "
            "bền để không chỉ sáng nhất thời."
        ),
        ngu_hanh=NguHanh.HOA,
    ),
    "lo_bang_tho": _meaning(
        name="Lộ Bàng Thổ",
        symbol="Đất đường lộ",
        keywords=("đường lộ", "lý thuyết", "thẳng cứng", "cần tưới"),
        nature=(
            "Thổ của đường đi, khô và cứng, có tính trải dài, tạo lối, nhưng cần "
            "Thủy để bớt khô và thành hữu dụng."
        ),
        reading_hint=(
            "Khi luận, chú ý năng lực lập đường, nghiên cứu, hệ thống hóa; mặt "
            "trái là cứng và thiếu mềm nếu không được bồi dưỡng."
        ),
        ngu_hanh=NguHanh.THO,
    ),
    "bich_thuong_tho": _meaning(
        name="Bích Thượng Thổ",
        symbol="Đất trên tường",
        keywords=("che chở", "kín đáo", "cần điểm tựa", "hình thức"),
        nature=(
            "Thổ của vách tường, kín và hướng nội; muốn vững phải có cột, vách "
            "hoặc cấu trúc để tựa."
        ),
        reading_hint=(
            "Đọc theo hướng bảo vệ, giữ ranh giới và cần hệ thống nâng đỡ; dễ "
            "thành phòng thủ hoặc nặng hình thức nếu thiếu nội lực."
        ),
        ngu_hanh=NguHanh.THO,
    ),
    "thanh_dau_tho": _meaning(
        name="Thành Đầu Thổ",
        symbol="Đất trên thành",
        keywords=("phòng thủ", "vững chắc", "cao vị", "tham vọng"),
        nature=(
            "Thổ của tường thành, cao và có chức năng ngăn chặn, bảo vệ; cũng "
            "gợi vị trí uy quyền và ý chí kiểm soát."
        ),
        reading_hint=(
            "Khi luận, ưu tiên tính ổn định, trung thành và năng lực phòng thủ; "
            "cần xét sao để biết là bảo hộ chính đáng hay quá muốn thống trị."
        ),
        ngu_hanh=NguHanh.THO,
    ),
    "sa_trung_tho": _meaning(
        name="Sa Trung Thổ",
        symbol="Đất trong cát",
        keywords=("rời rạc", "ẩn tàng", "thiếu kết dính", "cần nước"),
        nature=(
            "Thổ lẫn trong cát, sạch và có hình thế biến hóa, nhưng thiếu nước "
            "thì khó tụ và dễ tản."
        ),
        reading_hint=(
            "Đọc như nền biến động, có phần kín và phân tán; cần lực kết nối để "
            "thành nền chắc."
        ),
        ngu_hanh=NguHanh.THO,
    ),
    "dai_dich_tho": _meaning(
        name="Đại Trạch Thổ",
        symbol="Đất nền nhà",
        keywords=("rộng mở", "gánh vác", "chính trực", "nền tảng"),
        nature=(
            "Thổ ở nền đất rộng, khí lớn và phẳng, có sức chứa và khả năng gánh "
            "trách nhiệm."
        ),
        reading_hint=(
            "Khi luận, ưu tiên độ rộng, tính chính trực và vai trò làm nền cho "
            "việc lớn; cần xét sao để biết sức gánh có bền hay quá ôm đồm."
        ),
        ngu_hanh=NguHanh.THO,
        aliases=("Đại Dịch Thổ",),
    ),
    "oc_thuong_tho": _meaning(
        name="Ốc Thượng Thổ",
        symbol="Đất trên mái",
        keywords=("che chở", "hy sinh", "chịu mưa gió", "dễ vỡ"),
        nature=(
            "Thổ thành mái/ngói, đã qua Thủy và Hỏa để có chức năng che chắn, "
            "nhưng rơi vỡ thì khó nguyên vẹn."
        ),
        reading_hint=(
            "Đọc theo hướng bảo hộ, chịu đựng và hy sinh; cần xem thêm cách cục "
            "để tránh lệ thuộc hoặc chờ đợi quá nhiều."
        ),
        ngu_hanh=NguHanh.THO,
    ),
}


_RELATION_LENS: dict[MenhCucRelationType, dict[str, str]] = {
    MenhCucRelationType.SINH_XUAT: {
        "relation": "Mệnh sinh Cục",
        "meaning": (
            "Người phải tự mình nỗ lực, tiên phong hành động trước khi hoàn "
            "cảnh biến đổi theo ý mình."
        ),
    },
    MenhCucRelationType.SINH_NHAP: {
        "relation": "Cục sinh Mệnh",
        "meaning": "Người gặp nhiều may mắn, được hoàn cảnh hỗ trợ và ưu đãi.",
    },
    MenhCucRelationType.KHAC_XUAT: {
        "relation": "Mệnh khắc Cục",
        "meaning": (
            "Người có khả năng thay đổi, cải cách môi trường xung quanh mình."
        ),
    },
    MenhCucRelationType.KHAC_NHAP: {
        "relation": "Cục khắc Mệnh",
        "meaning": (
            "Hoàn cảnh gây khó khăn, cản trở hoặc buộc bản tính cá nhân phải "
            "thay đổi để thích nghi."
        ),
    },
    MenhCucRelationType.BINH_HOA: {
        "relation": "Mệnh Cục Bình Hòa",
        "meaning": "Mệnh và môi trường ngang hàng, ít có sự chi phối lẫn nhau.",
    },
}


def build_ban_menh_meaning(ban_menh_id: str) -> dict[str, object]:
    try:
        return BAN_MENH_MEANINGS[ban_menh_id].as_payload()
    except KeyError as exc:
        raise ValueError(f"Unknown Bản Mệnh id: {ban_menh_id}") from exc


def build_menh_cuc_lens(
    relation_type: MenhCucRelationType,
) -> dict[str, object]:
    relation_lens = _RELATION_LENS[relation_type]
    return {
        "relation": relation_lens["relation"],
        "meaning": relation_lens["meaning"],
    }
