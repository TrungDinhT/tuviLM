def get_cung_analyze_skill() -> str:
    return """Khi phân tích một cung trong Tử Vi, cần tuân theo quy trình sau:
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


def luan_tinh_cach_b1_b2() -> str:
    """Skill luận tính cách bằng B1 nền lá số và B2 vòng Thái Tuế."""

    return """Skill luan_tinh_cach_b1_b2: luận nền tính cách một người bằng B1-B2.

Mục tiêu: dựng lớp nền trước khi xét chính tinh, Tuần/Triệt, cách cục và phụ tinh. B1 cho biết quan hệ giữa bản thân với môi trường nền; B2 cho biết tư cách, thái độ nhập thế và cách đương số đứng trước cuộc đời. Đây là khung định hướng, không phải kết luận toàn bộ tính cách hay số phận.

Nguyên tắc nguồn:
- Luôn gọi get_laso_foundation cho B1 và get_vong_thai_tue cho B2; chỉ diễn giải dữ kiện hai tool trả về, không tự suy ra dữ liệu còn thiếu.
- Kiến thức cần thiết đã nằm trong payload của hai tool; không cần và không được đọc file knowledge khi chạy agent.
- B1-B2 phải được thực hiện trước B3-B4 và B5-B6, nhưng không thay thế chính tinh, Tuần/Triệt, cách cục, Tứ Hóa hay phụ tinh.
- Kết quả là diễn giải văn hóa/giả thuyết tự phản tỉnh, không phải chẩn đoán tâm lý hay sự thật khách quan.

## Bước 1 - Nền lá số từ get_laso_foundation
1. Đọc Âm/Dương thuận lý hoặc nghịch lý:
   - Thuận lý: dùng các trường environment_alignment, thinking_consistency, action_style, resilience_pattern để mô tả xu hướng hòa nhịp với môi trường, độ nhất quán giữa suy nghĩ và hành động, và cách phản ứng trước hoàn cảnh.
   - Nghịch lý: đọc như độ lệch pha ban đầu, tư duy đa luồng, khả năng tự phản biện và sức bền được rèn qua nghịch cảnh; không gắn nhãn xấu hay bất thường.
   - Đây chỉ là dữ kiện nền; phải chuyển sang B3-B6 trước khi kết luận tính cách.
2. Đọc Bản Mệnh:
   - Dùng name, ngu_hanh và meaning để rút ra hình tượng nạp âm, khí chất nền, tiềm năng và điều kiện giúp phẩm chất đó biểu hiện đúng.
   - Ưu tiên nature và reading_hint; không biến keywords thành danh sách tính từ cứng nhắc, không suy rộng sang nghề nghiệp, giàu nghèo, hôn nhân hay sức khỏe.
3. Đọc Cục và quan hệ Mệnh-Cục:
   - Bản Mệnh là "mình"; Cục là môi trường nền. Không dùng riêng Cục để gán tính cách.
   - Lấy relation và meaning trong menh_cuc_relation làm trọng tâm để xác định môi trường nâng đỡ, đồng hành, làm đương số sinh xuất/hao lực, bị đương số khắc chế/cải tạo, hay gây áp lực lên đương số.
   - Không tự tính lại quan hệ ngũ hành và không xếp loại tốt-xấu tuyệt đối.
4. Tổng hợp B1 thành ba ý: khí chất nền; mức hòa hợp với hoàn cảnh; hướng phát triển hoặc cách dùng sức phù hợp.

## Bước 2 - Tư cách nhập thế từ get_vong_thai_tue
1. Lấy đúng sao vòng Thái Tuế thủ Mệnh từ menh.thai_tue_star; tool đã xác định sao này trực tiếp tại vị trí Mệnh.
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
   - ego_and_collaboration_note: chỉ xuất hiện với Nhóm Chính Phái; dùng như ghi chú về tự trọng, chính danh và cách hợp tác. Chỉ nhấn mạnh cái tôi khi menh.thai_tue_star.id là thai_tue.
   - thien_ma: chỉ có ý nghĩa đặc biệt với Nhóm Đối Lập. Dùng lens để đọc kiểu nghị lực; nếu tuan_triet không rỗng thì nói đà hành động bị cản hoặc phải đi vòng, không nói ý chí biến mất.
   - thai_tue_sat_tinh_at_menh: chỉ áp dụng khi chính Thái Tuế thủ Mệnh đồng cung Không/Kiếp/Hỏa/Linh. Diễn giải thành bài học rèn tâm và quản sát khí, không hù dọa hay kết luận tai họa.
5. Không dùng riêng vòng Thái Tuế để mở rộng luận giàu nghèo, nghề nghiệp, bệnh tật, hôn nhân hay vận hạn.
6. Tổng hợp B2 thành ba ý: tư cách/động lực nhập thế; mặt xây dựng; cái bẫy cần tự điều chỉnh.

## Ghép B1 với B2
- B1 trả lời "khí nền vận hành trong môi trường ra sao"; B2 trả lời "đương số chọn thái độ nào để bước vào đời".
- Tìm điểm đồng thuận và điểm căng giữa hai bước. Ví dụ, nền thiên về uyển chuyển có thể làm mềm nhóm trọng nguyên tắc; nền chịu áp lực có thể khiến nghị lực của Nhóm Đối Lập biểu hiện rõ hơn. Chỉ viết như giả thuyết, không tạo quan hệ nhân quả mà tool không hỗ trợ.
- Nếu B1 và B2 trái sắc thái, giữ cả hai theo cấu trúc "bên trong/nền khí" và "cách biểu hiện ra đời"; không ép chúng thành một kết luận duy nhất.
- Chuyển kết quả sang B3-B4 để chính tinh và Tuần/Triệt xác nhận, phản biện hoặc chỉnh cường độ; sau đó mới dùng B5-B6 hoàn thiện khung.

Cách viết như người luận giỏi:
- Đọc cấu trúc trước khi gán tính từ; tách khí nền, biểu hiện xã hội và bài học trưởng thành.
- Viết hai mặt: khi được nâng đỡ thì biểu hiện ra sao, khi chịu áp lực thì dễ lệch thế nào.
- Dùng câu điều kiện: "có xu hướng", "dễ", "thường", "nếu được rèn luyện".
- Cô đọng, không đọc lại tên mọi trường trong payload, không liệt kê đủ 12 sao vòng Thái Tuế.

Độ dài:
- B1 và B2 mỗi phần 1-3 câu; phần ghép B1-B2 1-2 câu.
- Chỉ mở rộng khi người dùng yêu cầu luận kỹ.

Giọng văn:
- Tiếng Việt tự nhiên, sâu nhưng rõ, giọng truyền đạt như thầy tử vi nhiều năm trong nghề.
- Không chẩn đoán tâm lý, không khẳng định tuyệt đối, không hù dọa.
"""


def luan_tinh_cach_b3_b4() -> str:
    """Skill luận tính cách bằng B3 chính tinh thủ Mệnh và B4 Tuần/Triệt."""

    return """Skill luan_tinh_cach_b3_b4: luận tính cách một người bằng B3-B4.

Mục tiêu: tạo giả thuyết tính cách từ lá số theo lối thầy Tử Vi lão luyện: đọc cấu trúc trước, gán tính từ sau, nói có điều kiện, không đóng đinh.

Nguyên tắc nguồn:
- Gọi get_tinh_cach_b3_b4_context để lấy dữ liệu lá số: Bản Mệnh/Cục, Cung Mệnh, chính tinh, xung chiếu, tam hợp.
- Kiến thức B3-B4 đã được nhúng trong skill này; không cần và không được đọc file knowledge khi chạy agent.
- Nếu cần kiểm chứng nghĩa sao/cách cục trong Tử Vi Tân Biên, dùng read_book_tuvi_tan_bien, read_catalog, read_section, get_list_cach_cuc.
- Kết quả là diễn giải văn hóa/giả thuyết tự phản tỉnh, không phải chẩn đoán tâm lý hay sự thật khách quan.

Quy trình B3-B4:
1. B3 - xác định cấu trúc chính tinh thủ Mệnh:
   - Một chính tinh, hai chính tinh hay Vô Chính Diệu.
   - Không nhầm sao tọa thủ với sao xung chiếu/tam hợp.
   - Với Vô Chính Diệu, phải dùng chính tinh xung chiếu và tam hợp làm dữ liệu bắt buộc.
2. B3 - xét chất lượng vận hành của chính tinh:
   - Miếu/vượng: bản chất sao biểu hiện mạnh, rõ, chủ động.
   - Đắc: có chỗ dùng, phát huy được phần lớn công năng.
   - Bình: có phẩm chất nhưng không nổi trội hoặc thiếu nhất quán.
   - Hãm: phẩm chất khó phát huy mặt xây dựng, dễ lệch hoặc thành cơ chế phòng vệ.
   - Xét quan hệ ngũ hành giữa chính tinh và Bản Mệnh: sao sinh mệnh, đồng hành, mệnh sinh sao, mệnh khắc sao, sao khắc mệnh.
   - Viết B3 thành: động cơ lõi, cách hành động, mặt xây dựng, mặt bóng khi lệch.
3. B4 - áp Tuần/Triệt lên giả thuyết B3:
   - Tuần: bao, giữ, trì hoãn, tự giới hạn, phát triển vòng vèo.
   - Triệt: cắt, chặn, gãy khúc, phủ định phương thức cũ, buộc đổi cách biểu hiện.
   - Bốn kiểu tác động: giảm cường độ; ngăn phương thức biểu hiện ban đầu; kiềm mặt tiêu cực; làm yếu mặt xây dựng.
   - Không đảo dấu máy móc. Sao tốt không tự thành xấu, sao xấu không tự thành tốt; bản chất sao vẫn còn nhưng đổi đường biểu hiện.
   - Triệt có thể nổi bật hơn ở tiền vận nhưng không viết kiểu "đến 30 tuổi hết tác dụng".
4. Xác nhận bằng phần còn lại:
   - Dùng xung chiếu, tam hợp, phụ tinh, Tứ Hóa, cách cục để xác nhận, phản biện hoặc làm mềm kết luận.
   - B3-B4 là xương sống tính cách; các yếu tố khác không thay thế xương sống đó.

Diễn giải chính tinh:
- Không tự nhét bảng nghĩa sao cố định vào câu trả lời. Nếu cần tính cách cụ thể của sao, tra sách bằng read_book_tuvi_tan_bien/read_catalog/read_section.
- Không dùng nhãn cổ nặng tính định kiến làm kết luận trực tiếp, ví dụ không viết kiểu "Liêm Trinh là tù", "Phá Quân là phá", "Thất Sát là hung".
- Dịch nghĩa sao sang các trục hiện đại: động cơ lõi, cách ra quyết định, mức tự kiểm soát, phản ứng khi áp lực, kiểu quan hệ, nguồn phục hồi, điểm mạnh khi được nâng đỡ.
- Ngôn ngữ hiện đại chỉ là lớp diễn giải bổ sung để người đọc tự hiểu mình; không thay thế nguồn Tử Vi và không biến thành chẩn đoán tâm lý.

Nhánh đặc biệt:
- Hai chính tinh: không cộng danh sách tính từ. Hỏi sao nào định mục tiêu, sao nào định cách làm, chúng hỗ trợ hay giằng co, khi áp lực nghiêng về cực nào.
- Vô Chính Diệu: B3 không được rỗng. Lấy chính tinh xung chiếu làm nền, rồi dùng tam hợp/phụ tinh tại Mệnh để xác nhận. Tuần/Triệt có thể trở thành yếu tố cấu trúc.
- Tuần/Triệt án Mệnh, xung chiếu hoặc tam hợp: nêu rõ nó đang tác động vào chính tinh nào và theo cơ chế nào.
- Khi một sao/cặp sao có dấu hiệu đặc biệt, tra sách rồi mới kết luận.
- Nếu nguồn sách có nhiều quan điểm, nói "theo nguồn đang đọc" và giữ kết luận có điều kiện.

Cách viết như người luận giỏi:
- Đọc cấu trúc trước khi gán tính từ.
- Tách nội tâm, hành vi quan sát được và quỹ đạo trưởng thành.
- Viết hai mặt: khi được nâng đỡ thì biểu hiện ra sao, khi áp lực thì lệch thế nào.
- Tìm cả chứng cứ xác nhận và chứng cứ phủ định trong xung chiếu/tam hợp.
- Dùng câu điều kiện: "có xu hướng", "dễ", "thường", "nếu được rèn luyện".
- Cô đọng, vắn tắt, súc tích. Tránh dài dòng, tránh liệt kê mọi sao nếu không trực tiếp phục vụ kết luận.

Độ dài:
- Mỗi mục 1-3 câu.
- Toàn bài ưu tiên ngắn gọn; chỉ mở rộng khi người dùng yêu cầu luận kỹ.

Giọng văn:
- Tiếng Việt tự nhiên, sâu nhưng rõ, giọng truyền đạt như thầy tử vi nhiều năm trong nghề.
- Không chẩn đoán tâm lý, không khẳng định tuyệt đối, không hù dọa.
"""


def luan_tinh_cach_b5_b6_skill() -> str:
    """Quy trình luận khung tính cách từ cách cục (Bước 5) và tô màu chi tiết
    bằng phụ tinh + Tràng Sinh (Bước 6) của workflow
    """
    return """Quy trình luận tính cách theo Bước 5 (cách cục) và Bước 6 (phụ tinh + Tràng Sinh).

## Bước 5 — Khung tính cách lớn từ cách cục
- Gọi get_list_cach_cuc để lấy các cách cục đang ứng với lá số.
- Kết quả được sắp theo priority giảm dần: lấy cách priority cao nhất làm khung tính cách chính (giọng khẳng định mạnh), các cách priority thấp hơn chỉ bổ trợ.
- Các cách cục là "xương sống", quyết định phần lớn tính cách.

## Bước 6 — Tô điểm chi tiết (không lật khung Bước 5)
- Gọi get_phu_tinh_tam_phuong_tu_chinh(role="menh") để lấy phụ tinh chiếu về theo tam phương tứ chính, đã phân nhóm Lục Cát / Lục Sát / Tứ Hóa / Tứ Linh / Tam Minh.
  - Lục Cát: trợ lực, quý nhân, văn tài, thông tuệ — nâng đỡ khung.
  - Lục Sát: nóng vội, biến động, áp lực, cô khắc — gây căng, thử thách khung (cát và hung phải xem cùng lúc).
  - Tứ Hóa: Lộc (thuận lợi, sức hút), Quyền (uy lực, kiểm soát), Khoa (danh tiếng, học hỏi), Kỵ (vướng mắc, nút thắt) — bẻ hướng nét nào trội lên.
  - Tứ Linh: tài hoa, phong thái, khí chất thanh quý.
  - Tam Minh: duyên, sức hút, giao tế, tình cảm.
  - Luôn đọc trạng thái đắc/hãm: đắc/miếu/vượng thì thiên về tốt/ưu điểm, hãm thì thiên về xấu/nhược điểm.
- Gọi get_trang_sinh(role="menh"), thêm role="cung_than" nếu muốn xét cả Thân. Tràng Sinh là vòng vận hạn/phúc-lộc-thọ, ưu tiên thấp nhất khi luận tính cách. Chỉ đưa vào bài luận khi:
  - Trong cung an Mệnh/Thân có sao tạo thành một tổ hợp đã biết. Ví dụ: Tuyệt + Hỏa Tinh + Thất Sát (nét "tàn nhẫn"); Thiên Mã + Trường Sinh (nét "chung thân bôn tẩu"); Mộ + Phá Quân tại Tứ Mộ (chế bớt cái hung của Phá Quân).
  - Nếu KHÔNG khớp tổ hợp nào thì bỏ qua Tràng Sinh hoàn toàn, không nhắc tới thông tin này.

## Cách viết phần Bước 6 cho user
- Chỉ viết tổng quan ngắn gọn, tối đa 50 chữ: nêu vài nhóm nổi trội và tác động chung lên khung (nâng đỡ / gây căng / bẻ hướng). KHÔNG liệt kê hay đi sâu từng con sao.
- Các mô tả chi tiết từng nhóm ở trên chỉ dùng để suy luận nội bộ, không bê nguyên vào câu trả lời.

## Nguyên tắc
- Thứ tự ưu tiên khi có ý kiến trái chiều: Chính tinh > Tuần triệt > Tứ hóa > Phụ tinh > Tràng sinh.
- Bước 6 chỉ thêm chi tiết và điều chỉnh cường độ cho khung Bước 5, không thay đổi kết luận chính.
- Chỉ dùng thông tin từ tool; không tự bịa sao hay tổ hợp không có trong lá số.
"""


def read_book_tuvi_tan_bien() -> str:
    """Skill to read the book Tử Vi Tân Biên with progressive disclosure

    Always use this skill when you get new concepts, topics, etc.
    """

    return """Kỹ năng đọc sách Tử Vi Tân Biên

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
