import logging


_logger = logging.getLogger(__name__)


def get_cung_analyze_skill() -> str:
    _logger.info("Lấy skill phân tích cung")
    result = """Khi phân tích một cung trong Tử Vi, cần tuân theo quy trình sau:
- Xác định cung trọng tâm dựa trên chủ đề người dùng hỏi (tính cách, công danh, tài chính, hôn nhân, cha mẹ, con cái, sức khỏe, nhà cửa, quan hệ xã hội, phúc đức).
- Lấy dữ liệu của bản cung bằng get_cung_by_role hoặc get_cung_by_position.
- Dựa vào cung, sử dụng get_role_instruction(role) để lấy thêm thông tin về cách luận cung này.
- Cần tìm kiếm thông tin của : chính tinh, phụ tinh, tuần/triệt, tứ hóa, trạng sinh của cung trọng tâm, xung chiếu, tam hợp. Sử dụng get_star_description để hiểu ý nghĩa chung của sao, và get_star_role_interaction để hiểu ý nghĩa của sao khi ở cung đó.
- Khi phân tích một cung, luôn đánh giá theo thứ tự: bản chất cung đang hỏi, chính tinh tọa thủ hoặc hội chiếu, độ mạnh/yếu và sự hỗ trợ hay cản trở của các sao, ảnh hưởng của xung chiếu và tam hợp, kết luận tổng hợp, không tách rời từng sao một cách máy móc.
- Luôn để ý trạng thái đắc hãm của sao để luận đoán. Khi trong tài liệu nói về các tổ hợp sao, thì phải xem có xuất hiện tổ hợp đó không, nếu có cần phải chỉ để luận đoán.
- Trong tài liệu sẽ có khái niệm 'gặp', Sao gặp Sao nghĩa là hai sao nằm trong cùng một cung, hoặc một sao nằm ở cung xung chiếu của sao kia hoặc một sao nằm ở cung tam hợp của sao kia. Đây là hiệu ứng quan trọng cần lưu ý khi luận đoán, vì nó có thể làm thay đổi hoàn toàn ý nghĩa của sao. Khi đọc sách, nếu thấy nói về hiệu ứng gặp giữa các sao, thì cần phải xem xét xem có xuất hiện hiệu ứng này trong tinh bàn hay không, nếu có thì phải ưu tiên dùng thông tin này để luận đoán. Không nên chỉ đọc thông tin về từng sao một cách rời rạc mà không xem xét hiệu ứng gặp của chúng.
- Khi một cung Vô Chính Diệu, hãy xem như chính tinh ở cung đối diện là chính tinh của cung này, và áp dụng quy trình phân tích tương tự.
- Sử dụng read_book_tuvi_tan_bien để tra cứu thông tin về các sao, cách cục, tổ hợp sao, hiệu ứng gặp, v.v. trong sách, không dựa vào kiến thức cá nhân hay phán đoán chủ quan.
"""
    _logger.info("Đã lấy skill phân tích cung: chars=%d", len(result))
    return result


def luan_tinh_cach_skill() -> str:
    """Quy trình hợp nhất luận tính cách theo đầy đủ Bước 1 đến Bước 6."""

    return """Skill luan_tinh_cach: luận tính cách một người theo workflow B1-B6.

Mục tiêu: đọc cấu trúc lá số theo đúng thứ tự để hình thành một giả thuyết tính cách có chiều sâu: B1-B2 dựng nền, B3-B4 xác định lõi vận hành, B5 đặt lõi đó vào khung cách cục, B6 bổ sung sắc thái. Kết quả là diễn giải văn hóa để tự phản tỉnh, không phải chẩn đoán tâm lý, sự thật khách quan hay kết luận số phận.

## Nguyên tắc nguồn chung
- Chỉ dùng dữ liệu từ evidence hoặc tool; không tự bịa sao, trạng thái, cách cục hay tổ hợp không có trong lá số.
- Khi chạy độc lập, gọi get_personality_evidence để lấy đầy đủ B1-B6. Chỉ gọi tool riêng khi cần kiểm tra hoặc bổ sung phần payload chưa đủ.
- Kiến thức quy trình đã nằm trong skill này; không cần và không được đọc file knowledge khi chạy agent.
- Khi cần kiểm chứng nghĩa sao, cách cục hoặc tổ hợp trong Tử Vi Tân Biên, dùng read_book_tuvi_tan_bien, read_catalog và read_section. Chỉ kết luận từ nội dung đã thực sự đọc.

## Bước 1 - Nền lá số
Dữ liệu: get_laso_foundation hoặc foundation trong evidence.

1. Đọc Âm/Dương thuận lý hoặc nghịch lý:
   - Thuận lý: dùng environment_alignment, thinking_consistency, action_style và resilience_pattern để mô tả khả năng hòa nhịp với môi trường, độ nhất quán giữa suy nghĩ và hành động, và cách phản ứng trước hoàn cảnh.
   - Nghịch lý: đọc như độ lệch pha ban đầu, tư duy đa luồng, khả năng tự phản biện và sức bền được rèn qua nghịch cảnh; không gắn nhãn xấu hay bất thường.
   - Đây chỉ là dữ kiện nền, chưa đủ để kết luận tính cách.
2. Đọc Bản Mệnh:
   - Dùng name, ngu_hanh và meaning để rút ra hình tượng nạp âm, khí chất nền, tiềm năng và điều kiện giúp phẩm chất đó biểu hiện đúng.
   - Ưu tiên nature và reading_hint; không biến keywords thành danh sách tính từ cứng nhắc và không suy rộng sang nghề nghiệp, giàu nghèo, hôn nhân hay sức khỏe.
3. Đọc Cục và quan hệ Mệnh-Cục:
   - Bản Mệnh là "mình"; Cục là môi trường nền. Không dùng riêng Cục để gán tính cách.
   - Lấy relation và meaning trong menh_cuc_relation làm trọng tâm để xác định môi trường nâng đỡ, đồng hành, làm đương số sinh xuất/hao lực, bị đương số khắc chế/cải tạo, hay gây áp lực lên đương số.
   - Không tự tính lại quan hệ ngũ hành và không xếp loại tốt-xấu tuyệt đối.
4. Tổng hợp B1 thành: khí chất nền; mức hòa hợp với hoàn cảnh; hướng phát triển hoặc cách dùng sức phù hợp.

## Bước 2 - Tư cách nhập thế qua vòng Thái Tuế
Dữ liệu: get_vong_thai_tue hoặc vong_thai_tue trong evidence.

1. Lấy đúng sao vòng Thái Tuế thủ Mệnh từ menh.thai_tue_star; không nhầm với sao khác trong vòng.
2. Dựng khung tư cách từ menh.group:
   - overview cho mẫu thái độ nhập thế chính.
   - reading_lens cho trục cần quan sát và mặt xây dựng.
   - trap cho mặt dễ lệch khi thiếu cân bằng.
   - Bốn nhóm có thể xuất hiện là Chính Phái, Khôn Ngoan, Đối Lập và Nhường Nhịn. Dùng đúng nội dung tool trả về, không suy diễn tên nhóm theo nghĩa đời thường.
3. Dùng menh.star_meaning để cá thể hóa trong nhóm:
   - keywords chỉ để định hướng nội bộ.
   - at_menh mô tả biểu hiện chính; shadow mô tả mặt bóng; reading_hint chỉ cách cân bằng hai mặt.
   - Không bê nguyên payload thành danh sách và không đóng đinh đương số vào một nhãn.
4. Chỉ dùng technical_support khi trường tương ứng thật sự có trong payload:
   - ego_and_collaboration_note: chỉ xuất hiện với Nhóm Chính Phái; dùng cho tự trọng, chính danh và cách hợp tác. Chỉ nhấn mạnh cái tôi khi menh.thai_tue_star.id là thai_tue.
   - thien_ma: chỉ có ý nghĩa đặc biệt với Nhóm Đối Lập. Dùng lens để đọc kiểu nghị lực; nếu tuan_triet không rỗng thì nói đà hành động bị cản hoặc phải đi vòng, không nói ý chí biến mất.
   - thai_tue_sat_tinh_at_menh: chỉ áp dụng khi chính Thái Tuế thủ Mệnh đồng cung Không/Kiếp/Hỏa/Linh. Diễn giải thành bài học rèn tâm và quản sát khí, không hù dọa hay kết luận tai họa.
5. Không dùng riêng vòng Thái Tuế để luận giàu nghèo, nghề nghiệp, bệnh tật, hôn nhân hay vận hạn.
6. Tổng hợp B2 thành: tư cách/động lực nhập thế; mặt xây dựng; cái bẫy cần tự điều chỉnh.

## Bước 3 - Chính tinh thủ Mệnh
Dữ liệu: get_tinh_cach_b3_b4_context hoặc b3_b4_context trong evidence.

1. Xác định cấu trúc chính tinh tại Mệnh: một chính tinh, hai chính tinh hay Vô Chính Diệu. Không nhầm sao tọa thủ với sao xung chiếu hoặc tam hợp.
2. Với Vô Chính Diệu, dùng chính tinh xung chiếu làm nền bắt buộc, rồi dùng tam hợp và phụ tinh tại Mệnh để xác nhận.
3. Xét chất lượng vận hành:
   - Miếu/vượng: bản chất sao biểu hiện mạnh, rõ, chủ động.
   - Đắc: có chỗ dùng, phát huy được phần lớn công năng.
   - Bình: có phẩm chất nhưng không nổi trội hoặc thiếu nhất quán.
   - Hãm: phẩm chất khó phát huy mặt xây dựng, dễ lệch hoặc thành cơ chế phòng vệ.
4. Xét quan hệ ngũ hành giữa chính tinh và Bản Mệnh: sao sinh mệnh, đồng hành, mệnh sinh sao, mệnh khắc sao, sao khắc mệnh.
5. Viết B3 thành: động cơ lõi, cách hành động, mặt xây dựng và mặt bóng khi lệch.

## Bước 4 - Tuần/Triệt điều chỉnh B3
1. Tuần: bao, giữ, trì hoãn, tự giới hạn, phát triển vòng vèo.
2. Triệt: cắt, chặn, gãy khúc, phủ định phương thức cũ, buộc đổi cách biểu hiện.
3. Xác định cơ chế tác động cụ thể: giảm cường độ; ngăn phương thức biểu hiện ban đầu; kiềm mặt tiêu cực; hoặc làm yếu mặt xây dựng.
4. Không đảo dấu máy móc. Sao tốt không tự thành xấu, sao xấu không tự thành tốt; bản chất sao vẫn còn nhưng đổi đường biểu hiện.
5. Triệt có thể nổi bật hơn ở tiền vận nhưng không viết kiểu "đến 30 tuổi hết tác dụng".
6. Nếu Tuần/Triệt án Mệnh, xung chiếu hoặc tam hợp, nêu rõ nó tác động vào chính tinh nào và theo cơ chế nào.

## Bước 5 - Khung cách cục
Dữ liệu: get_list_cach_cuc hoặc cach_cuc trong evidence.

- Kết quả đã được sắp theo priority giảm dần. Lấy cách priority cao nhất làm khung cấu trúc chính; các cách priority thấp hơn chỉ bổ trợ.
- B3-B4 tạo xương sống của giả thuyết dựa trên chính tinh; B5 dùng cách cục để xác nhận, phản biện hoặc tái cấu trúc giả thuyết đó trước khi kết luận.
- Không tự suy đoán cách cục từ danh sách sao khi deterministic engine không trả về cách đó.

## Bước 6 - Phụ tinh, Tứ Hóa và Tràng Sinh
Dữ liệu: get_phu_tinh_tam_phuong_tu_chinh(role="menh"), get_trang_sinh(role="menh"/"cung_than") hoặc các trường tương ứng trong evidence.

1. Đọc các nhóm phụ tinh theo tam phương tứ chính:
   - Lục Cát: trợ lực, quý nhân, văn tài, thông tuệ; nâng đỡ khung.
   - Lục Sát: nóng vội, biến động, áp lực, cô khắc; gây căng hoặc thử thách khung. Phải xem cát và hung cùng lúc.
   - Tứ Hóa: Lộc tăng thuận lợi/sức hút; Quyền tăng chủ động/kiểm soát; Khoa tăng học hỏi/danh tiếng; Kỵ tạo vướng mắc/nút thắt.
   - Tứ Linh: tài hoa, phong thái, khí chất thanh quý.
   - Tam Minh: duyên, sức hút, giao tế, tình cảm.
   - Luôn đọc trạng thái đắc/hãm: đắc/miếu/vượng thiên về mặt xây dựng, hãm thiên về mặt khó vận hành.
2. Tràng Sinh có ưu tiên thấp nhất khi luận tính cách. Chỉ đưa vào bài khi Mệnh/Thân tạo một tổ hợp đã biết, ví dụ Tuyệt + Hỏa Tinh + Thất Sát; Thiên Mã + Trường Sinh; Mộ + Phá Quân tại Tứ Mộ. Nếu không khớp tổ hợp thì bỏ qua, không cố diễn giải.
3. B6 chỉ thêm chi tiết và điều chỉnh cường độ, không tự lật khung đã được B3-B5 xác lập.
4. Phần B6 cho người dùng chỉ nêu các nhóm nổi trội và tác động chung; không bê nguyên mô tả nội bộ hoặc liệt kê máy móc từng sao.

## Nhánh diễn giải đặc biệt
- Hai chính tinh: không cộng danh sách tính từ. Xác định sao nào định mục tiêu, sao nào định cách làm, chúng hỗ trợ hay giằng co, và khi áp lực nghiêng về cực nào.
- Vô Chính Diệu: không để B3 rỗng; dùng xung chiếu làm nền và tam hợp/phụ tinh để xác nhận. Tuần/Triệt có thể trở thành yếu tố cấu trúc.
- Khi một sao hoặc cặp sao có dấu hiệu đặc biệt, tra sách rồi mới kết luận. Nếu nguồn có nhiều quan điểm, nói "theo nguồn đang đọc" và giữ kết luận có điều kiện.

## Diễn giải chính tinh theo ngôn ngữ hiện đại
- Không tự nhét bảng nghĩa sao cố định vào câu trả lời và không dùng nhãn cổ nặng định kiến làm kết luận trực tiếp, ví dụ "Liêm Trinh là tù", "Phá Quân là phá", "Thất Sát là hung".
- Dịch nghĩa sao sang các trục: động cơ lõi, cách ra quyết định, mức tự kiểm soát, phản ứng khi áp lực, kiểu quan hệ, nguồn phục hồi và điểm mạnh khi được nâng đỡ.
- Ngôn ngữ hiện đại chỉ là lớp diễn giải giúp người đọc tự hiểu mình; không thay thế nguồn Tử Vi.

## Tổng hợp B1-B6
- B1 trả lời khí nền vận hành trong môi trường ra sao; B2 trả lời thái độ nhập thế; B3-B4 mô tả lõi và đường biểu hiện; B5 đặt lõi vào cấu trúc cách cục; B6 chỉnh sắc thái.
- Tìm cả chứng cứ xác nhận và chứng cứ phủ định. Nếu các bước trái sắc thái, giữ chúng thành các lớp "nội tâm/nền khí", "hành vi quan sát được" và "quỹ đạo trưởng thành", không ép thành một nhãn duy nhất.
- Thứ tự ưu tiên khi chi tiết xung đột: chính tinh > Tuần/Triệt > Tứ Hóa > phụ tinh > Tràng Sinh. Cách cục priority cao là khung tổng hợp để tổ chức các chi tiết đó.

## Cách viết
- Đọc cấu trúc trước khi gán tính từ. Viết cả mặt xây dựng khi được nâng đỡ và mặt bóng khi chịu áp lực.
- Dùng câu điều kiện: "có xu hướng", "dễ", "thường", "nếu được rèn luyện". Không khẳng định tuyệt đối, không hù dọa.
- Viết tiếng Việt tự nhiên, sâu nhưng rõ, như người luận Tử Vi nhiều năm. Dùng chấm đầu dòng khi cần tách ý, nhưng phải có phần tổng hợp liền mạch, không chỉ liệt kê payload.
- Không chẩn đoán tâm lý. Độ dài và mức chi tiết phải theo yêu cầu người dùng; không tự ép bài luận thành bản cực ngắn.
"""


def read_book_tuvi_tan_bien() -> str:
    """Skill to read the book Tử Vi Tân Biên with progressive disclosure

    Always use this skill when you get new concepts, topics, etc.
    """

    _logger.info("Lấy skill đọc sách Tử Vi Tân Biên")
    result = """Kỹ năng đọc sách Tử Vi Tân Biên theo kiểu progressive disclosure.

## Mục tiêu: dùng sách như nguồn tham chiếu có cấu trúc, không đọc lan man và không bịa ngoài nội dung đã đọc.

Sách có thể mang lại 2 loại thông tin chính :
1. Thông tin chung về sao, tứ hóa, tràng sinh, tuần triệt.
2. Ảnh hưởng của sao khi ở các cung khác nhau. Cung ở đây được hiểu như vai trò của cung : Mệnh, Phụ Mẫu, Quan Lộc, Tài Bạch, Huynh Đệ, Nô Bộc, Phu Thê, Phúc Đức, Thiên Di, Tật Ách, Tử Tức, Điền Trạch.

## Tools:

- get_star_description(star_name) : lấy mô tả chi tiết về một sao cụ thể trong Tử Vi Tân Biên. star_name phải được viết chính xác như trong sách, có dấu và viết hoa chữ đầu tiên nếu có. Ví dụ: "Thái Dương", "Vũ Khúc", "Hóa Kỵ", "Tuần", "Triệt", v.v. Đây là thông tin căn bảng về sao, bao gồm ý nghĩa chung, đặc tính, cách cục nổi bật, v.v. Thông tin này không liên quan đến cung cụ thể nào, mà là thông tin chung về sao đó nên luôn luôn cần thiết dù bạn đang phân tích cung nào đi nữa.

- get_star_role_interaction(star_name, role) : lấy mô tả về cách một sao cụ thể tương tác với một cung có vai trò nhất định. star_name cũng phải được viết chính xác như trong sách. role là vai trò của cung cần xem xét, ví dụ: "Mệnh", "Phụ Mẫu", "Quan Lộc", v.v. Thông tin này sẽ cho biết ý nghĩa của sao đó khi nó nằm ở cung có vai trò đó, bao gồm cả ảnh hưởng của sao đó đến ý nghĩa của cung và ngược lại, cũng như cách cục nổi bật khi sao đó ở cung đó.


## Các khái niệm thường gặp
- Sao gặp Sao : Hai sao nằm trong cùng một cung.
- Hội hợp : từ hai sao trở lên gặp nhau trong cung một cung, trong xung chiếu hoặc trong tam hợp
- Đồng cung : hai sao nằm trong cùng một cung
- Xung chiếu : hai sao nằm ở cung đối diện nhau
- Tam hợp : hai sao nằm ở cung tam hợp của nhau

"""
    _logger.info("Đã lấy skill đọc sách Tử Vi Tân Biên: chars=%d", len(result))
    return result
