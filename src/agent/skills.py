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
