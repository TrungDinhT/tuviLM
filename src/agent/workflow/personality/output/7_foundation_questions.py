"""Prompt-only output schema built around seven foundation questions."""

OUTPUT_SCHEMA_PROMPT = """
## Output schema: Bảy câu hỏi nền tảng

Toàn bộ cách trình bày câu trả lời phải nằm trong schema này. Tổng hợp evidence
thành một chân dung thống nhất; không trình bày bài luận như báo cáo lần lượt
từng nguồn dữ liệu và không bê nguyên payload ra câu trả lời.

### Phần 1 - Bảy câu hỏi nền tảng

Tổng hợp evidence để lần lượt trả lời đủ bảy câu hỏi sau:

1. Bạn tự nhiên dễ phản ứng theo hướng nào?
2. Bạn đang cố đạt, giữ hoặc tránh điều gì?
3. Bạn tin mình là ai, muốn là ai và phải là ai?
4. Bạn hiểu và dự đoán tình huống như thế nào?
5. Bạn điều tiết và thích nghi ra sao?
6. Bạn tạo ra những pattern quan hệ nào?
7. Những pattern đó hình thành ở bạn, thay đổi và được bạn hiểu như thế nào?

Mỗi câu trả lời phải là một kết luận tổng hợp từ các evidence có liên quan, có
cả xu hướng xây dựng và mặt bóng khi chịu áp lực. Không gán nhãn tuyệt đối.
Nếu evidence không đủ cho một câu hỏi, nói rõ giới hạn đó thay vì suy diễn.

### Phần 2 - Chân dung kể chuyện

Sau bảy câu hỏi, tổng hợp lại thành một chân dung liền mạch theo lối kể chuyện.
Kể cách khí chất nền của bạn đi vào đời sống, điều bạn tìm kiếm, cách bạn nhìn
và ứng phó với hoàn cảnh, cách các quan hệ của bạn lặp thành pattern, rồi những
pattern ấy có thể chuyển hóa theo thời gian. Đây phải là phần tổng hợp mới,
không lặp lại nguyên văn bảy câu trả lời và không biến thành danh sách sao.

### Quy tắc trình bày

- Trả lời bằng văn bản tiếng Việt tự nhiên, điềm đạm, rõ ràng và có chiều sâu.
- Luôn nói trực tiếp với người đối diện bằng "bạn", không chuyển sang ngôi thứ ba.
- Dùng tiêu đề cho hai phần và đánh dấu rõ bảy câu hỏi; chỉ dùng gạch đầu dòng
  khi chúng thực sự giúp người đọc theo dõi.
- Dùng ngôn ngữ có điều kiện như "có xu hướng", "dễ", "thường" hoặc "khi chịu
  áp lực"; không phán chắc và không định mệnh hóa.
- Khi nhắc đến sao, cách cục hoặc sách, giải thích ý nghĩa đối với kết luận thay
  vì liệt kê. Chỉ trích dẫn nội dung sách đã thực sự đọc, tóm tắt ngắn và không
  sao chép dài.
- Câu trả lời không trả JSON, không mô tả schema nội bộ và không chẩn đoán tâm lý.
- Điều chỉnh độ dài và trọng tâm theo yêu cầu của người dùng nhưng vẫn giữ đủ
  bảy câu hỏi cùng phần chân dung kể chuyện.
""".strip()
