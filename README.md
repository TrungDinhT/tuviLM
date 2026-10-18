# TuviLM

Chọn model khi chạy workflow bằng `--model` (trước hoặc sau `run`):

```bash
uv run python -m src.cli.main --model openrouter:qwen/qwen3.8-flash run data/workflow_profiles.yaml --workflow strength_weakness
```

Nếu bỏ qua `--model`, CLI dùng `TUVILM_WORKFLOW_MODEL` hoặc model mặc định.

Mở dashboard riêng cho workflow điểm mạnh–điểm yếu:

```bash
uv run python -m src.cli.main view
```

Dashboard tự tìm `reports/strength_weakness*.yaml` / `.yml`. Chọn nhiều lần chạy trong sidebar hoặc upload nhiều report để đối chiếu model. Để mở sẵn một report:

```bash
uv run python -m src.cli.main view reports/strength_weakness_qwen3.8-flash.yaml --port 8501
```

Ba phần của dashboard:

- **Hồ sơ từng người:** đọc tổng quan, điểm mạnh, điểm yếu, luận giải và metric từng hồ sơ cạnh nhau giữa các model.
- **Token & thời gian:** input, output, thinking, total, cache, requests, tool calls, thời gian batch và latency từng người. Thinking nằm trong output; metric thiếu hiển thị trống.
- **So sánh độ đa dạng:** số nhãn khác nhau, độ rộng trong mỗi người, Jaccard giữa người, mức tập trung top 3, tần suất nhãn và ma trận trùng lặp. Có kỳ vọng chính xác khi chỉ giữ 2 nhận định/người để kiểm soát độ dài danh sách.

So sánh dùng phần giao của các hồ sơ thành công, ghép bằng tên, ngày sinh, giờ sinh và giới tính. Số liệu gốc và chuẩn hóa được hiển thị riêng; các số chuẩn hóa không tính nếu có người dưới 2 nhận định. Đa dạng không phải thước đo tính đúng của luận giải.

Năng lực dùng ontology hiện tại. Chủ đề điểm yếu dùng nhãn thủ công đã review trong `data/strength_weakness_review_annotations.json`, kiểm tra SHA-256 của report và tên nhận định trước khi áp dụng. Report mới vẫn đọc được, nhưng chưa có metric chủ đề điểm yếu cho tới khi được review và bổ sung bộ nhãn; không tự suy ra sự khác biệt ngữ nghĩa từ tên gọi.

Có thể xuất bảng metric và độ đa dạng thành CSV. Viewer chỉ đọc file, không gọi model.
