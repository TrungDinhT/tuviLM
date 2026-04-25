def get_cung_analyze_skill() -> str:
    return """Khi phân tích một cung trong Tử Vi, cần tuân theo quy trình sau:
1. Xác định cung trọng tâm dựa trên chủ đề người dùng hỏi (tính cách, công danh, tài chính, hôn nhân, cha mẹ, con cái, sức khỏe, nhà cửa, quan hệ xã hội, phúc đức).
2. Lấy dữ liệu của bản cung bằng get_cung_by_role hoặc get_cung_by_position.
3. Luôn lấy thêm cung xung chiếu bằng get_xung_chieu và 2 cung tam hợp bằng get_tam_hop. Sau khi có vị trí, sử dụng get_cung_by_position để lấy dữ liệu chi tiết của các cung này.
4. Cần tìm kiếm thông tin của : chính tinh, phụ tinh, tuần/triệt, tứ hóa, trạng sinh của cung trọng tâm, xung chiếu, tam hợp. Tra nghĩa sao trong sách bằng search_sections rồi read_section. Ưu tiên đọc chính tinh trước, rồi mới tới phụ tinh/tuần triệt/tứ hóa/tràng sinh.
5. Khi phân tích một cung, luôn đánh giá theo thứ tự: bản chất cung đang hỏi, chính tinh tọa thủ hoặc hội chiếu, độ mạnh/yếu và sự hỗ trợ hay cản trở của các sao, ảnh hưởng của xung chiếu và tam hợp, kết luận tổng hợp, không tách rời từng sao một cách máy móc.
6. Luôn để ý trạng thái đắc hãm của sao để luận đoán. Khi trong tài liệu nói về các tổ hợp sao, thì phải xem có xuất hiện tổ hợp đó không, nếu có cần phải chỉ để luận đoán
"""
