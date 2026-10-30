# Personality overview

Workflow độc lập cho phần “Nét tính cách chủ đạo”, dùng
`WorkflowInputDefinition` / `WorkflowOutputInstruction`. Chưa nối vào main
agent, CLI hoặc API chat; không thay đổi workflow `personality` hiện tại.

Agent tiếp nhận công việc nên đọc [DESIGN.md](DESIGN.md): mục tiêu, các quyết
định đã chốt, ranh giới nguồn dữ liệu và việc còn cần làm.

```python
from src.agent.deps import TuviAgentDeps
from src.agent.workflow.personality_overview import (
    build_personality_overview_agent,
    run_personality_overview_workflow,
)

# Trong async application; la_so là LaSo đã dựng, model là tên model đã cấu hình.
agent = build_personality_overview_agent(model)
text = await run_personality_overview_workflow(
    agent=agent,
    deps=TuviAgentDeps(la_so=la_so, book_root=book_root),
    request="Nét tính cách chủ đạo của tôi là gì?",
)
```

`run_personality_overview_agent()` trả `PersonalityOverview` có bốn trường;
`run_personality_overview_workflow()` render Markdown từ cùng kết quả, không
gọi model viết lại. Usage và message history có thể truyền qua hai hàm.

## Input và nguồn

- `input/tanbien.py`: chính tinh/trạng thái tại Mệnh và tam hợp/xung chiếu;
  Tuần/Triệt tại Mệnh. Thân cư gồm lĩnh vực vận dụng, chính tinh/trạng thái và
  Tuần/Triệt tại Thân; không mở rộng tam phương hoặc vòng Thái Tuế của Thân.
- Instruction đọc đắc/hãm theo từng sao, tổng hợp theo cấu trúc tinh hệ và
  Thể–Dụng, không cộng đặc tính hoặc đếm trùng dữ kiện. Không dùng `tinh_he.py`.
- `input/thai_tue.py`: bốn nhóm (`overview`, `tension`) và mười hai sao
  (`expression`, `reading_hint`). Nội dung bản đầu dựa trên nghiên cứu người dùng,
  còn cần rà và chỉnh cùng người dùng; không phải trích dẫn Tân Biên/Thiên Lương.
  Builder cũ chỉ cung cấp định danh sao. Diễn giải cũ, keywords và technical
  support không được đưa vào input mới; `vong_thai_tue.py` không thay đổi.
- `get_personality_overview_evidence` tự nạp sách vào `meanings`: nghĩa chung
  và mục Mệnh/Thân của chính tinh tại Mệnh/Thân; chỉ đọc chính tinh tam hợp và
  xung chiếu khi Mệnh Vô Chính Diệu. Thân Vô Chính Diệu không đọc thêm.
  Cung trùng nhau chỉ đọc một lần, liên kết qua `component_id`/`palace_role`.
  Không còn tool tra nghĩa riêng. Giữ section ID, breadcrumb và nội dung đúng
  mục; không đưa phần cha hoặc chương lĩnh vực vào context. Thiếu sách/mục/
  nội dung trả rõ trong `missing`; không tự bù nghĩa cho sao chưa có nguồn.
- Các quy tắc Tuần/Triệt giản lược ở instruction là framework người dùng;
  mapping sách hiện chưa có mục chung/Mệnh cho Tuần/Triệt. Không bịa section ID.
- Giữ bốn phần output. “Một điều đáng để ý” chọn một hướng quan sát mới,
  đúng một câu khoảng 20–40 từ, không lặp kết luận hoặc yêu cầu trả lời.

## Tật Ách thử nghiệm

Không có Tật Ách trong input ban đầu. Tool riêng yêu cầu `reason`, chỉ lấy
chính tinh, trạng thái và Tuần/Triệt tại cung này cùng nghĩa sao chung. Không
đọc chương bệnh tật hoặc mở rộng sang phụ tinh/tam phương.

Instruction quy định chỉ gọi khi tension nền chưa rõ, đã xét lại dữ kiện
hiện có và có ích lợi cụ thể từ góc nội tâm. Code kiểm tra lý do không rỗng;
việc lý do có giá trị hay không vẫn là quyết định của model, cần đánh giá trên
output thực tế. Chưa có nguồn diễn giải nội tâm chuyên biệt được duyệt. Không
coi nghĩa chung là bằng chứng về tiềm thức; bỏ qua nếu không có căn cứ phù hợp.

## Kiểm tra

```sh
rtk proxy .venv/bin/python -m pytest tests/test_agent_personality_overview_workflow.py -q
```

Tests kiểm tra lọc dữ kiện, Vô Chính Diệu, chính tinh đôi, Tuần/Triệt, sáu vị
trí Thân cư, phạm vi tra sách, nhánh Tật Ách và vòng gọi tool/validate JSON với
model mô phỏng. Chất lượng một pattern nhất quán, câu gợi mở và quyết định có
cần Tật Ách hay không cần được rà trên model thật; schema không đảm bảo các
tiêu chí ngữ nghĩa này.
