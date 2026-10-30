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
| Miếu/Vượng/Đắc/Bình/Hãm của từng chính tinh | Temperament Condition: điều chỉnh cách khí chất vận hành | Đọc theo từng sao và nguồn sách, không quy thành tăng/giảm cường độ hoặc điểm số |
| Vòng Thái Tuế tại Mệnh | Tư thế sống trước hoàn cảnh và cách biểu hiện | Bổ sung cho chính tinh, không thành một chân dung độc lập |
| Tuần/Triệt tại Mệnh/Thân | Điều chỉnh cách khí chất biểu hiện/vận dụng | Không coi là một kiểu tính cách riêng, không lấy từ cung hội chiếu để luận Mệnh |
| Chính tinh xung chiếu/tam hợp Mệnh | Hiểu và điều chỉnh khí chất Mệnh; quan trọng hơn khi Vô Chính Diệu | Chỉ chính tinh, không thêm trait độc lập hoặc đổi sao chiếu thành sao tọa Mệnh |
| Thân cư cùng chính tinh, trạng thái, Tuần/Triệt tại Thân | Hướng và phương thức vận dụng khí chất (Dụng) | Không tạo chân dung thứ hai; không xét tam phương hoặc Thái Tuế tại Thân |
| Tật Ách | Góc khám phá nội tâm thử nghiệm, có điều kiện | Không lấy mặc định, không luận bệnh/tai ách/tiềm thức chắc chắn |

Tuần thường kìm, làm chậm hoặc tiết chế. Triệt thường ngăn, cắt, tạo gián đoạn
hoặc khiến xu hướng khó biểu hiện trực tiếp. Cả hai có thể giảm biểu hiện quá
cực đoan. Đây là quy tắc giản lược do người dùng cung cấp.

**Temperament Condition:** đắc không có nghĩa tăng cường độ, hãm không có nghĩa
giảm cường độ; hãm có thể làm đặc tính thiếu cân bằng hoặc biểu hiện theo chiều
hướng khác. Đọc điều kiện riêng từng sao qua các đoạn sách trong evidence, không hardcode
thêm bảng ý nghĩa hay công thức chung. Với hai chính tinh đồng cung, xét trạng
thái từng sao trước khi tổng hợp, không dùng trạng thái chung hoặc trung bình.
Áp dụng cho chính tinh tại Mệnh, hội chiếu và Thân. Thiếu trạng thái/nguồn phù
hợp thì giữ giới hạn, không tự gán trạng thái hoặc bù ý nghĩa.

**Cấu trúc tinh hệ:** Mệnh là trọng tâm; đọc bộ đồng cung và các quan hệ hội
chiếu như một cấu trúc liên kết. Không cộng dồn đặc tính, không xem các quan hệ
an sao vốn đi cùng nhau là nhiều bằng chứng độc lập. Một sao nằm trong nhiều
bộ/quan hệ vẫn là cùng dữ kiện; tên bộ không tự xác nhận cách cục hoặc ý nghĩa.
Nguyên tắc này nằm trong instruction, không sử dụng `input/tinh_he.py`.

**Mệnh Vô Chính Diệu:** nhánh riêng, trong đó cấu trúc chính tinh xung chiếu/
tam hợp và trạng thái từng sao có vai trò quan trọng hơn, kết hợp vòng Thái Tuế
và Tuần/Triệt tại Mệnh. Không mượn một chính tinh thay thế Mệnh; không kết luận
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
  `core_question`; tinh thần và câu hỏi nền được làm rõ trong instruction để
  định hướng suy luận, không ép kết luận theo một nhãn/câu hỏi cố định.
- Bỏ `reading_lens` nhóm: các quy tắc chung nằm trong instruction; góc riêng
  đã được mô tả trong `overview`.
- Bỏ `keywords` để tránh cộng tính từ. Không tách `shadow` sao vì dễ lặp
  `tension`; mặt quá đà riêng nằm cạnh cơ chế sinh ra nó trong `expression`.
- `expression` thay tên `at_menh` vì toàn bộ bộ dữ liệu này luôn xét tại Mệnh.

Instruction bổ sung bốn hướng đọc nội bộ, giữ nguyên schema nhóm/sao:

- **Tuế Hổ Phù:** “Tôi có quyền và trách nhiệm phải làm.” → Tôi nên làm gì và
  chịu trách nhiệm thế nào?
- **Tang Tuế Khách:** “Thực tại này có gì đó không ổn.” → Điều gì trong hiện
  trạng cần thay đổi?
- **Dương Tử Phúc:** “Tôi có thể nhìn ra một cách đi khác.” → Tôi nhìn thấy
  khả năng nào và sẽ làm gì với nó?
- **Âm Long Trực:** “Tôi thích nghi hơn là áp đặt.” → Tôi điều chỉnh mình và
  giữ cân bằng thế nào?

Đây không phải kết luận bắt buộc, nhãn tính cách hay câu hỏi gửi người dùng.
Chỉ đọc nhóm thực sự có tại Mệnh, kết hợp `expression`/`reading_hint` và khí
chất nền; không dùng câu hỏi nền làm Reflection Lens mặc định.

Không biến khuynh hướng thành năng lực: dùng lời xử lý bất đồng không có nghĩa
nói giỏi; theo việc không bảo đảm thành công; cân nhắc giá trị không chứng minh
đạo đức hơn người. Riêng Tử Phù, giả thuyết nhận thức–thực hiện là cách diễn giải
mới để thử nghiệm, không phải bản dịch tương đương của nhận định “chịu thiệt”.

**Trạng thái nội dung:** schema đã chốt; bốn nhóm/mười hai sao đã có bản đầu dựa
trên nghiên cứu người dùng. Nội dung chi tiết còn cần thảo luận và rà chỉnh.

## 4. Thân cư và Tật Ách

### Thân cư: luôn xem xét, chỉ sử dụng khi hữu ích

**Mệnh (Thể)** là khí chất và khuynh hướng tự nhiên. **Thân (Dụng)** là hướng
và phương thức vận dụng khí chất. Vị trí Thân cư cho biết lĩnh vực:

| Thân cư | Hướng vận dụng |
|---|---|
| Mệnh | Phát triển, thể hiện bản thân |
| Quan Lộc | Công việc, thành tựu, trách nhiệm |
| Tài Bạch | Nguồn lực, tài chính, tự chủ vật chất |
| Thiên Di | Môi trường bên ngoài, xã hội, trải nghiệm |
| Phu Thê | Gắn bó, đồng hành, cam kết |
| Phúc Đức | Đời sống tinh thần, giá trị cá nhân, bình ổn nội tâm |

`than_cu.palace` bổ sung chính tinh/bộ chính tinh, trạng thái từng sao và
Tuần/Triệt tại cung Thân, dùng lại `PalaceEvidence`. Evidence tự đọc nghĩa
chung và mục Mệnh/Thân của chính tinh tại Thân vào `meanings`, liên kết bằng
`component_id` và cung thực tế trong `palace_role`;
chỉ chọn phần phù hợp với hướng/phương thức vận dụng, không lấy chương lĩnh
vực như nghề nghiệp, tài chính, hôn nhân để suy tính cách.

Tên lĩnh vực không phải kết luận về tham vọng, năng lực hoặc thành công.
Không xét thêm phụ tinh, Thái Tuế hay tam phương tứ chính của Thân. Thân không
có chính tinh thì chỉ dùng vị trí cư và Tuần/Triệt, không mượn sao hội chiếu.
Không tạo chân dung tính cách thứ hai hoặc section riêng.

Đối chiếu `position`/`component_id` để tránh double-counting: Thân trùng Mệnh
là cùng dữ kiện qua Thể–Dụng; Thân nằm trong tam phương tứ chính đã xét chỉ bổ
sung vai trò vận dụng, không cộng lại đặc tính hay tăng độ chắc chắn. Chỉ đưa
ảnh hưởng vào bài nếu làm pattern cụ thể hoặc có ý nghĩa hơn.

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
│   ├── tanbien.py           evidence kèm nghĩa sách, tool Tật Ách có điều kiện
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
    (hội chiếu chỉ chính tinh/trạng thái)
    + Thái Tuế tại Mệnh + Thân cư/chính tinh/trạng thái/Tuần–Triệt
  → tự nạp meanings cho chính tinh Mệnh/Thân; hội chiếu chỉ khi Mệnh VCD
  → nhánh có chính tinh hoặc Vô Chính Diệu; tổng hợp cấu trúc và đắc/hãm
  → cân nhắc Thể–Dụng, không đếm lại dữ kiện
  → tùy nhu cầu: get_personality_overview_tat_ach_evidence(reason)
  → chọn một Reflection Lens, viết một câu khoảng 20–40 từ
  → PersonalityOverview → renderer → bốn phần Markdown
```

Input ban đầu gồm dữ kiện lá số và `meanings: list[OverviewMeaning]`, không
lấy Tật Ách. Không còn tool `get_personality_overview_meaning` để agent tự
điều phối từng lượt đọc. Phạm vi tra sách được quyết định từ evidence đã dựng:

- Mệnh có chính tinh: đọc nghĩa chung và mục Mệnh/Thân của các chính tinh đó.
- Mệnh Vô Chính Diệu: đọc nghĩa chung của chính tinh tại cả hai cung tam hợp
  và cung xung chiếu. Không coi sao chiếu là sao tọa Mệnh.
- Thân có chính tinh: đọc nghĩa chung và mục Mệnh/Thân của chúng.
- Thân Vô Chính Diệu: không đọc thêm hoặc mượn sao hội chiếu cho Thân.

Danh sách cung cần đọc được loại trùng theo cung thực tế trước khi tra sách;
chính tinh thuộc một cung natal nên mỗi sao/cung chỉ có một `OverviewMeaning`.
Thân trùng Mệnh hoặc cung hội chiếu không tạo bản sao nghĩa sách. Mỗi meaning
liên kết với dữ kiện bằng `component_id`/`palace_role`; passages giữ section ID,
breadcrumb, content, scope và `additional_context`. Ngữ cảnh cho biết tọa
Mệnh, tam hợp/xung chiếu với Mệnh VCD hoặc tọa Thân; khi trùng cung thì gộp
các ngữ cảnh trong cùng passage, không nhân đôi nguồn. Mục Mệnh/Thân dùng scope `menh` nếu ở Mệnh,
`than` nếu ở Thân khác Mệnh; nghĩa chung dùng `generic`. Agent đối chiếu vai trò
với evidence, không coi cùng nguồn là các bằng chứng độc lập.

Dữ kiện chính tinh/trạng thái hội chiếu vẫn được giữ khi Mệnh có chính tinh,
nhưng không đọc thêm sách cho chúng (trừ cung cũng là Thân). Chúng cung cấp
bối cảnh cấu trúc; không tự bù ý nghĩa sao từ kiến thức model khi thiếu nguồn.
Cung hội chiếu giữ `tuan_triet=[]`; nếu cũng là Thân thì Tuần/Triệt nằm trong
`than_cu.palace` với vai trò Dụng.

Dùng `BookIndex.get_record()` đọc đúng mục đã ánh xạ, không đưa nội dung mục
cha hoặc chương nghề nghiệp/tài chính/hôn nhân vào context. Không tính lại vị
trí Thân hay dựng lại cung để tra từng sao. Thiếu nguồn/mục/nội dung được trả
trong `missing`, không tự bù kiến thức. Không tra sách cho phụ tinh hay
Tuần/Triệt; quy tắc giản lược Tuần/Triệt nằm trong instruction và không được
trình bày như trích sách. Tật Ách vẫn có tool riêng và chỉ đọc nghĩa sao chung.

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
| `mot_dieu_dang_de_y` | Một điều đáng để ý | Một câu khoảng 20–40 từ, chỉ chọn một góc quan sát mới, không yêu cầu trả lời |

Viết tiếng Việt phổ thông, gọi người dùng là “bạn”, chỉ dùng thuật ngữ Tử Vi khi
cần để hiểu nhận định. Không thêm section, không lộ evidence ID/suy luận nội bộ.

**Reflection Lens:** agent chủ động chọn một hướng phù hợp nhất: điều kiện
xuất hiện; ngoại lệ/mặt đối lập; khoảng cách suy nghĩ–hành động; động cơ dưới
hành vi nếu có căn cứ; khác biệt giữa các lĩnh vực; hoặc ảnh hưởng tới quan hệ.
Không ghép nhiều hướng, lặp kết luận hoặc thêm nhận định tâm lý thiếu căn cứ.
Không kiểm tra đúng/sai, không khẳng định động cơ vô thức, không yêu cầu trả lời.
Giữ nguyên bốn field, renderer và độ ngắn của free layer; 20–40 từ là hướng
dẫn viết, không thêm bộ đếm từ/câu cứng vào validator.

**Code bảo đảm:** dữ kiện được lọc theo loại/cung/lớp natal, lý do Tật Ách không
rỗng, phạm vi sách được nạp theo nhánh Mệnh/Thân và loại trùng cung,
output đúng bốn field không rỗng, danh sách có 2–3 mục, renderer cố định.

**Instruction yêu cầu, cần đánh giá bằng model thật:** gọi input trước, chọn
đoạn sách phù hợp trong meanings, chỉ gọi Tật Ách khi hữu ích và tối đa một lần, một pattern nhất
quán, đắc/hãm theo từng sao, không đếm trùng tinh hệ/Thân, tension liên quan,
câu cuối một hướng, đúng một câu khoảng 20–40 từ và có góc nhìn mới. Hiện chưa có
state machine hoặc validator ngữ nghĩa cưỡng chế các yêu cầu này.

## 7. Trạng thái, kiểm tra và việc tiếp theo

- Đã triển khai standalone. Chưa nối main agent, CLI, API hoặc frontend. Các
  workflow cũ giữ nguyên; không tự thay thế workflow `personality` hiện có.
- Kiểm tra ngày 2026-10-17: **41 test qua**. Gồm projection/trạng thái từng sao,
  sáu vị trí Thân cư và dữ kiện
  trùng Mệnh/hội chiếu, nạp sách theo nhánh Mệnh/Thân/VCD, loại trùng nguồn,
  instruction và regression của
  personality/Thái Tuế. Chưa đánh giá chất lượng bằng model thật.
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
