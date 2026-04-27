def get_cung_analyze_skill() -> str:
    return """Khi phân tích một cung trong Tử Vi, cần tuân theo quy trình sau:
- Xác định cung trọng tâm dựa trên chủ đề người dùng hỏi (tính cách, công danh, tài chính, hôn nhân, cha mẹ, con cái, sức khỏe, nhà cửa, quan hệ xã hội, phúc đức).
- Lấy dữ liệu của bản cung bằng get_cung_by_role hoặc get_cung_by_position.
- Cần tìm kiếm thông tin của : chính tinh, phụ tinh, tuần/triệt, tứ hóa, trạng sinh của cung trọng tâm, xung chiếu, tam hợp. Tra nghĩa sao trong sách bằng read_catalog rồi read_section. Ưu tiên đọc chính tinh trước, rồi mới tới phụ tinh/tuần triệt/tứ hóa/tràng sinh. Nếu được, hãy kiếm thông tin về tất cả các sao liên quan, không chỉ sao chính tinh.
- Khi phân tích một cung, luôn đánh giá theo thứ tự: bản chất cung đang hỏi, chính tinh tọa thủ hoặc hội chiếu, độ mạnh/yếu và sự hỗ trợ hay cản trở của các sao, ảnh hưởng của xung chiếu và tam hợp, kết luận tổng hợp, không tách rời từng sao một cách máy móc.
- Luôn để ý trạng thái đắc hãm của sao để luận đoán. Khi trong tài liệu nói về các tổ hợp sao, thì phải xem có xuất hiện tổ hợp đó không, nếu có cần phải chỉ để luận đoán.
- Trong tài liệu sẽ có khái niệm 'gặp', Sao gặp Sao nghĩa là hai sao nằm trong cùng một cung, hoặc một sao nằm ở cung xung chiếu của sao kia hoặc một sao nằm ở cung tam hợp của sao kia. Đây là hiệu ứng quan trọng cần lưu ý khi luận đoán, vì nó có thể làm thay đổi hoàn toàn ý nghĩa của sao. Khi đọc sách, nếu thấy nói về hiệu ứng gặp giữa các sao, thì cần phải xem xét xem có xuất hiện hiệu ứng này trong tinh bàn hay không, nếu có thì phải ưu tiên dùng thông tin này để luận đoán. Không nên chỉ đọc thông tin về từng sao một cách rời rạc mà không xem xét hiệu ứng gặp của chúng.
- Khi một cung Vô Chính Diệu, hãy xem như chính tinh ở cung đối diện là chính tinh của cung này, và áp dụng quy trình phân tích tương tự.

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
1. read_catalog
   - Dùng để đọc mục lục dạng cây.
   - section_id=None: xem các mục cấp cao của phần sách mặc định.
   - section_id="4" hoặc "11.2": xem các mục con của một section cụ thể.
   - depth quyết định nhìn sâu bao nhiêu tầng; bắt đầu với depth=1, tăng lên 2-3 nếu cần dò sâu hơn.
   - Kết quả trả về id và title của từng mục; dựa vào title để chọn mục phù hợp với câu hỏi, sau đó dùng id để đọc nội dung bằng read_section.


2. read_section(section_id, max_chars=8000)
   - Dùng khi đã biết section_id cần đọc.
   - section_id phải có dạng số như "3", "3.4", "3.4.5", hoặc "8.11".
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
"""
