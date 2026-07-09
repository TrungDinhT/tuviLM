def get_cung_analyze_skill() -> str:
    return """Khi phân tích một cung trong Tử Vi, cần tuân theo quy trình sau:
- Xác định cung trọng tâm dựa trên chủ đề người dùng hỏi (tính cách, công danh, tài chính, hôn nhân, cha mẹ, con cái, sức khỏe, nhà cửa, quan hệ xã hội, phúc đức).
- Lấy dữ liệu của bản cung bằng get_cung_by_role hoặc get_cung_by_position.
- Dựa vào cung, sử dụng get_role_instruction(role) để lấy thêm thông tin về cách luận cung này.
- Cần tìm kiếm thông tin của : chính tinh, phụ tinh, tuần/triệt, tứ hóa, trạng sinh của cung trọng tâm, xung chiếu, tam hợp. Tra nghĩa sao trong sách bằng read_catalog rồi read_section. Ưu tiên đọc chính tinh trước, rồi mới tới phụ tinh/tuần triệt/tứ hóa/tràng sinh. Nếu được, hãy kiếm thông tin về tất cả các sao liên quan, không chỉ sao chính tinh.
- Khi phân tích một cung, luôn đánh giá theo thứ tự: bản chất cung đang hỏi, chính tinh tọa thủ hoặc hội chiếu, độ mạnh/yếu và sự hỗ trợ hay cản trở của các sao, ảnh hưởng của xung chiếu và tam hợp, kết luận tổng hợp, không tách rời từng sao một cách máy móc.
- Luôn để ý trạng thái đắc hãm của sao để luận đoán. Khi trong tài liệu nói về các tổ hợp sao, thì phải xem có xuất hiện tổ hợp đó không, nếu có cần phải chỉ để luận đoán.
- Trong tài liệu sẽ có khái niệm 'gặp', Sao gặp Sao nghĩa là hai sao nằm trong cùng một cung, hoặc một sao nằm ở cung xung chiếu của sao kia hoặc một sao nằm ở cung tam hợp của sao kia. Đây là hiệu ứng quan trọng cần lưu ý khi luận đoán, vì nó có thể làm thay đổi hoàn toàn ý nghĩa của sao. Khi đọc sách, nếu thấy nói về hiệu ứng gặp giữa các sao, thì cần phải xem xét xem có xuất hiện hiệu ứng này trong tinh bàn hay không, nếu có thì phải ưu tiên dùng thông tin này để luận đoán. Không nên chỉ đọc thông tin về từng sao một cách rời rạc mà không xem xét hiệu ứng gặp của chúng.
- Khi một cung Vô Chính Diệu, hãy xem như chính tinh ở cung đối diện là chính tinh của cung này, và áp dụng quy trình phân tích tương tự.
- Sử dụng read_book_tuvi_tan_bien để tra cứu thông tin về các sao, cách cục, tổ hợp sao, hiệu ứng gặp, v.v. trong sách, không dựa vào kiến thức cá nhân hay phán đoán chủ quan.
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


    return """Kỹ năng đọc sách Tử Vi Tân Biên theo kiểu progressive disclosure.

Mục tiêu: dùng sách như nguồn tham chiếu có cấu trúc, không đọc lan man và không bịa ngoài nội dung đã đọc.

## Khi nào dùng kỹ năng này
1. Khi người dùng hỏi về học thuyết, nguyên tắc luận đoán, mục/chương trong sách, ý nghĩa sao, cách cục, tổ hợp sao, hoặc muốn đối chiếu với Tử Vi Tân Biên.
2. Khi cần tìm đúng section_id trước khi đọc nội dung.
3. Khi cần xem cây mục lục để chọn đúng ngữ cảnh trước khi đọc nội dung.
4. Sau khi có được thông tin, cần phải chọn thông tin phù hợp để trả lời, phụ thuộc vào vị trí của Sao, chức vị của cung, sao đắc hay hãm.
5. Khi đọc tài liệu, nếu có nói về hiệu ứng một tổ hợp sao, hoặc một cách cục, thì cần phải xem có xuất hiện tổ hợp đó trong tinh bàn hay không, nếu có thì phải ưu tiên dùng thông tin này để luận đoán. Không nên chỉ đọc thông tin về từng sao một cách rời rạc mà không xem xét tổ hợp của chúng.


## Hai công cụ chính của sách

- section_id là id của một mục trong sách. section id có dạng number.number... Ví dụ: "1.1", "11.2.14". Dùng section_id để đọc nội dung của một mục cụ thể bằng read_section.


1. read_catalog(section_id, depth)
   - Dùng để đọc mục lục dạng cây.
   - section_id=None: xem các mục cấp cao của phần sách mặc định.
   - depth quyết định nhìn sâu bao nhiêu tầng; bắt đầu với depth=1, tăng lên 2-3 nếu cần dò sâu hơn.
   - Kết quả trả về id và title của từng mục; dựa vào title để chọn mục phù hợp với câu hỏi, sau đó dùng id để đọc nội dung bằng read_section.
   - Nên bắt đầu bằng read_catalog(None, depth=2) để có cái nhìn tổng quan về cấu trúc sách, sau đó đi sâu vào các mục con khi đã xác định được chủ đề cần tìm.


2. read_section(section_id, max_chars=8000)
   - Dùng khi đã biết section_id cần đọc.
   - Nội dung trả về đã bao gồm các mục cha trước mục được yêu cầu.
   - max_chars giúp giới hạn section dài; tăng giới hạn nếu nội dung bị cắt mà vẫn cần đọc tiếp.

## Quy trình nên dùng
1. Nếu người dùng đưa section_id rõ ràng: gọi read_section trực tiếp.
2. Nếu người dùng hỏi theo tên sao/cách cục/chủ đề: gọi read_catalog để tìm nhánh liên quan.
3. Nếu chưa chắc ứng viên nằm đúng nhánh: gọi read_catalog với section_id là mục cha gần nhất hoặc None để xem cây.
4. Khi đã chọn đúng id: gọi read_section, đọc thông tin, lựa chọn dữ kiện quan trọng, và tổng hợp trả lời.
5. Nếu không tìm thấy mục phù hợp sau khi xem catalog, nói rõ chưa tìm thấy trong sách.

## Note
- Nên bắt đầu bằng read_catalog(None, depth=2) để xem các phần sách chính, sau đó đi sâu dần vào các mục con.
- Luôn luôn dùng read_section để đọc nội dung mục đã chọn, không tự ý tóm tắt dựa trên title mà chưa đọc nội dung.
- Chương 4 đến 11 chứa thông tin về các cung khác nhau và ảnh hưởng của sao khi ở tại cung đó, nên ưu tiên xem các mục này khi phân tích cung trước khi nhìn vào phần thông tin chung ở chương 3.
- Trong mỗi section của chương 4-11, sẽ có thông tin về các sao khi ở tại cung đó, bao gồm chính tinh, phụ tinh, tuần triệt, tứ hóa, tràng sinh. Đây là những thông tin quan trọng nhất cần tìm kiếm khi phân tích cung, vì chúng có ảnh hưởng trực tiếp đến ý nghĩa của cung đó. Ưu tiên tìm kiếm thông tin về các sao này trước khi tìm kiếm thông tin chung về sao ở chương 3.
- Chương 3 sẽ nói về thông tin chung của các sao. Nhiều trường hợp không thể tìm thấy thông tin của Sao trong phần cung cụ thể, thì có thể phải xem thông tin chung của sao ở chương 3 để luận đoán. Tuy nhiên, nếu đã tìm thấy thông tin của sao ở phần cung cụ thể, thì nên ưu tiên dùng thông tin đó để luận đoán, vì nó sẽ có ngữ cảnh cụ thể hơn so với thông tin chung ở chương 3.
- Đối với chinh tinh, thông tin trong chương 3 luôn quan trọng
- Tên của tiêu đề đôi khi được dùng với tên rút gọn của sao thay vì tên chính thức, lưu ý để không bỏ sót thông tin khi tìm kiếm. Tên rút gọn của sao sẽ được cung cấp trong lá số.

## Các khái niệm thường gặp
- Sao gặp Sao : Hai sao nằm trong cùng một cung.
- Hội hợp : từ hai sao trở lên gặp nhau trong cung một cung, trong xung chiếu hoặc trong tam hợp
- Đồng cung : hai sao nằm trong cùng một cung
- Xung chiếu : hai sao nằm ở cung đối diện nhau
- Tam hợp : hai sao nằm ở cung tam hợp của nhau

"""
