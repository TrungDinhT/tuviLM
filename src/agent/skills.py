def get_cung_analyze_skill() -> str:
    return """Khi phân tích một cung trong Tử Vi, cần tuân theo quy trình sau:

NGUYÊN TẮC TỐI THƯỢNG: "Tiên minh cách cục, thứ khán chúng tinh" — luôn xác định cách cục trước, mới luận tới sao chi tiết. Cách cục là khung luận chính; luận sao rời chỉ tô đậm / điều chỉnh trong khung đó.

- Xác định cung trọng tâm dựa trên chủ đề người dùng hỏi (tính cách, công danh, tài chính, hôn nhân, cha mẹ, con cái, sức khỏe, nhà cửa, quan hệ xã hội, phúc đức).
- Lấy dữ liệu của bản cung bằng get_cung_by_role hoặc get_cung_by_position.
- Dựa vào cung, sử dụng get_role_instruction(role) để lấy thêm thông tin về cách luận cung này.
- BƯỚC ƯU TIÊN: gọi get_cach_cuc_for_palace(position) để lấy danh sách cách cục đã match sẵn (đã được engine evaluate deterministic, không cần tự suy đoán). Nếu muốn xem toàn lá số, dùng get_all_cach_cuc.
  - Với mỗi cách cục match: tra read_catalog/read_section để hiểu nghĩa cách cục đó, lấy đó làm khung diễn giải.
  - Cách cục match có ưu tiên cao hơn luận sao rời.
  - Nếu cung không có cách cục match, mới chuyển sang luận sao rời theo các bước dưới.
- Cần tìm kiếm thông tin của : chính tinh, phụ tinh, tuần/triệt, tứ hóa, trạng sinh của cung trọng tâm, xung chiếu, tam hợp. Tra nghĩa sao trong sách bằng read_catalog rồi read_section. Ưu tiên đọc chính tinh trước, rồi mới tới phụ tinh/tuần triệt/tứ hóa/tràng sinh.
- Khi phân tích một cung, luôn đánh giá theo thứ tự: cách cục đã match → bản chất cung → chính tinh tọa thủ hoặc hội chiếu → độ mạnh/yếu và sự hỗ trợ hay cản trở của các sao → ảnh hưởng của xung chiếu/tam hợp → kết luận tổng hợp.
- Luôn để ý trạng thái đắc hãm của sao để luận đoán.
- Khi một cung Vô Chính Diệu, xem chính tinh ở cung đối diện là chính tinh của cung này, áp dụng quy trình tương tự.
- Sử dụng read_book_tuvi_tan_bien để tra ý nghĩa cách cục / sao trong sách. Không dựa vào kiến thức cá nhân hay phán đoán chủ quan.

Lưu ý: hiệu ứng "sao gặp sao", "hội hợp", "đồng cung", "xung chiếu", "tam hợp" đã được engine xử lý sẵn trong cách cục. Không cần tự suy đoán positional — gọi get_cach_cuc_for_palace là đủ.

## Định dạng "luận sao lẻ trong xung chiếu / tam hợp / nhị hợp"
Khi luận sao lẻ thuộc các cung phụ trợ (xung chiếu, tam hợp, nhị hợp), trình bày KHÁC với cung chính:
- Tối đa 5 bullet gộp cho cả 3 hướng. Cung chính được luận đầy đủ; cung phụ trợ chỉ "tô đậm".
- Mỗi bullet BẮT BUỘC nêu căn cứ trong ngoặc cuối câu: cách cục id (nếu có match), hoặc trang sách / section_id Tử Vi Tân Biên.
- Format: `- [Sao] tại [cung phụ trợ] ([đắc/hãm]) [hướng: xung/tam hợp/nhị hợp]: [tác động lên cung trọng tâm]. (Căn cứ: [cách cục id / sách trang X / section Y])`
- Chỉ chọn sao có ảnh hưởng đáng kể (chính tinh, tứ hóa, sát tinh mạnh, sao trong cách cục match). Không liệt kê toàn bộ.
- Không lặp lại nội dung đã luận ở cung chính. Chỉ nêu phần *thay đổi* hoặc *bổ sung*.
- Nếu cung phụ trợ không có sao đáng kể, ghi rõ "không có sao đáng kể trong [hướng]" thay vì bịa.
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
