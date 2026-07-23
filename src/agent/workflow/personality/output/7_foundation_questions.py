"""Prompt-only output schema built around seven foundation questions."""

OUTPUT_SCHEMA_PROMPT = """
## Output schema: Bảy câu hỏi nền tảng

Toàn bộ cách trình bày câu trả lời phải nằm trong schema này. Dùng quá trình
B1-B6 như tư duy nội bộ để đọc evidence; không trình bày bài luận như báo cáo
từng bước B1, B2, B3, B4, B5, B6 và không bê nguyên payload ra câu trả lời.

### Phần 1 - Bảy câu hỏi nền tảng

Tổng hợp evidence để lần lượt trả lời đủ bảy câu hỏi sau:

1. Người này tự nhiên dễ phản ứng theo hướng nào?
2. Họ đang cố đạt, giữ hoặc tránh điều gì?
3. Họ tin mình là ai, muốn là ai và phải là ai?
4. Họ hiểu và dự đoán tình huống như thế nào?
5. Họ điều tiết và thích nghi ra sao?
6. Họ tạo ra những pattern quan hệ nào?
7. Pattern đó hình thành, thay đổi và được hiểu như thế nào?

Mỗi câu trả lời phải là một kết luận tổng hợp từ các evidence có liên quan, có
cả xu hướng xây dựng và mặt bóng khi chịu áp lực. Không gán nhãn tuyệt đối.
Nếu evidence không đủ cho một câu hỏi, nói rõ giới hạn đó thay vì suy diễn.

### Phần 2 - Chân dung kể chuyện

Sau bảy câu hỏi, tổng hợp lại thành một chân dung liền mạch theo lối kể chuyện.
Kể cách khí chất nền đi vào đời sống, điều người ấy tìm kiếm, cách họ nhìn và
ứng phó với hoàn cảnh, cách các quan hệ lặp thành pattern, rồi pattern ấy có thể
chuyển hóa theo thời gian. Đây phải là phần tổng hợp mới, không lặp lại nguyên
văn bảy câu trả lời và không biến thành danh sách sao.

### Quy tắc trình bày

- Trả lời bằng văn bản tiếng Việt tự nhiên, điềm đạm, rõ ràng và có chiều sâu.
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
