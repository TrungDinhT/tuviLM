# Personality overview

Workflow độc lập cho phần “Nét tính cách chủ đạo”, dùng
`WorkflowInputDefinition` / `WorkflowOutputInstruction`. Có thể chạy qua CLI;
chưa nối vào main agent hoặc API chat.

Agent tiếp nhận công việc nên đọc [DESIGN.md](DESIGN.md): mục tiêu, các quyết
định đã chốt, ranh giới nguồn dữ liệu và việc còn cần làm.

```python
from tuvi_agent.deps import TuviAgentDeps
from tuvi_agent.workflow.personality_overview import (
    build_personality_overview_agent,
    run_personality_overview_workflow,
)

# Trong async application; la_so là LaSo đã dựng, model là tên model đã cấu hình.
agent = build_personality_overview_agent(model)
text = await run_personality_overview_workflow(
    agent=agent,
    deps=TuviAgentDeps(la_so=la_so),
    request="Nét tính cách chủ đạo của tôi là gì?",
)
```

`run_personality_overview_agent()` trả `PersonalityOverview` có bốn trường;
`run_personality_overview_workflow()` render Markdown từ cùng kết quả, không
gọi model viết lại. Usage và message history có thể truyền qua hai hàm.

## Chạy không qua UI

Tạo `profiles.yaml` (ngày dương lịch, giờ 0–23):

```yaml
- name: Mau
  birth_date: 1998-04-04
  birth_time: 8
  gender: male
```

Đặt `OPENROUTER_API_KEY` trong `apps/api/.env` (hoặc biến môi trường), rồi chạy:

```sh
rtk proxy .venv/bin/python -m tuvi_tools.workflow_cli.workflow profiles.yaml --workflow personality_overview --model openrouter:qwen/qwen3.7-max --output /tmp/personality_overview.yaml
```

Kết quả Markdown nằm ở `results[0].output` trong file YAML. Thay profile và
model theo dữ liệu, provider bạn muốn thử.

## Context cho agent

`get_personality_overview_evidence()` trong `input/evidence.py` trả thẳng một
schema gồm bốn nhóm `menh`, `thai_tue`, `than`, `tuan_triet`. Các nhóm giữ vị
trí thực tế, knowledge Trung Châu đã chọn, nghĩa Thái Tuế và bối cảnh Thân cư;
Tuần/Triệt ghi riêng vị trí Mệnh/Thân chịu ảnh hưởng. Không kèm Tật Ách,
trạng thái đắc/hãm hoặc giới tính. Mệnh luôn có `xung_chieu` và `tam_hop`, kể cả khi có chính tinh;
`than.same_as_menh` đánh dấu cùng cung để tránh đếm trùng.

Hook instructions trong `agent.py` chỉ gọi getter rồi `.model_dump_json()`
trước lượt model đầu tiên. Không có hàm dựng lại context hoặc schema trung
gian khác, không đăng ký tool lấy evidence nền cho model, không tra sách.

Nghiên cứu [60 tinh hệ](tuviLM_60_tinh_he_merged.md) là nguồn nội dung;
60 bản ghi được khai báo trực tiếp trong `input/trung_chau.py`, không cần JSON
đi kèm. Mỗi bản ghi dùng `chinh_tinh: frozenset[str]` và `dia_chi` chứa hai enum
`DiaChi`; tra cứu theo tập ID sao và địa chi thực tế, không dùng `system_id`.
Test đối chiếu nội dung Python với Markdown; khi sửa nghiên cứu cần cập nhật
các bản ghi tương ứng.

`menh.interpretation` chỉ chứa một bản ghi khớp toàn bộ chính tinh và cặp địa chi
Mệnh. Mệnh VCD trả `null`, không mượn bản ghi đối cung. Thân chỉ bổ sung
`than.basic_combination_id`, không mở thêm hội chiếu hoặc áp toàn bộ tinh hệ
Mệnh vào Thân. Trục tính chất không tự xác định người ở cực nào; khí chất,
cơ chế và biểu hiện là cùng một nguồn giả thuyết, không phải chứng cứ độc lập.

Prompt tổng hợp trong cùng agent/lượt sinh bài theo A–E: khí chất Mệnh → tư
thế Thái Tuế → phương thức Thân (Thể–Dụng) → constraint Tuần/Triệt → narrative.
Chỉ dùng knowledge được cấp; không tự dùng kiến thức nhớ sẵn, phân cực trục
hoặc tạo một lớp đánh giá đắc/hãm. Output giữ bốn field, phần biểu hiện có
một hoặc hai ý; tên sao được dùng khi giúp giải thích.
Agent không có function tool và không sử dụng Tật Ách. Lượt hợp lệ thông
thường cần một model request; retry JSON có thể cần thêm request.
Không có lượt riêng để viết lại bài.
Bài viết vẫn là giả thuyết để tự quan sát, không phải chẩn đoán.

Instructions chia trách nhiệm: `agent.py` giữ các bước tổng hợp A–E;
`input/trung_chau.py` tập trung cách đọc dữ liệu và giới hạn diễn giải;
`output/overview.py` giữ bố cục, giọng luận và ví dụ câu chữ. Không biến câu hỏi
phân tích trong nguồn thành thói quen tự vấn của người dùng, hoặc tự nối các
khuynh hướng thành quan hệ nhân quả/trước–sau. “Mặt còn lại” có thể là sức ép
hay giới hạn có căn cứ, không bắt buộc là khuyết điểm.

### Giới hạn knowledge đang được cấp

- Thân có ID tổ hợp và bối cảnh Thân cư, chưa có knowledge cơ chế riêng của
  tổ hợp; không tự ghép nghĩa sao hoặc áp bản ghi Mệnh vào Thân.
- VCD có dữ kiện đối cung/tam hợp nhưng chưa có tri thức nền đủ để xác định
  khí chất trong phạm vi này; bài phải nêu giới hạn, không mượn nguyên đối cung.
- `applicable_constraints` hiện rỗng: chưa có bộ quy tắc đã khớp điều kiện
  đi vào evidence. Tuần/Triệt được ghi đúng vị trí, nhưng xử lý `no_change`.
  Tài liệu nghiên cứu tổng quát trong repository chưa phải quy tắc runtime;
  không tự suy Chính Không/Bàng Không hoặc tác động từ tên sao.
- Thiếu nghĩa Thái Tuế thì trả `null` và tiếp tục từ phần còn có căn cứ.
  Dữ kiện lá số Mệnh/Thân thiếu hoặc không nhất quán vẫn báo lỗi, không coi là VCD.

## Kiểm tra

```sh
rtk proxy .venv/bin/python -m pytest tests/test_personality_overview_trung_chau.py tests/test_agent_personality_overview_workflow.py tests/test_workflow_cli.py -q
```

Test đối chiếu đủ 60 bản ghi, kiểm tra bộ chọn qua mọi bố cục an sao,
payload, phạm vi dữ kiện, context được cập nhật khi đổi lá số và số model
requests khi có/không retry bằng model mô phỏng, đồng thời xác nhận agent
không có function tool. Tests prompt kiểm
tra các ràng buộc có mặt; không chứng minh model thật tuân thủ, không lặp ý
hoặc viết chân dung đủ đặc trưng. Những tiêu chí này chưa được kiểm thử bằng LLM thật.
