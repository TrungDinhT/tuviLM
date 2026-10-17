# Personality Overview — thiết kế và bàn giao

Cập nhật: 2026-10-17. Tài liệu này ghi lại mục tiêu, quyết định đã thống nhất
và trạng thái triển khai để tiếp tục công việc mà không cần lịch sử hội thoại.

## 1. Mục tiêu sản phẩm

Tạo phần **“Nét tính cách chủ đạo”**: một chân dung ngắn về **một pattern hành vi
nhất quán**, giúp người dùng tự quan sát. Pattern gồm cách suy nghĩ, xử lý vấn
đề, phản ứng và tension — sự giằng co hoặc cái giá của chính khuynh hướng đó.

Lá số là nguồn giả thuyết, không phải phán quyết về con người. Không mô tả toàn
bộ tính cách, chứng minh Tử Vi, đánh giá đạo đức, năng lực, thành quả hay số phận.
Không cộng tính từ của từng sao; không bịa sự kiện đời sống. Dùng “có xu hướng”,
“thường”, “có thể” khi phù hợp, nhưng vẫn phải cụ thể, tránh nhận định đúng với
gần như bất kỳ ai.

Ví dụ về cách tổng hợp mong muốn: “Nhanh nhận ra điều chưa hợp lý, nhưng thường
cần suy xét trước khi phản ứng.” Hai phía thuộc cùng một cơ chế, không phải hai
đặc điểm rời nhau. Đây là ví dụ cách viết, không phải mapping cố định từ sao.

## 2. Phạm vi và ưu tiên luận giải

| Yếu tố | Vai trò | Giới hạn |
|---|---|---|
| Chính tinh/bộ chính tinh tại Mệnh | Khí chất, cách vận hành tự nhiên | Tổng hợp cả bộ, không cộng đặc tính |
| Vòng Thái Tuế tại Mệnh | Tư thế sống trước hoàn cảnh và cách biểu hiện | Bổ sung cho chính tinh, không thành một chân dung độc lập |
| Tuần/Triệt | Điều chỉnh cách xu hướng được biểu hiện | Không coi là một kiểu tính cách riêng |
| Chính tinh xung chiếu/tam hợp Mệnh | Bối cảnh hỗ trợ; đặc biệt cần khi Vô Chính Diệu | Không đổi sao chiếu thành sao tọa Mệnh |
| Thân cư | Lĩnh vực hướng khí chất vào | Chỉ vị trí Thân cư, không phân tích thêm sao tại Thân |
| Tật Ách | Góc khám phá nội tâm thử nghiệm, có điều kiện | Không lấy mặc định, không luận bệnh/tai ách/tiềm thức chắc chắn |

Tuần thường kìm, làm chậm hoặc tiết chế. Triệt thường ngăn, cắt, tạo gián đoạn
hoặc khiến xu hướng khó biểu hiện trực tiếp. Cả hai có thể giảm biểu hiện quá
cực đoan. Đây là quy tắc giản lược do người dùng cung cấp.

**Mệnh Vô Chính Diệu:** ưu tiên vòng Thái Tuế, đối chiếu chính tinh xung chiếu/
tam hợp và Tuần/Triệt. Không mượn một chính tinh thay thế Mệnh; không kết luận
tuyệt đối bằng công thức như “đắc Tam Không”. Thiếu dữ liệu Mệnh phải báo lỗi,
không được xem là Vô Chính Diệu.

Chỉ dùng lớp lá số gốc. Ngoài phần vòng Thái Tuế đã định nghĩa, không mở rộng
sang phụ tinh, Tứ Hóa, Tràng Sinh, Mệnh–Cục hoặc cách cục khác.

## 3. Vòng Thái Tuế: quyết định quan trọng

**Không sửa `src/agent/tool/thai_tue/vong_thai_tue.py`.** Người dùng yêu cầu giữ
nguyên hành vi các workflow đang sử dụng file này.

Workflow mới gọi `build_vong_thai_tue_payload()` chỉ để lấy ID/tên sao tại Mệnh,
rồi tra bộ diễn giải riêng trong [input/thai_tue.py](input/thai_tue.py). Các
diễn giải cũ, `keywords` và `technical_support` không được chuyển vào input mới.

Khung nghiên cứu người dùng lấy cảm hứng từ hệ thống Thiên Lương, tổ chức thành
**4 tư thế sống × 3 cách biểu hiện**. Nội dung mới là giả thuyết diễn giải nội bộ,
không được gắn nhãn nguyên văn Thiên Lương hay nguồn sách Tân Biên đã xác minh.

| Nhóm | Tư thế sống chung | Cách biểu hiện riêng của ba sao |
|---|---|---|
| Thái Tuế – Quan Phù – Bạch Hổ | Chủ động can dự, có lập trường, nhận trách nhiệm | Thái Tuế: xác lập lập trường/nhận vai trò; Quan Phù: cân nhắc cách làm/hệ quả; Bạch Hổ: dồn sức/theo việc |
| Tang Môn – Tuế Phá – Điếu Khách | Chú ý khoảng cách giữa hiện trạng và điều hợp lý hơn | Tang Môn: suy nghĩ/dự liệu bên trong; Tuế Phá: trực tiếp phản biện/thay đổi; Điếu Khách: xử lý bất đồng bằng lời |
| Thiếu Dương – Tử Phù – Phúc Đức | Nhìn ra khả năng hoặc cách tiếp cận khác | Thiếu Dương: nhanh nhận ra phương án; Tử Phù: khoảng cách nhận thức–thực hiện; Phúc Đức: cân nhắc giới hạn/giá trị trước khi tận dụng |
| Thiếu Âm – Long Đức – Trực Phù | Tiếp nhận, thích nghi, duy trì cân bằng/quan hệ | Thiếu Âm: tiếp nhận trước phản ứng; Long Đức: ưu tiên hòa khí hơn phần thắng; Trực Phù: đóng góp, ít chủ động đòi ghi nhận |

Schema đã thống nhất:

| Model | Field | Chức năng |
|---|---|---|
| `ThaiTueGroupMeaning` | `id`, `name` | Định danh và tên nhóm |
| | `overview` | Một tư thế sống chung, chứa tinh thần cốt lõi |
| | `tension` | Mặt còn lại chung của tư thế sống, có điều kiện |
| `ThaiTueStarMeaning` | `id`, `group_id` | Định danh sao và liên kết nhóm |
| | `expression` | Cách riêng biểu hiện tư thế sống, gồm mặt quá đà riêng khi cần |
| | `reading_hint` | Phân biệt hoặc ngăn hiểu sai; có thể để trống |

Lý do giản lược:

- Nhóm giữ phần chung; sao thừa hưởng và chỉ nói phần riêng. `tension` nhóm
  không gom mọi mặt trái riêng của ba sao rồi gán cho cả nhóm.
- Tinh thần cốt lõi được giữ trong `overview`. Không thêm `archetype` hoặc
  `core_question`: dễ lặp ý hoặc ép diễn giải vào một nhãn/câu hỏi cố định.
- Bỏ `reading_lens` nhóm: các quy tắc chung nằm trong instruction; góc riêng
  đã được mô tả trong `overview`.
- Bỏ `keywords` để tránh cộng tính từ. Không tách `shadow` sao vì dễ lặp
  `tension`; mặt quá đà riêng nằm cạnh cơ chế sinh ra nó trong `expression`.
- `expression` thay tên `at_menh` vì toàn bộ bộ dữ liệu này luôn xét tại Mệnh.

Không biến khuynh hướng thành năng lực: dùng lời xử lý bất đồng không có nghĩa
nói giỏi; theo việc không bảo đảm thành công; cân nhắc giá trị không chứng minh
đạo đức hơn người. Riêng Tử Phù, giả thuyết nhận thức–thực hiện là cách diễn giải
mới để thử nghiệm, không phải bản dịch tương đương của nhận định “chịu thiệt”.

**Trạng thái nội dung:** schema đã chốt; bốn nhóm/mười hai sao đã có bản đầu dựa
trên nghiên cứu người dùng. Nội dung chi tiết còn cần thảo luận và rà chỉnh.

## 4. Thân cư và Tật Ách

### Thân cư: luôn xem xét, chỉ sử dụng khi hữu ích

Mệnh là Thể, Thân là Dụng theo cách giản lược. Chỉ lấy cung mà Thân cư:

| Thân cư | Hướng vận dụng |
|---|---|
| Mệnh | Phát triển, thể hiện bản thân |
| Quan Lộc | Công việc, thành tựu, trách nhiệm |
| Tài Bạch | Nguồn lực, tài chính, tự chủ vật chất |
| Thiên Di | Môi trường bên ngoài, xã hội, trải nghiệm |
| Phu Thê | Gắn bó, đồng hành, cam kết |
| Phúc Đức | Đời sống tinh thần, giá trị cá nhân, bình ổn nội tâm |

Tên lĩnh vực không phải kết luận về tham vọng, năng lực hoặc thành công.
Không đọc thêm chính tinh, phụ tinh, Thái Tuế hay tam phương của Thân. Khi Thân
cư trùng cung nền, không tính evidence hai lần. Chỉ đưa ảnh hưởng vào bài nếu
làm pattern cụ thể hoặc có ý nghĩa hơn; không tạo section riêng.

### Tật Ách: bổ sung có điều kiện

Chỉ gọi tool sau khi đã hình thành pattern nền, xét Thân cư và thử giải thích
tension bằng dữ kiện đã có. Cần đủ ba điều kiện:

1. Có tension đáng chú ý vẫn chưa rõ.
2. Có lý do cụ thể để góc nội tâm giúp làm rõ.
3. Dữ kiện bổ sung có thể tăng giá trị, không chỉ tăng độ dài/phức tạp.

Tool nhận `reason` ngắn, trả chính tinh/trạng thái, Tuần/Triệt tại Tật Ách và
nghĩa chung của chính tinh. Không lấy phụ tinh, tam phương hay chương bệnh tật.
Chưa có nguồn diễn giải nội tâm chuyên biệt được duyệt: nghĩa sao chung không
phải bằng chứng về tiềm thức. Không suy bệnh tật thành tâm lý, chẩn đoán hoặc
khẳng định động cơ vô thức. Không phù hợp thì bỏ qua, giữ pattern ban đầu.

Có thể hỗ trợ câu gợi mở cuối, nhưng không bắt buộc. Không tạo section Tật Ách,
không cố giải thích mọi mâu thuẫn, không viết “sâu bên trong bạn thực ra…”.

## 5. Cấu trúc code và luồng chạy

```text
personality_overview/
├── agent.py                 instruction, build agent, run structured/rendered
├── input/
│   ├── __init__.py          PERSONALITY_OVERVIEW_INPUT
│   ├── tanbien.py           evidence, Thân cư, tool tra nghĩa và Tật Ách
│   └── thai_tue.py          bộ diễn giải Thái Tuế riêng
├── output/
│   └── overview.py          schema, output instruction, renderer
├── __init__.py              public API
├── README.md                hướng dẫn sử dụng
└── DESIGN.md                tài liệu này
```

Dùng `WorkflowInputDefinition` / `WorkflowOutputInstruction` trong
`src/agent/workflow/contracts.py`, không phải contract lưu lịch sử chat trong
`api/chat/contracts.py`. Một input/output cố định; chưa cần registry, ontology
hoặc thêm dependency.

```text
get_personality_overview_evidence
  → Mệnh + Tài Bạch/Quan Lộc tam hợp + Thiên Di xung chiếu
    + Thái Tuế mới + vị trí Thân cư
  → get_personality_overview_meaning cho chính tinh làm căn cứ
  → tổng hợp pattern, cân nhắc bối cảnh Thân cư
  → tùy nhu cầu: get_personality_overview_tat_ach_evidence(reason)
  → PersonalityOverview → renderer → bốn phần Markdown
```

Input ban đầu không đọc sách, không lấy Tật Ách. Tool tra nghĩa kiểm tra yếu tố
thực sự thuộc chính tinh/Tuần–Triệt của cung nền được chọn. Chỉ đọc nghĩa chung
và nghĩa Mệnh nếu sao thực sự ở Mệnh; không lấy nghĩa cung nghề nghiệp/tài chính
rồi chuyển thành tính cách. Dùng `BookIndex.get_record()` đọc đúng mục và giữ
section ID/breadcrumb, không đưa toàn bộ nội dung mục cha vào context.

Thiếu nguồn/mục/nội dung được trả trong `missing`, không tự bù kiến thức. Mapping
hiện chưa có mục chung/Mệnh cho Tuần/Triệt; quy tắc giản lược của chúng nằm trong
instruction và không được trình bày như trích sách.

`build_personality_overview_agent(model)` dùng `TuviAgentDeps` hiện có và
`PromptedOutput(PersonalityOverview)`, cùng cơ chế JSON qua prompt như
`strength_weakness`, tránh yêu cầu output qua tool không tương thích Qwen thinking.
`run_personality_overview_agent()` trả model dữ liệu; `run_personality_overview_workflow()`
render từ model đó. Cả hai nhận `agent`, `deps`, `request`, tùy chọn `usage` và
`message_history`. Không có lượt LLM viết lại bài. Ví dụ chạy ở [README](README.md).

## 6. Output và mức bảo đảm

| Field | Phần hiển thị | Yêu cầu |
|---|---|---|
| `net_chu_dao` | Nét chủ đạo | Một đoạn ngắn, một pattern |
| `bieu_hien_thuong_thay` | Biểu hiện thường thấy | 2–3 biểu hiện cụ thể của pattern |
| `mat_con_lai` | Mặt còn lại | Tension/cái giá của cùng đặc điểm |
| `mot_dieu_dang_de_y` | Một điều đáng để ý | Một câu mở góc quan sát mới, không kiểm tra đúng/sai hoặc yêu cầu trả lời |

Viết tiếng Việt phổ thông, gọi người dùng là “bạn”, chỉ dùng thuật ngữ Tử Vi khi
cần để hiểu nhận định. Không thêm section, không lộ evidence ID/suy luận nội bộ.

**Code bảo đảm:** dữ kiện được lọc theo loại/cung/lớp natal, lý do Tật Ách không
rỗng, output đúng bốn field không rỗng, danh sách có 2–3 mục, renderer cố định.

**Instruction yêu cầu, cần đánh giá bằng model thật:** gọi input trước, tra nghĩa
khi cần kết luận, chỉ gọi Tật Ách khi hữu ích và tối đa một lần, một pattern nhất
quán, tension liên quan, câu cuối đúng một câu và có góc nhìn mới. Hiện chưa có
state machine hoặc validator ngữ nghĩa cưỡng chế các yêu cầu này.

## 7. Trạng thái, kiểm tra và việc tiếp theo

- Đã triển khai standalone. Chưa nối main agent, CLI, API hoặc frontend. Các
  workflow cũ giữ nguyên; không tự thay thế workflow `personality` hiện có.
- Lần kiểm tra triển khai gần nhất: **26 test qua**, gồm bộ mới và regression
  của personality/Thái Tuế. Chưa đánh giá chất lượng bằng model thật.
- Khi triển khai, checkout thiếu `data/tuvitanbien_chunking`; cần kiểm tra lại
  môi trường hoặc truyền `book_root` có dữ liệu trước khi đánh giá có nguồn sách.

Chạy từ repo root:

```sh
rtk proxy .venv/bin/python -m pytest tests/test_agent_personality_overview_workflow.py tests/test_agent_vong_thai_tue.py tests/test_agent_personality_workflow.py tests/test_agent_personality_tools.py -q
```

Tests dùng lá số thật để kiểm tra phép chiếu dữ liệu, nguồn sách tổng hợp để
kiểm tra retrieval, model mô phỏng để kiểm tra tool/JSON/retry. Chúng không xác
nhận giá trị luận giải hoặc chứng minh model tự chọn Tật Ách đúng lúc.

Thứ tự tiếp tục đề xuất:

1. Rà nội dung Thái Tuế cùng người dùng, bắt đầu một nhóm/ba sao; giữ rõ phần
   chung và phần riêng, đặc biệt giả thuyết Tử Phù.
2. Chốt nguồn/cách đọc nội tâm của Tật Ách trước khi tăng vai trò của nó.
3. Đánh giá bằng model thật trên chính tinh đơn/đôi, Vô Chính Diệu, Tuần/Triệt,
   Thân cư khác nhau, và trường hợp Tật Ách hữu ích/không hữu ích. Kiểm tra cả
   độ ngắn, cụ thể, không khẳng định năng lực/thành quả, và câu gợi mở.
4. Khi nội dung ổn mới bàn cách tích hợp main agent/chat và điều hướng với
   workflow personality cũ. Không thêm hạ tầng mở rộng chỉ để dự phòng.
