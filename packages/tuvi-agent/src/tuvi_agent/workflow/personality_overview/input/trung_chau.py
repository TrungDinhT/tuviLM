"""Interpretation bases following Trung Châu, selected by stars and branch."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field
from pydantic_ai import ModelRetry

from tuvi_engine.model.elementary import DiaChi

if TYPE_CHECKING:
    from .evidence import PalaceEvidence


class InterpretationBasis(BaseModel):
    model_config = ConfigDict(frozen=True)

    chinh_tinh: frozenset[str] = Field(min_length=1)
    dia_chi: tuple[DiaChi, DiaChi]
    title: str
    axis_classical_vi: str
    axis_interpretation: str
    core_temperament: str
    personality_mechanism: str
    observable_hypothesis: str
    weakness: str


TRUNG_CHAU_STAR_SYSTEMS = (
    InterpretationBasis(
        chinh_tinh=frozenset({'tu_vi'}),
        dia_chi=(DiaChi.TY, DiaChi.NGO),
        title='Tử Vi độc tọa Tý/Ngọ',
        axis_classical_vi='Tinh thần ↔ Vật chất',
        axis_interpretation=(
            'Lựa chọn thường được dẫn dắt bởi danh dự, lý tưởng và giá trị bản thân, hoặc bởi thành'
            ' tựu, nguồn lực và kết quả hữu hình.'
        ),
        core_temperament=(
            'Tự trọng cao, thích làm chủ và tổ chức. Cần vị thế, sự công nhận và làm chủ trật tự; '
            'có khả năng tổ chức, nhìn xa và quy tụ người khác.'
        ),
        personality_mechanism=(
            'Tử Vi độc tọa đứng giữa nhu cầu xác lập một trọng tâm riêng và việc biến trọng tâm ấy '
            'thành trật tự có ích; Tham Lang đối cung đặt câu hỏi về sức hút của những khả năng bên'
            ' ngoài.'
        ),
        observable_hypothesis=(
            'Trong việc chung, có thể muốn xác định mục tiêu, sắp xếp vai trò và giữ quyền định '
            'hướng; mức chú trọng danh dự hay thành quả thực tế còn tùy cấu hình cụ thể.'
        ),
        weakness=(
            'Có thể dao động giữa lý tưởng cá nhân và thành tựu hữu hình; thiếu hỗ trợ dễ tự tôn, '
            'cô độc hoặc ôm đồm.'
        ),
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'pha_quan'}),
        dia_chi=(DiaChi.DAN, DiaChi.THAN),
        title='Phá Quân độc tọa Dần/Thân',
        axis_classical_vi='Phản nghịch ↔ Thuận tòng',
        axis_interpretation=(
            'Trước khuôn khổ gò bó, có xu hướng phá bỏ để mở lối riêng, hoặc thích nghi và thuận '
            'theo trật tự đang có.'
        ),
        core_temperament='Tinh thần cải cách: thích tháo gỡ cái cũ, tự thử đường mới và không chịu rập khuôn.',
        personality_mechanism=(
            'Phá Quân độc tọa có Vũ Khúc–Thiên Tướng đối cung: nhu cầu thay đổi liên hệ trực tiếp '
            'với thực tế nguồn lực và khả năng phối hợp.'
        ),
        observable_hypothesis=(
            'Khi thấy cách làm cũ bế tắc, có thể chủ động đề xuất thử hướng khác; cách thể hiện có '
            'thể từ đối thoại cải tiến đến phản ứng mạnh trước ràng buộc.'
        ),
        weakness=(
            'Dễ phản kháng chỉ để khẳng định mình, hoặc vì áp lực mà miễn cưỡng thuận theo rồi tích'
            ' tụ bất mãn.'
        ),
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'liem_trinh', 'thien_phu'}),
        dia_chi=(DiaChi.THIN, DiaChi.TUAT),
        title='Liêm Trinh – Thiên Phủ Thìn/Tuất',
        axis_classical_vi='Tình cảm ↔ Lý trí',
        axis_interpretation=(
            'Khi quyết định, đặt nặng tình nghĩa và cảm nhận cá nhân, hoặc ưu tiên lý lẽ, nguyên '
            'tắc và tính khả thi.'
        ),
        core_temperament=(
            'Trọng nguyên tắc, sự công bằng, muốn an toàn và kiểm soát nguồn lực. Hay phải cân bằng'
            ' giữa tình nghĩa, cảm xúc và lợi ích thực tế.'
        ),
        personality_mechanism=(
            'Liêm Trinh cùng Thiên Phủ tạo sự căng kéo giữa điều bản thân thấy cần giữ đúng và cách'
            ' quản trị những gì đang có.'
        ),
        observable_hypothesis=(
            'Trước lựa chọn quan trọng, có thể cân nhắc đồng thời sự đúng đắn, tình nghĩa và nguồn '
            'lực đang nắm giữ; thường muốn quyết định không làm tổn hại nền tảng lâu dài.'
        ),
        weakness='Dễ giằng co giữa tình nghĩa và tính toán; có thể kìm nén cảm xúc hoặc nể tình quá mức.',
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'thai_am'}),
        dia_chi=(DiaChi.TI, DiaChi.HOI),
        title='Thái Âm độc tọa Tỵ/Hợi',
        axis_classical_vi='Bộc lộ ↔ Thu liễm',
        axis_interpretation=(
            'Cảm nhận và suy nghĩ được đưa ra ngoài qua chia sẻ, sáng tạo, hành động, hoặc giữ lại '
            'để suy ngẫm và nuôi dưỡng bên trong.'
        ),
        core_temperament=(
            'Tinh tế, sâu sắc, giàu tưởng tượng; có nhu cầu nuôi dưỡng đời sống riêng và biến cảm '
            'nhận thành giá trị.'
        ),
        personality_mechanism=(
            'Thái Âm độc tọa đối Thiên Cơ: điều tiếp nhận từ bên trong có thể được chuyển thành '
            'phương án hành động hoặc tiếp tục ấp ủ.'
        ),
        observable_hypothesis=(
            'Có thể cần thời gian riêng để cảm nhận và hình dung nhiều khả năng trước khi chia sẻ '
            'hoặc hành động; cách bộc lộ tùy mức an tâm và bối cảnh.'
        ),
        weakness='Có thể quá kín đáo, suy nghĩ vòng vo; hoặc bộc lộ cảm xúc, kỳ vọng thiếu đúng lúc.',
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'tham_lang'}),
        dia_chi=(DiaChi.TY, DiaChi.NGO),
        title='Tham Lang độc tọa Tý/Ngọ',
        axis_classical_vi='Tích cực ↔ Tiêu cực',
        axis_interpretation=(
            'Chủ động theo đuổi trải nghiệm, ham muốn và cơ hội, hoặc dễ giảm nhiệt, bỏ dở khi động'
            ' lực và sức hút ban đầu suy yếu.'
        ),
        core_temperament=(
            'Ham trải nghiệm, giao tiếp, giỏi kết nối và phát hiện cơ hội; có động lực mở rộng đời '
            'sống và hưởng thụ.'
        ),
        personality_mechanism=(
            'Tham Lang độc tọa xung Tử Vi: sức hút của trải nghiệm và cơ hội liên hệ với nhu cầu '
            'chọn một định hướng có trọng tâm.'
        ),
        observable_hypothesis=(
            'Dễ nhận thấy cơ hội qua giao tiếp, trải nghiệm hoặc môi trường mới; có thể chủ động mở'
            ' rộng lựa chọn rồi tìm điều đáng tập trung theo đuổi.'
        ),
        weakness=(
            'Khi mất định hướng dễ chạy theo kích thích, vui trước mắt, chán nhanh hoặc giảm ý chí '
            'theo đuổi mục tiêu.'
        ),
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'thien_dong', 'cu_mon'}),
        dia_chi=(DiaChi.SUU, DiaChi.MUI),
        title='Thiên Đồng – Cự Môn Sửu/Mùi',
        axis_classical_vi='Sáng sủa ↔ U ám',
        axis_interpretation=(
            'Đối diện điều chưa ổn bằng cái nhìn cởi mở, muốn làm rõ để hòa hợp, hoặc dễ mắc vào '
            'nghi ngờ và phiền lòng.'
        ),
        core_temperament='Tính cách nhẹ nhàng, thích hòa khí, đầu óc sắc sảo và có nhu cầu được thấu hiểu.',
        personality_mechanism=(
            'Thiên Đồng–Cự Môn đặt nhu cầu dễ chịu, được hiểu và hòa hợp cạnh xu hướng phân tích '
            'điều chưa khớp; tam hợp có cung vô chính diệu nên có thể ít có nguồn hỗ trợ độc lập.'
        ),
        observable_hypothesis=(
            'Trong quan hệ và trao đổi, có thể vừa muốn không khí êm dịu vừa muốn những điều chưa '
            'rõ được nói ra; mức trực diện hay giữ lại tùy hoàn cảnh.'
        ),
        weakness=(
            'Dễ vừa muốn yên ổn vừa nghi ngờ người khác; suy diễn lời nói, mắc kẹt trong phiền '
            'lòng.'
        ),
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'vu_khuc', 'thien_tuong'}),
        dia_chi=(DiaChi.DAN, DiaChi.THAN),
        title='Vũ Khúc – Thiên Tướng Dần/Thân',
        axis_classical_vi='Quá cứng ↔ Quá mềm',
        axis_interpretation=(
            'Giữ tiêu chuẩn đến mức cứng nhắc, khó phối hợp, hoặc nhượng bộ quá nhiều để giữ hòa '
            'khí mà đánh mất lập trường.'
        ),
        core_temperament=(
            'Đáng tin cậy, thực tế, có trách nhiệm, biết bảo vệ nguyên tắc và hoàn thành trách '
            'nhiệm bằng hành động.'
        ),
        personality_mechanism=(
            'Vũ Khúc–Thiên Tướng kết hợp tính thực tế, kỷ luật với nhu cầu phân vai và duy trì hợp '
            'tác; Phá Quân đối cung đặt câu hỏi về giới hạn của hệ thống hiện tại.'
        ),
        observable_hypothesis=(
            'Khi cùng người khác thực hiện một việc, có thể chú ý tiêu chuẩn, trách nhiệm và sự '
            'phối hợp; thường tìm cách biến cam kết thành công việc cụ thể.'
        ),
        weakness=(
            'Dễ quá nghiêm khắc, khó cảm thông; hoặc quá nhường nhịn, ngại đối đầu nên mất tiếng '
            'nói riêng.'
        ),
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'thien_luong', 'thai_duong'}),
        dia_chi=(DiaChi.MEO, DiaChi.DAU),
        title='Thái Dương – Thiên Lương Mão/Dậu',
        axis_classical_vi='Ôn hòa ↔ Cô kỵ',
        axis_interpretation=(
            'Theo đuổi điều đúng bằng sự ôn hòa, sẵn lòng nâng đỡ, hoặc trở nên khắt khe, xa cách '
            'với người khác quan điểm.'
        ),
        core_temperament=(
            'Thiên về chính nghĩa, bảo trợ và dẫn dắt; muốn tạo lợi ích cho người khác theo chuẩn '
            'mực của mình.'
        ),
        personality_mechanism=(
            'Thái Dương–Thiên Lương cùng cung nối nhu cầu làm rõ, chia sẻ với vai trò bảo vệ những '
            'nguyên tắc có ích cho người khác.'
        ),
        observable_hypothesis=(
            'Có thể thiên về giải thích, hướng dẫn hoặc đứng ra bảo vệ điều mình coi là đúng; mức '
            'cởi mở với góc nhìn khác phụ thuộc nhiều yếu tố hội hợp.'
        ),
        weakness='Dễ biến chuẩn mực thành sự phán xét hoặc tự cô lập.',
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'that_sat'}),
        dia_chi=(DiaChi.THIN, DiaChi.TUAT),
        title='Thất Sát độc tọa Thìn/Tuất',
        axis_classical_vi='Lý tưởng ↔ Ảo tưởng',
        axis_interpretation=(
            'Theo đuổi mục tiêu lớn có căn cứ và lộ trình thực hiện, hoặc bị cuốn theo viễn cảnh '
            'hấp dẫn nhưng thiếu kiểm chứng.'
        ),
        core_temperament='Mạnh mẽ, độc lập, có  mục tiêu lớn và sẵn sàng chịu áp lực để mở đường.',
        personality_mechanism=(
            'Thất Sát độc tọa gặp Liêm Trinh–Thiên Phủ đối cung: động lực quyết định nhanh đối diện'
            ' câu hỏi về nguyên tắc và sức bền nguồn lực.'
        ),
        observable_hypothesis=(
            'Khi gặp mục tiêu khó, có thể muốn quyết nhanh, tự nhận phần trách nhiệm và tạo lối đi;'
            ' cách kiểm chứng tính khả thi có thể khác nhau.'
        ),
        weakness=(
            'Khi thiếu điểm tựa thực tế dễ đặt cược vào viễn cảnh lớn, nóng lòng chứng minh bản '
            'thân.'
        ),
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'thien_co'}),
        dia_chi=(DiaChi.TI, DiaChi.HOI),
        title='Thiên Cơ độc tọa Tỵ/Hợi',
        axis_classical_vi='Ứng biến ↔ Mưu tính',
        axis_interpretation=(
            'Linh hoạt thay cách làm theo tình huống, hoặc thiên về tính trước nhiều bước để giữ '
            'thế chủ động và phòng ngừa bất trắc.'
        ),
        core_temperament=(
            'Nhanh trí, linh hoạt, giỏi nhìn thấy nhiều phương án và thích giải quyết các vấn đề '
            'phức tạp.'
        ),
        personality_mechanism=(
            'Thiên Cơ độc tọa có Thái Âm đối cung và Thiên Đồng–Cự Môn ở tam hợp: khả năng đổi '
            'phương án gặp nhu cầu suy ngẫm và đặt câu hỏi.'
        ),
        observable_hypothesis=(
            'Trong tình huống nhiều biến số, có thể nhanh chóng tìm phương án thay thế hoặc lường '
            'trước các tình huống; việc chốt hướng hay tiếp tục xoay xở còn tùy điều kiện.'
        ),
        weakness=(
            'Dễ suy tính quá nhiều, đổi kế hoạch liên tục hoặc dùng sự khéo léo thay cho quyết định'
            ' dứt khoát.'
        ),
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'tu_vi', 'pha_quan'}),
        dia_chi=(DiaChi.SUU, DiaChi.MUI),
        title='Tử Vi – Phá Quân Sửu/Mùi',
        axis_classical_vi='Biến động ↔ Ổn định',
        axis_interpretation=(
            'Muốn cải tổ bằng thay đổi mạnh, chấp nhận xáo trộn, hoặc đổi mới có kiểm soát để giữ '
            'nhịp vận hành và nguồn lực.'
        ),
        core_temperament='Lãnh đạo cải cách, muốn phá bỏ hệ thống cũ để dựng một trật tự tốt hơn.',
        personality_mechanism=(
            'Tử Vi–Phá Quân đồng cung không phải hai tính cách quản trị và phá bỏ cộng lại: điểm '
            'chung là chủ động quyết định cấu trúc nào nên được xây lại; Thiên Tướng đối cung gợi '
            'giới hạn của thay đổi.'
        ),
        observable_hypothesis=(
            'Khi một cơ chế không còn phù hợp, có thể muốn chủ động xác định phần cần thay và thiết'
            ' lập cách vận hành mới; mức độ xáo trộn không mặc định.'
        ),
        weakness=(
            'Dễ độc đoán, nóng vội với người chậm thay đổi, tạo xáo trộn không cần thiết nếu thiếu '
            'khả năng điều phối.'
        ),
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'thien_phu'}),
        dia_chi=(DiaChi.MEO, DiaChi.DAU),
        title='Thiên Phủ độc tọa Mão/Dậu',
        axis_classical_vi='Lão luyện ↔ Thận trọng',
        axis_interpretation=(
            'Dùng kinh nghiệm để cân nhắc rồi quyết đúng lúc, hoặc quá chú trọng an toàn nên chậm '
            'nắm cơ hội.'
        ),
        core_temperament='Điềm tĩnh, giỏi tích lũy và quản lý nguồn lực, tư duy dài hạn và cân nhắc hậu quả.',
        personality_mechanism=(
            'Thiên Phủ độc tọa đối Vũ Khúc–Thất Sát: xu hướng giữ nền nguồn lực gặp một cực hành '
            'động và quyết đoán mạnh.'
        ),
        observable_hypothesis=(
            'Có thể ưu tiên chuẩn bị nguồn lực, đánh giá rủi ro và duy trì nhịp ổn định trước khi '
            'cam kết; tốc độ quyết định thay đổi theo hoàn cảnh.'
        ),
        weakness='Khi nỗi sợ thất thoát lấn át tầm nhìn, dễ trở nên quá phòng thủ, tính toán vụn vặt.',
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'thai_am'}),
        dia_chi=(DiaChi.THIN, DiaChi.TUAT),
        title='Thái Âm độc tọa Thìn/Tuất',
        axis_classical_vi='Có mục tiêu ↔ Manh động',
        axis_interpretation=(
            'Hành động theo mục tiêu rõ ràng và có kiểm chứng, hoặc quyết dựa trên hình dung, cảm '
            'xúc chưa được đối chiếu thực tế.'
        ),
        core_temperament='Nhạy cảm nhưng có thể theo đuổi mục tiêu âm thầm, bền bỉ; chú ý nền tảng lâu dài.',
        personality_mechanism=(
            'Thái Âm độc tọa đối Thái Dương, trong tam hợp có Thiên Cơ và Đồng–Lương: nội tâm giàu '
            'tiếp nhận và tầm nhìn xa cần chuyển hóa thành lựa chọn rõ ràng.'
        ),
        observable_hypothesis=(
            'Có thể âm thầm đặt một mục tiêu và tích lũy từng bước; trước lúc quyết định thường cần'
            ' đối chiếu hình dung của mình với tình hình thực tế.'
        ),
        weakness='Dễ bị cảm xúc hoặc tưởng tượng dẫn đi, quyết theo một hình dung chưa được kiểm chứng.',
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'liem_trinh', 'tham_lang'}),
        dia_chi=(DiaChi.TI, DiaChi.HOI),
        title='Liêm Trinh – Tham Lang Tỵ/Hợi',
        axis_classical_vi='Tình cảm ↔ Ham muốn vật chất',
        axis_interpretation=(
            'Tìm sự gắn bó và đáp lại về tình cảm, hoặc bị thu hút mạnh bởi lợi ích, hưởng thụ và '
            'kết quả vật chất.'
        ),
        core_temperament=(
            'Có sức hút, coi trọng tương tác và trải nghiệm; đan xen nhu cầu gắn bó với khát vọng '
            'được hưởng thụ.'
        ),
        personality_mechanism=(
            'Liêm Trinh–Tham Lang nối nhu cầu ranh giới, ý nghĩa của cam kết với ham muốn mở rộng '
            'trải nghiệm; tam hợp còn có các cặp hành động mạnh.'
        ),
        observable_hypothesis=(
            'Trong lựa chọn liên quan quan hệ hoặc trải nghiệm, có thể vừa tìm sự gắn bó vừa muốn '
            'mở rộng cơ hội; cách đặt ranh giới không cố định.'
        ),
        weakness='Dễ lẫn lộn tình cảm, sự công nhận và lợi ích; hoặc bị một ham muốn trước mắt chi phối.',
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'cu_mon'}),
        dia_chi=(DiaChi.TY, DiaChi.NGO),
        title='Cự Môn độc tọa Tý/Ngọ',
        axis_classical_vi='Nội liễm ↔ Nghi kỵ',
        axis_interpretation=(
            'Kín đáo để quan sát, suy xét trước khi tin, hoặc nghi ngờ quá mức đến mức khó tiếp '
            'nhận cả thông tin có căn cứ.'
        ),
        core_temperament='Tư duy phản biện sâu, ít cả tin, giỏi nhìn nhận lỗ hổng trong lập luận và động cơ.',
        personality_mechanism=(
            'Cự Môn độc tọa xung Thiên Cơ: nhu cầu đặt câu hỏi đối diện nhiều khả năng diễn giải và'
            ' phương án khác nhau.'
        ),
        observable_hypothesis=(
            'Khi tiếp nhận thông tin, có thể chú ý điểm bất nhất, hỏi về căn cứ và động cơ trước '
            'khi đồng ý; cách chất vấn có thể kín đáo hoặc trực diện.'
        ),
        weakness='Quá kín kẽ, đa nghi, tự phòng vệ thay vì tìm sự thật.',
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'thien_tuong'}),
        dia_chi=(DiaChi.SUU, DiaChi.MUI),
        title='Thiên Tướng độc tọa Sửu/Mùi',
        axis_classical_vi='Thanh nhã ↔ Dung tục',
        axis_interpretation=(
            'Giữ sự tinh tế, đúng mực trong giao tiếp, hoặc quá chạy theo hình thức, đánh giá xã '
            'hội và lợi ích trước mắt.'
        ),
        core_temperament='Lịch thiệp, coi trọng tác phong, phép tắc; khéo hỗ trợ và giữ thể diện cho tập thể.',
        personality_mechanism=(
            'Thiên Tướng độc tọa đối Tử Vi–Phá Quân: trách nhiệm phối hợp được đặt trước khả năng '
            'hệ thống thay đổi từ gốc.'
        ),
        observable_hypothesis=(
            'Trong môi trường tập thể, có thể chú trọng phép tắc, hình ảnh chung và vai trò của '
            'từng cá nhân; thường muốn xử lý việc sao cho các bên giữ được thể diện.'
        ),
        weakness=(
            'Có thể lệ thuộc quy chuẩn xã hội, quá trọng hình thức, hành xử theo lợi ích và đánh '
            'giá của người ngoài.'
        ),
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'thien_dong', 'thien_luong'}),
        dia_chi=(DiaChi.DAN, DiaChi.THAN),
        title='Thiên Đồng – Thiên Lương Dần/Thân',
        axis_classical_vi='Lãng mạn ↔ Nguyên tắc',
        axis_interpretation=(
            'Đối đãi bằng thiện ý, cảm hứng và lý tưởng tốt đẹp, hoặc ưu tiên chuẩn mực lâu dài '
            'ngay cả khi chúng gây bất tiện.'
        ),
        core_temperament=(
            'Nhân hậu, hiền hòa, lý tưởng hóa điều tốt, có thiên hướng chăm sóc, cố vấn và hòa '
            'giải.'
        ),
        personality_mechanism=(
            'Thiên Đồng–Thiên Lương đồng cung đặt sự dễ chịu trước mắt trong quan hệ với điều có '
            'thể nâng đỡ bền vững.'
        ),
        observable_hypothesis=(
            'Khi có bất hòa, có thể thiên về xoa dịu và tìm một nguyên tắc chung để mọi người cùng '
            'dựa vào; đôi khi chọn vai trò hỗ trợ hoặc cố vấn.'
        ),
        weakness=(
            'Dễ kỳ vọng thế giới phải tử tế như mình hình dung, hoặc dùng chuẩn mực để ràng buộc '
            'người khác.'
        ),
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'vu_khuc', 'that_sat'}),
        dia_chi=(DiaChi.MEO, DiaChi.DAU),
        title='Vũ Khúc – Thất Sát Mão/Dậu',
        axis_classical_vi='Quyết đoán ↔ Thiển lự',
        axis_interpretation=(
            'Quyết nhanh khi đã nắm trọng tâm và nguồn lực, hoặc hành động vội trước khi lường đủ '
            'hệ quả.'
        ),
        core_temperament='Thực dụng, dứt khoát, hành động mạnh và xử lý tình huống áp lực nhanh.',
        personality_mechanism=(
            'Vũ Khúc–Thất Sát ghép tính dứt khoát với yêu cầu thực tế: không chỉ dám làm mà còn '
            'phải biết mình có gì để làm.'
        ),
        observable_hypothesis=(
            'Khi cần xử lý việc khó, có thể nhanh chóng xác lập ưu tiên, nguồn lực và bước hành '
            'động; mức độ tham khảo ý kiến trước khi quyết tùy cấu hình.'
        ),
        weakness=(
            'Dễ đánh đổi chiều sâu lấy tốc độ, cắt đứt quá nhanh hoặc xem nhẹ hậu quả với người '
            'khác.'
        ),
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'thai_duong'}),
        dia_chi=(DiaChi.THIN, DiaChi.TUAT),
        title='Thái Dương độc tọa Thìn/Tuất',
        axis_classical_vi='Tự chủ ↔ Bị lôi kéo',
        axis_interpretation=(
            'Chủ động chọn trách nhiệm phù hợp sức mình, hoặc bị kỳ vọng và nhu cầu được công nhận '
            'cuốn vào việc vượt giới hạn.'
        ),
        core_temperament='Có trách nhiệm, khuynh hướng gánh vác; dễ làm chỗ dựa, đứng ra giải quyết việc khó.',
        personality_mechanism=(
            'Thái Dương độc tọa đối Thái Âm, tam hợp có Cự Môn: xu hướng đưa việc ra ánh sáng cần '
            'cân bằng với khả năng lắng nghe và chia sẻ trách nhiệm.'
        ),
        observable_hypothesis=(
            'Trước việc chung chưa ai nhận, có thể chủ động đứng ra giải thích, tổ chức hoặc gánh '
            'trách nhiệm; cách chia phần việc với người khác còn cần xét thêm.'
        ),
        weakness=(
            'Dễ tiêu hao vì trách nhiệm ngoại cảnh, để nhu cầu được công nhận biến thành ôm việc '
            'hoặc kiệt sức.'
        ),
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'thien_co'}),
        dia_chi=(DiaChi.TY, DiaChi.NGO),
        title='Thiên Cơ độc tọa Tý/Ngọ',
        axis_classical_vi='Cương quyết ↔ Do dự',
        axis_interpretation=(
            'Biến phân tích thành quyết định rõ ràng, hoặc tiếp tục cân nhắc, đổi phương án đến mức'
            ' khó chốt hướng.'
        ),
        core_temperament='Đầu óc sắc bén, xoay chuyển khéo; khi chủ động có thể biến phân tích thành quyết sách.',
        personality_mechanism=(
            'Thiên Cơ độc tọa xung Cự Môn, tam hợp có Thái Âm và Đồng–Lương: phân tích nhiều hướng '
            'cần kết thúc bằng một lựa chọn có thể giải thích.'
        ),
        observable_hypothesis=(
            'Có thể nhanh phân tích phương án, thay đổi cách tiếp cận và lựa chọn đường xử lý phù '
            'hợp; mức quyết liệt khi triển khai không thể suy chỉ từ tinh hệ.'
        ),
        weakness=(
            'Khi quá uyển chuyển dễ do dự, chọn đường vòng, giấu ý kiến hoặc để người khác quyết '
            'hộ.'
        ),
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'tu_vi', 'thien_phu'}),
        dia_chi=(DiaChi.DAN, DiaChi.THAN),
        title='Tử Vi – Thiên Phủ Dần/Thân',
        axis_classical_vi='Chủ động ↔ Bị động',
        axis_interpretation=(
            'Tự xác lập hướng đi và khởi động kế hoạch, hoặc thiên về giữ nền tảng, chờ điều kiện '
            'thuận lợi mới hành động.'
        ),
        core_temperament=(
            'Năng lực điều hành và giữ thế cân bằng giữa mở rộng với bảo toàn; thích tạo trật tự '
            'vững chắc.'
        ),
        personality_mechanism=(
            'Tử Vi–Thiên Phủ đồng cung tập hợp quyền định hướng và nhu cầu bảo toàn nền tảng; Thất '
            'Sát đối cung đặt bài toán hành động quyết liệt.'
        ),
        observable_hypothesis=(
            'Khi xây dựng kế hoạch, có thể quan tâm cả tầm nhìn, quyền điều hành và khả năng duy '
            'trì nguồn lực; lựa chọn mở rộng hay giữ ổn định tùy điều kiện.'
        ),
        weakness=(
            'Hai nhu cầu tiến và giữ có thể triệt tiêu nhau, thành cầu toàn, chờ chắc thắng rồi bỏ '
            'lỡ thời cơ.'
        ),
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'thai_am'}),
        dia_chi=(DiaChi.MEO, DiaChi.DAU),
        title='Thái Âm độc tọa Mão/Dậu',
        axis_classical_vi='Ý chí mạnh ↔ Ý chí yếu',
        axis_interpretation=(
            'Kiên định với điều mình coi trọng, hoặc dễ dao động trước cảm xúc, lời nhận xét và tác'
            ' động từ các mối quan hệ.'
        ),
        core_temperament='Giàu cảm xúc, trực giác và thị hiếu; khi vững lòng rất kiên trì bảo vệ giá trị riêng.',
        personality_mechanism=(
            'Thái Âm độc tọa đối Thiên Đồng, tam hợp có Thiên Lương và Thái Dương: khả năng tiếp '
            'nhận cần một nền giá trị đủ rõ để không chỉ phản ứng theo bầu không khí.'
        ),
        observable_hypothesis=(
            'Có thể quan sát sắc thái và nhu cầu của người khác khá kỹ, rồi bảo vệ điều mình coi '
            'trọng bằng cách kín đáo hoặc bền bỉ.'
        ),
        weakness=(
            'Dễ bị lời nhận xét, quan hệ hoặc cảm xúc nhất thời dẫn dắt nếu thiếu ranh giới cá '
            'nhân.'
        ),
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'tham_lang'}),
        dia_chi=(DiaChi.THIN, DiaChi.TUAT),
        title='Tham Lang độc tọa Thìn/Tuất',
        axis_classical_vi='Kiên nhẫn ↔ Nôn nóng',
        axis_interpretation=(
            'Kiên trì nuôi dưỡng cơ hội đến khi thành kết quả, hoặc nôn nóng, dễ chuyển sang điều '
            'hấp dẫn hơn.'
        ),
        core_temperament=(
            'Đầy ham muốn trải nghiệm và phát triển; có năng lực tận dụng quan hệ, khai thác cơ hội'
            ' để theo mục tiêu dài.'
        ),
        personality_mechanism=(
            'Tham Lang độc tọa đối Vũ Khúc, tam hợp có Sát–Phá: động lực khám phá phải đối diện bài'
            ' toán nguồn lực và cái giá của việc theo đuổi.'
        ),
        observable_hypothesis=(
            'Có thể chủ động kết nối, thăm dò cơ hội rồi chọn mục tiêu đáng đầu tư lâu dài; nhịp '
            'theo đuổi có thể kiên nhẫn hoặc nóng vội.'
        ),
        weakness='Dễ vội vàng, ham kết quả nhanh, phân tán vào nhiều thú vui hoặc dự án.',
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'cu_mon'}),
        dia_chi=(DiaChi.TI, DiaChi.HOI),
        title='Cự Môn độc tọa Tỵ/Hợi',
        axis_classical_vi='Thâm trầm ↔ Bốc đồng',
        axis_interpretation=(
            'Quan sát sâu và chọn thời điểm lên tiếng, hoặc phản ứng nhanh, gay gắt khi gặp điều '
            'trái ý.'
        ),
        core_temperament=(
            'Quan sát sâu, có chính kiến, giỏi tranh luận, phát hiện mâu thuẫn và nói ra vấn đề '
            'khó; tư duy độc lập.'
        ),
        personality_mechanism=(
            'Cự Môn độc tọa xung Thái Dương, tam hợp có Cơ–Đồng: sự sắc bén trong chất vấn gặp nhu '
            'cầu trình bày điều đó ra bên ngoài.'
        ),
        observable_hypothesis=(
            'Khi thấy điều khó hiểu hoặc mâu thuẫn, có thể muốn phân tích và nêu câu hỏi sắc; mức '
            'độ công khai hay giữ kín tùy môi trường.'
        ),
        weakness=(
            'Dễ phản ứng bằng lời sắc bén khi bị kích thích, làm mối quan hệ căng vì nói đúng nhưng'
            ' thiếu thời điểm.'
        ),
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'liem_trinh', 'thien_tuong'}),
        dia_chi=(DiaChi.TY, DiaChi.NGO),
        title='Liêm Trinh – Thiên Tướng Tý/Ngọ',
        axis_classical_vi='Cứng cỏi ↔ Dễ tổn thương',
        axis_interpretation=(
            'Giữ vững nguyên tắc trước sức ép, nhưng cũng có thể nhạy cảm, dễ tổn thương khi danh '
            'dự hoặc lòng tin bị chạm tới.'
        ),
        core_temperament=(
            'Trọng danh dự, kỷ luật, tác phong; muốn được nhìn nhận là người chính đáng và có trách'
            ' nhiệm.'
        ),
        personality_mechanism=(
            'Liêm Trinh–Thiên Tướng đồng cung đưa giới hạn và trách nhiệm cá nhân vào những mối '
            'phối hợp; Phá Quân đối cung cho thấy thực tế nhiều cám dỗ và áp lực thay đổi.'
        ),
        observable_hypothesis=(
            'Trong hợp tác, có thể chú ý danh dự, lời hứa và giới hạn trách nhiệm; muốn hành động '
            'phù hợp với điều đã cam kết.'
        ),
        weakness=(
            'Bề ngoài mạnh nhưng dễ nhạy cảm trước chê trách; có thể cố giữ thể diện thay vì sửa '
            'sai.'
        ),
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'thien_luong'}),
        dia_chi=(DiaChi.SUU, DiaChi.MUI),
        title='Thiên Lương độc tọa Sửu/Mùi',
        axis_classical_vi='Chính trực ↔ Khôn khéo',
        axis_interpretation=(
            'Bảo vệ điều đúng một cách thẳng thắn, hoặc vận dụng sự mềm dẻo và hiểu tình thế để đạt'
            ' mục tiêu.'
        ),
        core_temperament='Có xu hướng bảo vệ lẽ phải, cố vấn, hỗ trợ người khác; biết suy xét điều lâu dài.',
        personality_mechanism=(
            'Thiên Lương độc tọa đối Thiên Cơ, tam hợp có Nhật Nguyệt: khuynh hướng bảo vệ điều '
            'đúng theo chuẩn riêng đi cùng nhu cầu hiểu tình thế trước khi áp dụng.'
        ),
        observable_hypothesis=(
            'Có thể thường đánh giá một quyết định theo công bằng và hậu quả lâu dài, rồi góp ý '
            'hoặc bảo vệ quan điểm; cách trình bày có thể mềm dẻo hoặc nghiêm khắc.'
        ),
        weakness='Đôi khi biến sự sắc sảo thành tính toán để giữ vị thế, hoặc khuyên bảo thành lên lớp.',
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'that_sat'}),
        dia_chi=(DiaChi.DAN, DiaChi.THAN),
        title='Thất Sát độc tọa Dần/Thân',
        axis_classical_vi='Cô cao  ↔ Uy quyền',
        axis_interpretation=(
            'Giữ vị thế và tiêu chuẩn độc lập, ít muốn lệ thuộc, hoặc thể hiện uy quyền qua việc '
            'nắm quyền quyết định và dẫn dắt người khác.'
        ),
        core_temperament='Tự chủ mạnh, tiêu chuẩn cao, thích thử sức và nắm quyền quyết định ở việc quan trọng.',
        personality_mechanism=(
            'Thất Sát độc tọa đối Tử Vi–Thiên Phủ: khả năng tự quyết được soi dưới yêu cầu về hướng'
            ' đi và nền tảng chịu trách nhiệm.'
        ),
        observable_hypothesis=(
            'Trước nhiệm vụ quan trọng, có thể muốn tự quyết, đặt tiêu chuẩn cao và nhận trách '
            'nhiệm chính; mức chấp nhận hợp tác vẫn thay đổi theo hoàn cảnh.'
        ),
        weakness=(
            'Dễ khó gần, coi mình phải tự gánh hết, hoặc trở nên áp đặt khi thiếu niềm tin vào cộng'
            ' sự.'
        ),
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'thien_dong'}),
        dia_chi=(DiaChi.MEO, DiaChi.DAU),
        title='Thiên Đồng độc tọa Mão/Dậu',
        axis_classical_vi='Trống rỗng ↔ Sung túc nội tâm',
        axis_interpretation=(
            'Tìm sự dễ chịu nhưng vẫn thiếu ý nghĩa, điểm tựa bên trong, hoặc có niềm vui và mục '
            'đích đủ sức nuôi dưỡng nội tâm.'
        ),
        core_temperament='Dễ gần, tìm niềm vui giản dị, cần cảm giác bình yên và một đời sống có ý nghĩa.',
        personality_mechanism=(
            'Thiên Đồng độc tọa đối Thái Âm, tam hợp có Cơ và Cự: nhu cầu dễ chịu liên kết với năng'
            ' lực nhận diện và diễn đạt điều không phù hợp.'
        ),
        observable_hypothesis=(
            'Có thể ưu tiên tạo nhịp sống hoặc môi trường dễ chịu, giữ hòa khí trong quan hệ; cách '
            'khởi động lại sau khi mất hứng cần xét thêm.'
        ),
        weakness=(
            'Khi thiếu mục tiêu dễ buồn chán, tránh né trách nhiệm, liên tục tìm sự dễ chịu mà vẫn '
            'thấy thiếu.'
        ),
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'vu_khuc'}),
        dia_chi=(DiaChi.THIN, DiaChi.TUAT),
        title='Vũ Khúc độc tọa Thìn/Tuất',
        axis_classical_vi='An phận ↔ Tiến thủ',
        axis_interpretation=(
            'Ưu tiên an toàn và những cách làm đã hiệu quả, hoặc chủ động mở rộng năng lực, tìm cơ '
            'hội và thành tựu mới.'
        ),
        core_temperament=(
            'Kỷ luật, thực tế, đánh giá con người qua việc làm; có khả năng tích lũy và theo đuổi '
            'kết quả.'
        ),
        personality_mechanism=(
            'Vũ Khúc độc tọa đối Tham Lang, tam hợp có Tử–Phủ và Liêm–Tướng: thực hành ổn định gặp '
            'sự hấp dẫn của những khả năng chưa thử.'
        ),
        observable_hypothesis=(
            'Có thể tin vào công việc có kết quả rõ, kiên trì với phương pháp đã hiệu quả hoặc tìm '
            'cơ hội nâng năng suất; mức tiến thủ không mặc định.'
        ),
        weakness=(
            'Dễ mắc kẹt trong thói quen an toàn hoặc quá đặt nặng và quyết liệt xây  thành quả đến '
            'mức khô cứng.'
        ),
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'thai_duong'}),
        dia_chi=(DiaChi.TI, DiaChi.HOI),
        title='Thái Dương độc tọa Tỵ/Hợi',
        axis_classical_vi='Tích cực ↔ Tiêu cực',
        axis_interpretation=(
            'Chủ động chia sẻ, đóng góp và tiếp tục hành động khi thiếu hưởng ứng, hoặc giảm nhiệt,'
            ' rút lui trước chất vấn và nghịch cảnh.'
        ),
        core_temperament=(
            'Muốn đóng góp, hiện diện và tạo sức ảnh hưởng; có khả năng truyền nhiệt huyết cho tập '
            'thể.'
        ),
        personality_mechanism=(
            'Thái Dương độc tọa xung Cự Môn, tam hợp có Thái Âm và Thiên Lương: nhu cầu làm rõ và '
            'chia sẻ điều mình tin gặp phản hồi chất vấn, đánh giá.'
        ),
        observable_hypothesis=(
            'Trong việc chung, có thể muốn đưa ý tưởng ra ánh sáng, chia sẻ định hướng và tạo động '
            'lực; mức bền bỉ khi thiếu hưởng ứng có thể khác nhau.'
        ),
        weakness='Khi nguồn lực yếu dễ tự nghi ngờ, sống vì đánh giá bên ngoài hoặc mất chủ động.',
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'pha_quan'}),
        dia_chi=(DiaChi.TY, DiaChi.NGO),
        title='Phá Quân độc tọa Tý/Ngọ',
        axis_classical_vi='Ngang ngạnh ↔ Quả cảm',
        axis_interpretation=(
            'Chống lại giới hạn chỉ vì không muốn bị ràng buộc, hoặc dám nhận việc khó để tạo thay '
            'đổi có giá trị.'
        ),
        core_temperament='Dũng cảm đổi mới cái không còn hiệu quả, hành động táo bạo, không sợ bắt đầu lại.',
        personality_mechanism=(
            'Phá Quân độc tọa xung Liêm–Tướng, tam hợp có Sát–Tham: xung lực thay đổi gặp bài toán '
            'nguyên tắc và phối hợp.'
        ),
        observable_hypothesis=(
            'Khi thấy giới hạn không còn phù hợp, có thể muốn tự thử cách mới và chấp nhận bước '
            'ngoặt; sự can đảm hay tính chống đối cần điều kiện để phân biệt.'
        ),
        weakness='Dễ thành chống đối, thích thắng bằng mọi giá hoặc phá trước khi có phương án thay thế.',
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'thien_co'}),
        dia_chi=(DiaChi.SUU, DiaChi.MUI),
        title='Thiên Cơ độc tọa Sửu/Mùi',
        axis_classical_vi='Vươn lên ↔ Buông xuôi',
        axis_interpretation=(
            'Dùng trí tuệ tìm đường cải thiện hoàn cảnh và tiếp tục triển khai, hoặc tự thu hẹp lựa'
            ' chọn, trì hoãn rồi bỏ cuộc.'
        ),
        core_temperament='Ham học hỏi, biết tìm đường tiến thân từ hoàn cảnh khó; tư duy thích nghi tốt.',
        personality_mechanism=(
            'Thiên Cơ độc tọa đối Thiên Lương, tam hợp có Thiên Đồng và Cự Môn: khả năng hoạch định'
            ' được soi qua tiêu chuẩn bền vững và sự hợp lý của môi trường.'
        ),
        observable_hypothesis=(
            'Có thể quan sát lối đi và hoạch định nhiều bước khi muốn cải thiện hoàn cảnh; mức thực'
            ' hiện tới cùng có thể thay đổi theo điều kiện hỗ trợ.'
        ),
        weakness='Dễ trì hoãn hoặc dùng suy tính nhiều mà ít hành động hoặc để tránh né hành động.',
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'tu_vi', 'tham_lang'}),
        dia_chi=(DiaChi.MEO, DiaChi.DAU),
        title='Tử Vi – Tham Lang Mão/Dậu',
        axis_classical_vi='Ham muốn vật chất ↔ Ham muốn tình cảm',
        axis_interpretation=(
            'Bị hấp dẫn bởi địa vị, thành tựu và hưởng thụ hữu hình, hoặc bởi sự gắn bó, được yêu '
            'mến và đáp lại tình cảm.'
        ),
        core_temperament='Có sức hút, tham vọng được chú ý và tạo ảnh hưởng; biết trình bày bản thân hấp dẫn.',
        personality_mechanism=(
            'Tử Vi–Tham Lang đồng cung đặt nhu cầu tạo ảnh hưởng cạnh nhiều ham muốn và cơ hội; '
            'việc chọn trọng tâm hay điều tiết các sức hút này là khả năng cần xét điều kiện, không'
            ' phải phẩm chất mặc định. Tam hợp Vũ–Phá, Liêm–Sát làm nổi rõ áp lực hành động.'
        ),
        observable_hypothesis=(
            'Trong giao tiếp hoặc theo đuổi mục tiêu, có thể biết tạo sức hút và muốn gây ảnh '
            'hưởng; cách chọn lọc cơ hội, điều tiết ham muốn không được coi là có sẵn.'
        ),
        weakness=(
            'Dễ lẫn lộn thành tựu, khoái cảm, tình cảm và quyền lực; khó thấy đủ, dễ chạy theo hào '
            'nhoáng.'
        ),
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'cu_mon'}),
        dia_chi=(DiaChi.THIN, DiaChi.TUAT),
        title='Cự Môn độc tọa Thìn/Tuất',
        axis_classical_vi='Được khơi mở ↔ Bị bài xích',
        axis_interpretation=(
            'Lời phản biện có thể khơi mở cách nhìn mới, hoặc dễ bị tiếp nhận như sự công kích, gây'
            ' đối đầu và bài xích.'
        ),
        core_temperament='Có tài phản biện, kích thích tư duy và giao tiếp để khơi gợi ra vấn đề then chốt.',
        personality_mechanism=(
            'Cự Môn độc tọa đối Thiên Đồng, tam hợp có Thái Dương: khả năng nhận ra điểm bất hợp lý'
            ' liên hệ với nhu cầu dễ chịu và sự công khai.'
        ),
        observable_hypothesis=(
            'Có thể dùng câu hỏi hoặc lập luận để mở ra góc nhìn mới trong cuộc trao đổi; phản ứng '
            'khi bị phản bác tùy hoàn cảnh và các yếu tố điều chỉnh.'
        ),
        weakness=(
            'Nhạy cảm với tư tưởng đối lập, thấy người khác không hiểu mình rồi chuyển sang đấu '
            'khẩu hoặc tự cô lập.'
        ),
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'thien_tuong'}),
        dia_chi=(DiaChi.TI, DiaChi.HOI),
        title='Thiên Tướng độc tọa Tỵ/Hợi',
        axis_classical_vi='Tự khai mở ↔ Nhờ người thành việc',
        axis_interpretation=(
            'Tự tìm đường, khởi xướng và kết nối nguồn lực, hoặc phát huy năng lực nhờ sự dẫn dắt, '
            'hỗ trợ của người khác.'
        ),
        core_temperament='Có khả năng hợp tác, tổ chức, thực thi ý tưởng; ứng xử linh hoạt trong quan hệ xã hội.',
        personality_mechanism=(
            'Thiên Tướng độc tọa đối Vũ–Phá: kỹ năng điều phối đứng trước yêu cầu vừa vận hành vừa '
            'thay đổi cấu trúc.'
        ),
        observable_hypothesis=(
            'Khi có việc cần phối hợp, có thể nhận ra vai trò từng người, kết nối nguồn lực và '
            'triển khai kế hoạch; mức độ tự khởi xướng còn phụ thuộc điều kiện.'
        ),
        weakness='Dễ quen nương theo người mạnh, mất định hướng cá nhân hoặc lệ thuộc sự bảo trợ.',
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'thien_luong'}),
        dia_chi=(DiaChi.TY, DiaChi.NGO),
        title='Thiên Lương độc tọa Tý/Ngọ',
        axis_classical_vi='Cô khắc ↔ Dung hòa',
        axis_interpretation=(
            'Bám chặt chuẩn mực đến mức tạo khoảng cách với người khác, hoặc dung hòa khác biệt mà '
            'vẫn giữ điều cốt yếu.'
        ),
        core_temperament='Trọng đạo lý, trách nhiệm, chăm sóc và chuẩn mực; giỏi nhìn điều nên và không nên.',
        personality_mechanism=(
            'Thiên Lương độc tọa xung Thái Dương: nhu cầu giữ nguyên tắc và bảo vệ gặp yêu cầu thể '
            'hiện, giải thích cho người khác.'
        ),
        observable_hypothesis=(
            'Có thể muốn làm rõ điều nên và không nên trước khi giúp đỡ hay hòa giải; cách giữ '
            'nguyên tắc hoặc dung hòa quan hệ không cố định.'
        ),
        weakness='Dễ khắt khe, thấy mình khác người, hoặc cố hòa giải đến mức bỏ qua nhu cầu bản thân.',
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'liem_trinh', 'that_sat'}),
        dia_chi=(DiaChi.SUU, DiaChi.MUI),
        title='Liêm Trinh – Thất Sát Sửu/Mùi',
        axis_classical_vi='Phấn đấu ↔ Cương bạo',
        axis_interpretation=(
            'Dùng ý chí và kỷ luật để vượt khó, hoặc trở nên cưỡng ép, mạnh tay khi mục tiêu gặp '
            'cản trở.'
        ),
        core_temperament=(
            'Quyết liệt, có kỷ luật, nhiệt huyết và giàu ý chí; phù hợp vai trò cần bản lĩnh bảo vệ'
            ' nguyên tắc.'
        ),
        personality_mechanism=(
            'Liêm Trinh–Thất Sát đồng cung kết hợp quyết tâm hành động với tiêu chuẩn và ranh giới '
            'rõ ràng; Thiên Phủ đối cung đặt giới hạn nguồn lực.'
        ),
        observable_hypothesis=(
            'Khi đã xem một mục tiêu là cần thiết, có thể hành động bền bỉ, giữ kỷ luật và bảo vệ '
            'giới hạn đã đặt ra; mức cứng rắn cần xét thêm.'
        ),
        weakness=(
            'Dễ đặt nặng thắng thua, quá cứng rắn, mạnh tay, hoặc biến tiêu chuẩn thành trừng phạt '
            'người khác.'
        ),
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'thien_dong'}),
        dia_chi=(DiaChi.THIN, DiaChi.TUAT),
        title='Thiên Đồng độc tọa Thìn/Tuất',
        axis_classical_vi='Khoáng đạt ↔ Chí ngắn',
        axis_interpretation=(
            'Rộng lượng để vượt qua va chạm và tiếp tục việc quan trọng, hoặc dễ hài lòng, thiếu '
            'sức theo đuổi mục tiêu dài hạn.'
        ),
        core_temperament=(
            'Rộng lượng, bao dung, vui vẻ, ít chấp nhặt, thích sống thoải mái; có khả năng giữ tinh'
            ' thần nhẹ nhàng.'
        ),
        personality_mechanism=(
            'Thiên Đồng độc tọa xung Cự Môn, tam hợp có Cơ–Âm và Thiên Lương: nhu cầu hòa hợp đối '
            'mặt với các vấn đề phải bàn kỹ, không thể chỉ xuôi theo.'
        ),
        observable_hypothesis=(
            'Trong căng thẳng, có thể tìm cách làm nhẹ không khí, thay đổi góc nhìn hoặc giữ sự '
            'thoải mái; khả năng theo đuổi mục tiêu dài hạn không mặc định.'
        ),
        weakness='Dễ hài lòng quá sớm, tránh xung đột và bỏ mục tiêu khi phải kiên trì chịu khó lâu dài.',
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'vu_khuc', 'pha_quan'}),
        dia_chi=(DiaChi.TI, DiaChi.HOI),
        title='Vũ Khúc – Phá Quân Tỵ/Hợi',
        axis_classical_vi='Thích nghi ↔ Chống đối',
        axis_interpretation=(
            'Chủ động sửa cách làm theo yêu cầu thực tế, hoặc bác bỏ điều cũ theo phản xạ, gây hao '
            'tổn hợp tác và nguồn lực.'
        ),
        core_temperament='Có tinh thần tái cấu trúc thực tế, dám xử lý bài toán khó bằng thay đổi mạnh.',
        personality_mechanism=(
            'Vũ Khúc–Phá Quân đồng cung nối năng lực thực thi với nhu cầu thay cấu trúc; Thiên '
            'Tướng đối cung làm rõ bài toán duy trì phối hợp.'
        ),
        observable_hypothesis=(
            'Khi thấy một cách vận hành kém hiệu quả, có thể muốn sửa trực tiếp công cụ, quy trình '
            'hoặc cách phân bổ nguồn lực; mức quyết liệt không cố định.'
        ),
        weakness='Dễ cố chấp, bác bỏ cách cũ theo phản xạ, làm mất hợp tác và nguồn lực đang có.',
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'thai_duong'}),
        dia_chi=(DiaChi.TY, DiaChi.NGO),
        title='Thái Dương độc tọa Tý/Ngọ',
        axis_classical_vi='Hào nhoáng ↔ Vững chãi',
        axis_interpretation=(
            'Đề cao hình ảnh, sự ghi nhận và sức hút bề ngoài, hoặc xây ảnh hưởng từ kết quả thực '
            'chất, bền vững.'
        ),
        core_temperament=(
            'Có xu hướng thể hiện năng lực công khai, muốn tạo sức ảnh hưởng, được nhìn nhận và dẫn'
            ' dắt bằng sự minh bạch.'
        ),
        personality_mechanism=(
            'Thái Dương độc tọa xung Thiên Lương, tam hợp có Cự Môn: mong muốn làm rõ, phát huy ảnh'
            ' hưởng đối chiếu với tiêu chuẩn hữu ích lâu dài.'
        ),
        observable_hypothesis=(
            'Có thể muốn trình bày quan điểm công khai, đứng ra nhận việc và tạo ảnh hưởng qua sự '
            'rõ ràng; cách cân bằng hình ảnh với kết quả cần xét thêm.'
        ),
        weakness=(
            'Dễ nói nhiều hơn làm, sống vì hình ảnh hoặc gồng gánh vai trò nổi bật khi nền tảng '
            'chưa đủ.'
        ),
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'thien_phu'}),
        dia_chi=(DiaChi.SUU, DiaChi.MUI),
        title='Thiên Phủ độc tọa Sửu/Mùi',
        axis_classical_vi='Khiêm hòa ↔ Nhút nhát',
        axis_interpretation=(
            'Nhường nhịn vì hiểu điều gì cần giữ, hoặc né va chạm đến mức không dám bảo vệ tiếng '
            'nói và lợi ích riêng.'
        ),
        core_temperament='Đôn hậu, giỏi giữ sự ổn định, làm việc có trật tự và biết dung hòa lợi ích.',
        personality_mechanism=(
            'Thiên Phủ độc tọa đối Liêm–Sát: khuynh hướng bảo toàn và làm dịu tình huống đối diện '
            'yêu cầu quyết định rõ ràng trong việc khó.'
        ),
        observable_hypothesis=(
            'Trong nhóm, có thể chú ý giữ sự hài hòa và ổn định nguồn lực, tìm giải pháp ít gây xáo'
            ' trộn; mức dám bảo vệ lợi ích riêng tùy điều kiện.'
        ),
        weakness='Dễ ngại rủi ro, thiếu quyết đoán, nhường nhịn đến mức không dám giữ phần mình.',
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'thien_co', 'thai_am'}),
        dia_chi=(DiaChi.DAN, DiaChi.THAN),
        title='Thiên Cơ – Thái Âm Dần/Thân',
        axis_classical_vi='Lý trí ↔ Cảm xúc',
        axis_interpretation=(
            'Xử lý tình huống dựa trên lập luận và phương án có căn cứ, hoặc ưu tiên trực giác, cảm'
            ' nhận và sắc thái quan hệ.'
        ),
        core_temperament='Kết hợp phân tích tinh tế với trực giác, trí tuệ cảm xúc, óc quan sát và sáng tạo.',
        personality_mechanism=(
            'Thiên Cơ–Thái Âm cùng cung ghép khả năng lập phương án với nhạy cảm đối với bối cảnh '
            'và những điều chưa nói ra.'
        ),
        observable_hypothesis=(
            'Khi xử lý vấn đề, có thể kết hợp nhiều phương án với việc đọc sắc thái bối cảnh và cảm'
            ' xúc; thường cần thời gian để cân nhắc hệ quả với con người.'
        ),
        weakness='Dễ bị tâm trạng làm nhiễu phán đoán, suy nghĩ nhiều, suy diễn các kịch bản trái chiều.',
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'tu_vi', 'thien_tuong'}),
        dia_chi=(DiaChi.THIN, DiaChi.TUAT),
        title='Tử Vi – Thiên Tướng Thìn/Tuất',
        axis_classical_vi='Có tình ↔ Lạnh tình',
        axis_interpretation=(
            'Dẫn dắt bằng nguyên tắc nhưng vẫn xét tình nghĩa và hoàn cảnh con người, hoặc đặt mục '
            'tiêu, vai vế lên trên gắn kết.'
        ),
        core_temperament='Trọng trách nhiệm, trật tự, danh dự; biết bảo vệ người và thiết lập quy tắc công bằng.',
        personality_mechanism=(
            'Tử Vi–Thiên Tướng đồng cung nối nhu cầu dẫn dắt với trách nhiệm điều phối con người; '
            'Phá Quân đối cung gợi câu hỏi về cách đổi mới mà không làm đứt hợp tác.'
        ),
        observable_hypothesis=(
            'Có thể muốn xác định trách nhiệm và nguyên tắc ứng xử rõ ràng, rồi duy trì hợp tác '
            'theo trật tự đã thống nhất; mức mềm dẻo còn tùy điều kiện.'
        ),
        weakness=(
            'Dễ đặt mục tiêu, vai vế hoặc nguyên tắc lên trên quan hệ; khi thất vọng có thể trở nên'
            ' rất lạnh lùng hoặc cắt đứt rất dứt khoát.'
        ),
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'thien_luong'}),
        dia_chi=(DiaChi.TI, DiaChi.HOI),
        title='Thiên Lương độc tọa Tỵ/Hợi',
        axis_classical_vi='Phiêu động ↔ Ổn định',
        axis_interpretation=(
            'Dễ đổi hướng, tìm môi trường phù hợp khi bất mãn, hoặc giữ được điểm tựa và sự vững '
            'vàng giữa biến động.'
        ),
        core_temperament='Có bản năng nâng đỡ, tư duy đạo lý và nhu cầu tìm môi trường phù hợp giá trị bản thân.',
        personality_mechanism=(
            'Thiên Lương độc tọa đối Thiên Đồng; tam hợp có Nhật–Nguyệt: nhu cầu bảo vệ điều bền '
            'vững đối diện các cảm nhận và hoàn cảnh đổi thay.'
        ),
        observable_hypothesis=(
            'Có thể tìm điểm tựa ở nguyên tắc và môi trường phù hợp giá trị của mình, muốn hỗ trợ '
            'người khác nhưng vẫn cần sự ổn định nội tâm.'
        ),
        weakness=(
            'Dễ cảm thấy lạc lõng, không thuộc về đâu, đổi hướng vì bất mãn hoặc khuyên người khác '
            'khi mình chưa vững.'
        ),
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'that_sat'}),
        dia_chi=(DiaChi.TY, DiaChi.NGO),
        title='Thất Sát độc tọa Tý/Ngọ',
        axis_classical_vi='Uy quyền ↔ Khắc kỵ',
        axis_interpretation=(
            'Dùng bản lĩnh và quyền chỉ huy để gánh trách nhiệm, hoặc trở nên khắc nghiệt, khó tin '
            'người và căng thẳng trong đối xử.'
        ),
        core_temperament=(
            'Khí chất chỉ huy, bản lĩnh, chịu áp lực tốt, dám nghĩ dám làm, có khả năng đứng mũi '
            'chịu sào.'
        ),
        personality_mechanism=(
            'Thất Sát độc tọa đối Vũ–Phủ, tam hợp có Phá–Tham: xung lực chốt việc đặt cạnh khả năng'
            ' tổ chức nguồn lực và thử khả năng mới.'
        ),
        observable_hypothesis=(
            'Khi xuất hiện vấn đề cần giải quyết nhanh, có thể chủ động chốt hướng, gánh trách '
            'nhiệm và thúc đẩy hành động; mức lắng nghe phản hồi không mặc định.'
        ),
        weakness='Dễ quá khắc nghiệt, thiếu tin tưởng, áp đặt hoặc coi người khác là vật cản.',
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'liem_trinh'}),
        dia_chi=(DiaChi.DAN, DiaChi.THAN),
        title='Liêm Trinh độc tọa Dần/Thân',
        axis_classical_vi='Nhạy cảm ↔ Thực tế',
        axis_interpretation=(
            'Nhạy với danh dự, ranh giới và sắc thái tình cảm, hoặc ưu tiên hiệu quả, điều kiện và '
            'cách giải quyết thực tế.'
        ),
        core_temperament='Trọng ranh giới, danh dự, có gu thẩm mỹ; biết kết hợp tinh tế với tính kỷ luật.',
        personality_mechanism=(
            'Liêm Trinh độc tọa đối Tham Lang, tam hợp có Tử–Tướng và Vũ–Phủ: các nguyên tắc và cam'
            ' kết tiếp xúc với sức hút của kết quả thực tế.'
        ),
        observable_hypothesis=(
            'Trong lựa chọn hoặc quan hệ, có thể nhạy với ranh giới, sự nhất quán và cách hành xử '
            'đúng mực; thường muốn giữ danh dự mà vẫn xử lý thực tế.'
        ),
        weakness=(
            'Dễ tự ái, trở nên soi xét trong các mối quan hệ hoặc quá cứng nhắc và che giấu cảm '
            'xúc.'
        ),
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'pha_quan'}),
        dia_chi=(DiaChi.THIN, DiaChi.TUAT),
        title='Phá Quân độc tọa Thìn/Tuất',
        axis_classical_vi='Lệch cực ↔ Điều hòa',
        axis_interpretation=(
            'Đẩy việc thay đổi đến cực đoan, chỉ thấy điều cần phá, hoặc biết cân bằng giữa phá bỏ '
            'và giữ lại để tái thiết.'
        ),
        core_temperament='Có động lực thay đổi tận gốc và năng lực tái lập trật tự sau đổ vỡ.',
        personality_mechanism=(
            'Phá Quân độc tọa đối Tử–Tướng, tam hợp có Sát–Tham: khuynh hướng phá bỏ gặp yêu cầu '
            'chọn điểm neo và xây lại cách phối hợp.'
        ),
        observable_hypothesis=(
            'Trước một tình huống bế tắc, có thể muốn thay đổi tận gốc và xây lại cách làm; mức '
            'điều hòa giữa phá bỏ và duy trì cần thêm điều kiện.'
        ),
        weakness=(
            'Dễ chỉ nhìn một phía, phá quá tay, hoặc thay đổi liên tục vì không chịu được trạng '
            'thái trung gian.'
        ),
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'thien_dong'}),
        dia_chi=(DiaChi.TI, DiaChi.HOI),
        title='Thiên Đồng độc tọa Tỵ/Hợi',
        axis_classical_vi='Yếu đuối ↔ Bền bỉ',
        axis_interpretation=(
            'Dễ chùn bước, né áp lực khi gặp khó, hoặc âm thầm chịu đựng, hồi phục và tiếp tục theo'
            ' đuổi điều quan trọng.'
        ),
        core_temperament='Mềm mỏng, dễ cảm thông; nếu có mục đích rõ có thể nhẫn nại, phục hồi và vượt khó.',
        personality_mechanism=(
            'Thiên Đồng độc tọa đối Thiên Lương, tam hợp có Cơ–Cự: thiên hướng hài hòa cần được đặt'
            ' cạnh nguyên tắc lâu dài và khả năng phân tích điều bất tiện.'
        ),
        observable_hypothesis=(
            'Có thể tìm cách giảm căng thẳng, quan tâm cảm xúc và giữ nhịp hồi phục; khi có mục '
            'tiêu rõ, sự bền bỉ có thể được phát huy.'
        ),
        weakness='Dễ trốn tránh xung đột, ỷ lại vào môi trường dễ chịu hoặc kéo dài quyết định khó.',
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'vu_khuc', 'thien_phu'}),
        dia_chi=(DiaChi.TY, DiaChi.NGO),
        title='Vũ Khúc – Thiên Phủ Tý/Ngọ',
        axis_classical_vi='Tạo tài ↔ Quản tài',
        axis_interpretation=(
            'Ưu tiên tạo ra thành quả và nguồn lực mới, hoặc quản lý, phân bổ và bảo toàn những gì '
            'đã tích lũy.'
        ),
        core_temperament='Thực tế, giỏi kết hợp làm ra kết quả với tích lũy, quản trị và kiểm soát rủi ro.',
        personality_mechanism=(
            'Vũ Khúc–Thiên Phủ đồng cung tập hợp năng lực thực thi và bảo toàn nguồn lực; Thất Sát '
            'đối cung là cực quyết đoán ngoài phạm vi an toàn.'
        ),
        observable_hypothesis=(
            'Khi xử lý nguồn lực, có thể vừa tìm cách tạo kết quả mới vừa kiểm soát chi phí, tích '
            'lũy và rủi ro; ưu tiên giữa phát triển và bảo toàn có thể khác nhau.'
        ),
        weakness=(
            'Dễ thiên quá về kiếm thêm mà quên giữ, hoặc giữ quá chặt mà mất khả năng tăng trưởng; '
            'khi quá đặt nặng kết quả hữu hình cũng có thể xem nhẹ yếu tố con người hoặc ý nghĩa '
            'công việc.'
        ),
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'thai_am', 'thai_duong'}),
        dia_chi=(DiaChi.SUU, DiaChi.MUI),
        title='Thái Dương – Thái Âm Sửu/Mùi',
        axis_classical_vi='Cởi mở ↔ Trầm uất',
        axis_interpretation=(
            'Chủ động chia sẻ, kết nối và thể hiện bản thân, hoặc thu mình, giữ kín cảm xúc và suy '
            'ngẫm nhiều hơn.'
        ),
        core_temperament=(
            'Vừa cần kết nối và được nhìn nhận, vừa cần chiều sâu nội tâm; có năng lực nhìn hai mặt'
            ' vấn đề.'
        ),
        personality_mechanism=(
            'Nhật–Nguyệt đồng cung đặt nhu cầu hiện diện ra ngoài và đời sống tiếp nhận nội tâm vào'
            ' cùng một trung tâm lựa chọn.'
        ),
        observable_hypothesis=(
            'Có thể luân phiên giữa việc chủ động trao đổi, xuất hiện trước người khác và nhu cầu '
            'trở về không gian riêng để nhìn lại cảm nhận.'
        ),
        weakness='Dễ xung đột giữa biểu hiện công khai và nhu cầu riêng tư, khiến tâm trạng lên xuống.',
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'tham_lang'}),
        dia_chi=(DiaChi.DAN, DiaChi.THAN),
        title='Tham Lang độc tọa Dần/Thân',
        axis_classical_vi='Ham muốn vật chất ↔ Ham muốn tình cảm',
        axis_interpretation=(
            'Theo đuổi thành tựu, lợi ích và trải nghiệm vật chất, hoặc ưu tiên sự gắn bó, gần gũi '
            'và được đáp lại tình cảm.'
        ),
        core_temperament=(
            'Đa tài, ham trải nghiệm, có duyên, thích giao tiếp; mạnh về tìm nguồn lực hoặc xây kết'
            ' nối tình cảm.'
        ),
        personality_mechanism=(
            'Tham Lang độc tọa đối Liêm Trinh: sức hút cơ hội và trải nghiệm gặp các câu hỏi về cam'
            ' kết, ranh giới và điều gì thực sự đáng giữ.'
        ),
        observable_hypothesis=(
            'Có thể dễ quan tâm tới lĩnh vực mới, xây quan hệ và tìm cơ hội từ trải nghiệm; cách ưu'
            ' tiên thành tựu hay gắn bó phụ thuộc hoàn cảnh.'
        ),
        weakness='Dễ bất ổn nếu không phân biệt mình cần thành tựu, sự kích thích hay sự gắn bó.',
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'thien_co', 'cu_mon'}),
        dia_chi=(DiaChi.MEO, DiaChi.DAU),
        title='Thiên Cơ – Cự Môn Mão/Dậu',
        axis_classical_vi='Chững chạc ↔ Nông nổi',
        axis_interpretation=(
            'Lập luận sau khi cân nhắc đủ mặt, hoặc vội đổi kết luận, tranh thắng bằng sự nhanh trí'
            ' nhất thời.'
        ),
        core_temperament=(
            'Tư duy chiến lược, giỏi lập luận, điều tra và thuyết phục; thích tháo gỡ vấn đề phức '
            'tạp.'
        ),
        personality_mechanism=(
            'Thiên Cơ–Cự Môn đồng cung ghép việc tìm phương án với thói quen nhận ra điểm chưa chặt'
            ' chẽ trong lập luận.'
        ),
        observable_hypothesis=(
            'Khi gặp bài toán phức tạp, có thể đặt nhiều câu hỏi, xem xét lỗ hổng và đề xuất cách '
            'giải quyết; mức chín chắn khi kết luận cần xét thêm.'
        ),
        weakness=(
            'Dễ nói lan man, thích tranh thắng thua, dùng trí khôn ứng biến thay cho lập trường '
            'nhất quán.'
        ),
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'tu_vi', 'that_sat'}),
        dia_chi=(DiaChi.TI, DiaChi.HOI),
        title='Tử Vi – Thất Sát Tỵ/Hợi',
        axis_classical_vi='Uy quyền ↔ Chuyên quyền',
        axis_interpretation=(
            'Dùng quyền lực để định hướng và chịu trách nhiệm, hoặc áp đặt ý chí, kiểm soát quá mức'
            ' và bỏ qua phản hồi.'
        ),
        core_temperament=(
            'Khí chất thủ lĩnh mạnh, quyết định nhanh, có bản lĩnh tổ chức và dẫn dắt trong biến '
            'động.'
        ),
        personality_mechanism=(
            'Tử Vi–Thất Sát đồng cung kết hợp nhu cầu định hướng với khả năng chốt việc dưới áp '
            'lực; Thiên Phủ đối cung gợi giới hạn nguồn lực.'
        ),
        observable_hypothesis=(
            'Khi một tập thể hoặc kế hoạch gặp biến động, có thể muốn đứng ra định hướng và đưa '
            'quyết định quan trọng; mức tham khảo ý kiến không cố định.'
        ),
        weakness=(
            'Dễ cứng rắn quá mức, độc đoán, đồng nhất quyền lực với kiểm soát, khó chấp nhận phản '
            'biện và thiếu sự lắng nghe.'
        ),
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'liem_trinh', 'pha_quan'}),
        dia_chi=(DiaChi.MEO, DiaChi.DAU),
        title='Liêm Trinh – Phá Quân Mão/Dậu',
        axis_classical_vi='Vì việc chung ↔ Tư lợi',
        axis_interpretation=(
            'Thay đổi quy tắc để phục vụ lợi ích chung, hoặc dùng việc cải cách nhằm bảo vệ lợi ích'
            ' riêng.'
        ),
        core_temperament=(
            'Có tinh thần cải cách thể chế và những quy tắc vận hành bất hợp lý, muốn thay đổi bằng'
            ' hành động cụ thể; phạm vi có thể từ nhóm nhỏ đến tổ chức.'
        ),
        personality_mechanism=(
            'Liêm Trinh–Phá Quân đồng cung đặt câu hỏi liệu việc phá bỏ giới hạn hiện có phục vụ '
            'một nguyên tắc sâu hơn hay chỉ tháo gỡ tình huống trước mắt.'
        ),
        observable_hypothesis=(
            'Khi thấy quy tắc hoặc cách vận hành bất hợp lý, có thể chủ động muốn sửa đổi và xác '
            'lập giới hạn mới; phạm vi có thể từ quan hệ, nhóm nhỏ tới tổ chức.'
        ),
        weakness=(
            'Dễ biến lý tưởng thành cuộc đấu quyền lợi, chống đối theo cảm xúc hoặc hợp lý hóa '
            'quyết định có lợi riêng.'
        ),
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'thien_phu'}),
        dia_chi=(DiaChi.TI, DiaChi.HOI),
        title='Thiên Phủ độc tọa Tỵ/Hợi',
        axis_classical_vi='Ôn hòa ↔ Quyền thuật (mưu lược, uyển chuyển, thủ thuật trong quan hệ)',
        axis_interpretation=(
            'Giữ nền tảng bằng hợp tác và lòng tin, hoặc giữ thế bằng tính toán lợi ích, thủ thuật '
            'và kiểm soát quan hệ.'
        ),
        core_temperament='Điềm tĩnh, giỏi giữ nguồn lực, xây quan hệ bền và tính toán đường dài.',
        personality_mechanism=(
            'Thiên Phủ độc tọa đối Tử–Sát: nhu cầu giữ nền tảng gặp động lực hành động mạnh từ phía'
            ' đối ứng.'
        ),
        observable_hypothesis=(
            'Trong việc dài hạn, có thể ưu tiên phòng ngừa rủi ro, phân bổ nguồn lực và xây quan hệ'
            ' đáng tin; mức độ cởi mở, tin người cần xét thêm.'
        ),
        weakness=(
            'Nếu quá chú trọng giữ thế và lợi ích, có thể biến sự kín kẽ thành cách tính toán, đa '
            'nghi, cân nhắc lợi ích, động cơ, chi phối người khác; đòi hỏi quá nhiều sự chắc chắn '
            'về mọi người cũng dễ khiến khó đặt lòng tin.'
        ),
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'thien_dong', 'thai_am'}),
        dia_chi=(DiaChi.TY, DiaChi.NGO),
        title='Thiên Đồng – Thái Âm Tý/Ngọ',
        axis_classical_vi='Tích cực ↔ Tiêu cực',
        axis_interpretation=(
            'Chủ động vun đắp điều có ý nghĩa và chấp nhận vượt khó, hoặc chọn an nhàn, chờ hoàn '
            'cảnh thuận lợi mới tiến lên.'
        ),
        core_temperament=(
            'Nhẹ nhàng, tinh tế, đề cao sự an toàn cảm xúc; có thể biến sự tinh tế thành động lực '
            'bền bỉ.'
        ),
        personality_mechanism=(
            'Thiên Đồng–Thái Âm đồng cung ghép nhu cầu hòa hợp và quá trình suy ngẫm, khiến sự '
            'thoải mái có cả chiều bên trong lẫn cách tổ chức đời sống.'
        ),
        observable_hypothesis=(
            'Có thể chú ý tạo cảm giác an toàn và dễ chịu trong sinh hoạt hoặc quan hệ, rồi âm thầm'
            ' chăm chút điều có ý nghĩa với mình.'
        ),
        weakness='Dễ né áp lực, tìm an nhàn quá sớm, chờ điều kiện thuận lợi mà thiếu chủ động.',
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'vu_khuc', 'tham_lang'}),
        dia_chi=(DiaChi.SUU, DiaChi.MUI),
        title='Vũ Khúc – Tham Lang Sửu/Mùi',
        axis_classical_vi='Khát vọng ↔ Dã tâm',
        axis_interpretation=(
            'Theo đuổi thành tựu lớn nhưng biết giới hạn và điểm dừng, hoặc bất chấp cái giá phải '
            'trả để đạt điều mình muốn.'
        ),
        core_temperament=(
            'Tham vọng về thành tựu lớn, giỏi tìm cơ hội, hiện thực hóa mục tiêu và biến năng lực '
            'thực tế thành lợi ích.'
        ),
        personality_mechanism=(
            'Vũ Khúc–Tham Lang đồng cung kết hợp động lực trải nghiệm/đạt được với kỷ luật triển '
            'khai, khiến mong muốn trở thành một dự án có bước đi.'
        ),
        observable_hypothesis=(
            'Khi thấy một cơ hội có thể thành kết quả cụ thể, có thể đầu tư công sức, kỹ năng và '
            'quan hệ để theo đuổi; mức đủ đầy hay quá tham vọng tùy điều kiện.'
        ),
        weakness=(
            'Khó hài lòng, dễ nôn nóng, đặt nặng thành quả hoặc đánh đồng giá trị bản thân với '
            'thành quả.'
        ),
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'thai_duong', 'cu_mon'}),
        dia_chi=(DiaChi.DAN, DiaChi.THAN),
        title='Thái Dương – Cự Môn Dần/Thân',
        axis_classical_vi='Được hỗ trợ ↔ Cô lập',
        axis_interpretation=(
            'Dễ tìm tiếng nói chung và sự cộng tác nhờ khả năng diễn đạt, hoặc thường gặp tranh '
            'cãi, cảm giác khó được thấu hiểu.'
        ),
        core_temperament=(
            'Có tài diễn đạt, tranh luận, thuyết phục, hùng biện, soi rõ vấn đề và tạo ảnh hưởng '
            'qua tri thức, lời nói.'
        ),
        personality_mechanism=(
            'Thái Dương–Cự Môn đồng cung đặt việc truyền đạt định hướng và chất vấn điều chưa rõ '
            'vào cùng một hoạt động; hai cung tam hợp không có chính tinh.'
        ),
        observable_hypothesis=(
            'Trong trao đổi, có thể muốn làm rõ vấn đề bằng lý lẽ, diễn đạt điều mình nhận ra và '
            'tìm người cùng hiểu; mức độ được hưởng ứng hay tranh cãi không mặc định.'
        ),
        weakness=(
            'Dễ gây tranh cãi khi lời nói quá sắc bén; nếu không được tiếp nhận, dễ thấy mình bị '
            'hiểu lầm, lẻ loi, đơn độc.'
        ),
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'thien_tuong'}),
        dia_chi=(DiaChi.MEO, DiaChi.DAU),
        title='Thiên Tướng độc tọa Mão/Dậu',
        axis_classical_vi='Chính trực ↔ Thiên vị',
        axis_interpretation=(
            'Áp dụng nguyên tắc công bằng nhất quán, hoặc dành ngoại lệ vì tình riêng, sự thân '
            'thiết và lợi ích gắn bó.'
        ),
        core_temperament='Coi trọng công bằng, phép tắc, lòng trung thành; giỏi đứng giữa điều phối quan hệ.',
        personality_mechanism=(
            'Thiên Tướng độc tọa đối Liêm–Phá, tam hợp với Thiên Phủ: khuynh hướng điều phối phải '
            'xử lý sự khác nhau giữa quy tắc chung và những cam kết riêng.'
        ),
        observable_hypothesis=(
            'Khi nảy sinh bất đồng trong nhóm, có thể muốn điều phối theo quy tắc chung, nhưng vẫn '
            'chú ý tình nghĩa và cam kết với người liên quan.'
        ),
        weakness='Dễ thiên vị người quen, hoặc đặt tình riêng lên trên nguyên tắc.',
    ),
    InterpretationBasis(
        chinh_tinh=frozenset({'thien_co', 'thien_luong'}),
        dia_chi=(DiaChi.THIN, DiaChi.TUAT),
        title='Thiên Cơ – Thiên Lương Thìn/Tuất',
        axis_classical_vi='Sắc lạnh ↔ Sáng suốt',
        axis_interpretation=(
            'Nhìn thấu vấn đề nhưng dễ lạnh lùng, soi xét, hoặc dùng sự sắc bén để nhận định sáng '
            'rõ và góp ý hữu ích.'
        ),
        core_temperament='Tư duy phân tích gắn với nguyên tắc và chuẩn mực, giỏi phán đoán vấn đề.',
        personality_mechanism=(
            'Thiên Cơ–Thiên Lương đồng cung kết hợp khả năng tìm phương án với tiêu chuẩn về điều '
            'có lợi lâu dài; tam hợp có Đồng–Âm.'
        ),
        observable_hypothesis=(
            'Khi xử lý vấn đề, có thể tìm nguyên nhân, so sánh phương án với tiêu chuẩn lâu dài rồi'
            ' đưa ra nhận xét; cách góp ý sắc bén hay mềm mại cần xét thêm.'
        ),
        weakness='Dễ soi lỗi hoặc chỉ trích quá mức, suy diễn rồi biến sự sáng suốt thành khắt khe.',
    ),
)
_SYSTEM_BY_PLACEMENT = {
    (record.chinh_tinh, branch): record
    for record in TRUNG_CHAU_STAR_SYSTEMS
    for branch in record.dia_chi
}


TRUNG_CHAU_INSTRUCTIONS = """
## Cách đọc diễn giải theo Trung Châu phái
- menh.interpretation chứa bản ghi tinh hệ đã khớp chính tinh tại Mệnh và cặp địa chi.
  Đọc tinh hệ đồng cung như một chỉnh thể, không tự ghép nghĩa từng sao.
- core_temperament xác định khí chất và động lực nền; personality_mechanism
  giải thích cách vận hành. observable_hypothesis là biểu hiện khả dĩ được phép
  chọn hoặc bỏ; weakness là mặt dễ vướng có điều kiện, không phải khuyết điểm chắc chắn.
- axis_classical_vi và axis_interpretation mô tả vấn đề phân biệt và hai cực;
  không tự chọn một cực khi chưa có điều kiện phân định. Câu hỏi phân tích trong
  nguồn không phải thói quen tự vấn của người mang tinh hệ.
  Sáu trường cùng một tinh hệ, không phải sáu nguồn xác nhận độc lập.
- Bản ghi dùng chung cho một cặp địa chi; chỉ phân biệt hai địa chi khi interpretation
  nói rõ. Không đánh giá Miếu/Vượng/Đắc/Bình/Hãm như lớp độc lập hoặc tự đảo cực
  trục từ đắc/hãm.
- menh.interpretation là null khi Mệnh Vô Chính Diệu: chưa có bản ghi khí chất nền VCD trong
  bộ tri thức này, không phải bằng chứng về tính cách hay mức độ có bản sắc.
- than.basic_combination_id chỉ là mã
  nhận diện tổ hợp chính tinh tại Thân, không kèm tri thức diễn giải tổ hợp.
  Không áp bản ghi Mệnh sang Thân; null nghĩa là Thân không có chính tinh.
""".strip()


def get_interpretation_basis(menh: PalaceEvidence) -> InterpretationBasis | None:
    if not menh.chinh_tinh:
        return None
    members = frozenset(star.component_id for star in menh.chinh_tinh)
    record = _SYSTEM_BY_PLACEMENT.get((members, menh.position))
    if record is None:
        raise ModelRetry(
            f"Không tìm thấy tinh hệ Trung Châu cho Mệnh: {sorted(members)} tại {menh.position.value}."
        )
    return record
