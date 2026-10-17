# Personality Overview — thiết kế và bàn giao

Cập nhật: 2026-11-13. Tài liệu ghi lại mục tiêu, quyết định và contract hiện
hành. Xem [README.md](README.md) để chạy workflow và kiểm tra.

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

Thứ tự trong cùng Personality Agent: **Mệnh → Thái Tuế → Thân →
Tuần/Triệt → narrative**. Đây là framework tổng hợp của tuviLM, không khẳng
định là quy tắc nguyên văn của một trường phái.

- Mệnh: khí chất và động lực nền từ đúng một tinh hệ đã chọn.
- Thái Tuế: lập trường, thái độ và tư thế ứng xử; phân biệt nhóm với sao.
- Thân: phương thức vận dụng theo Thể–Dụng; không tạo bản ngã thứ hai.
- Tuần/Triệt: constraint cuối, chỉ adjust/qualify khi có quy tắc đủ điều kiện;
  thiếu quy tắc thì no_change. Không đảo cực hoặc làm suy yếu chung.
- Tật Ách nằm ngoài phạm vi Personality Overview; không có tool bổ sung.

Không dùng Tứ Hóa, phụ tá/sát tinh và phụ tinh khác, luận riêng Phúc Đức,
vận hạn hoặc dự đoán sự kiện/nghề nghiệp/sức khỏe/tình cảm. Sao Phúc Đức thuộc
vòng Thái Tuế và bối cảnh Thân cư Phúc Đức vẫn nằm trong phạm vi đã định nghĩa.
Không có bước đánh giá Miếu/Vượng/Đắc/Bình/Hãm độc lập: phân loại tinh hệ đã
phản ánh cấu hình và vị trí. Giữ địa chi thực tế; chỉ phân biệt hai vị trí
khi knowledge nói rõ, không tự tạo khác biệt.

Mệnh VCD giữ nhánh riêng, được tham khảo đối cung/tam hợp nếu có quy tắc đã
cấp. Không mượn nguyên tinh hệ đối cung hoặc coi VCD là thiếu cá tính. Nếu
thiếu tri thức nền thì nêu giới hạn. Quy tắc cấu trúc VCD về Tuần/Triệt, nếu
được cấp và đủ điều kiện, cần dùng ngay ở bước Mệnh rồi tránh áp lần hai.
Dữ kiện Mệnh thiếu phải báo lỗi, không được coi là VCD.

### Context 60 tinh hệ Trung Châu

[input/trung_chau.py](input/trung_chau.py) định nghĩa schema, bộ chọn và chỉ
dẫn sử dụng nghiên cứu [60 tinh hệ](tuviLM_60_tinh_he_merged.md). 60 bản ghi
`InterpretationBasis` được khai báo trực tiếp bằng Python và validate bằng
Pydantic. `chinh_tinh` là `frozenset[str]` chứa ID sao; `dia_chi` là cặp enum
`DiaChi`. Khóa tra cứu là tập ID sao và địa chi thực tế, không cần `system_id`
hoặc JSON đi kèm. Test đối chiếu từng trường với Markdown để giữ hai bản đồng bộ.

- `menh.interpretation`: một bản ghi khớp toàn bộ chính tinh tọa Mệnh và cặp địa
  chi, không phụ thuộc thứ tự sao. Cấu hình có chính tinh nhưng không khớp
  bản ghi sẽ báo `ModelRetry`; không tự coi là VCD.
- Mệnh VCD: bản ghi là `null`; tham khảo xung chiếu/tam hợp trong giới hạn knowledge,
  không bê nguyên tinh hệ của đối cung vào Mệnh.
- `core_temperament` làm nền; `personality_mechanism` gợi cơ chế;
  `observable_hypothesis` gợi biểu hiện; `weakness` gợi mặt đánh đổi có điều kiện.
  Các trường này cùng một nguồn, không xác nhận lẫn nhau.
- `axis_classical_vi` và `axis_interpretation` làm rõ hai hướng biểu hiện,
  không tự chọn cực từ đắc/hãm, Tuần/Triệt hoặc gắn nhãn tốt/xấu.
- `than.basic_combination_id`: ID ghép các chính tinh thực tế tọa Thân theo
  thứ tự tên ID, hoặc `null` khi Thân VCD. Chỉ dùng cùng hướng Thân cư và
  knowledge đã cấp, không áp toàn bộ tinh hệ Mệnh hay mở thêm hội chiếu.

Nội dung là khung Tử Vi truyền thống kèm giả thuyết biên soạn, không phải mô
hình tâm lý học thực chứng. Chỉ điều chỉnh biểu hiện theo dữ kiện thực sự có
trong tool; không tự thêm Tứ Hóa, phụ tinh hoặc quy tắc nhân quả chưa cung cấp.
Agent không tự bù ý nghĩa bằng kiến thức nhớ sẵn.

Workflow không tra sách Tân Biên. Không cần `BookIndex`,
`book_root` hoặc dữ liệu chunking. Các workflow khác vẫn có thể dùng sách
qua deps dùng chung.

## 3. Vòng Thái Tuế: quyết định quan trọng

**Không sửa `packages/tuvi-agent/src/tuvi_agent/tool/thai_tue/vong_thai_tue.py`.** Người dùng yêu cầu giữ
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

Instruction chỉ đọc nhóm/sao thực sự được cấp, kết hợp `overview`,
`expression` và `reading_hint` với khí chất nền. Không gán khẩu hiệu chung
cho mọi sao trong nhóm hoặc dùng tên nhóm để tự suy ý nghĩa.
Thiếu nghĩa sao hoặc nhóm trong dữ liệu nội bộ thì trả `null`, tiếp tục từ
các lớp còn có căn cứ.

Không biến khuynh hướng thành năng lực: dùng lời xử lý bất đồng không có nghĩa
nói giỏi; theo việc không bảo đảm thành công; cân nhắc giá trị không chứng minh
đạo đức hơn người. Riêng Tử Phù, giả thuyết nhận thức–thực hiện là cách diễn giải
mới để thử nghiệm, không phải bản dịch tương đương của nhận định “chịu thiệt”.

**Trạng thái nội dung:** schema đã chốt; bốn nhóm/mười hai sao đã có bản đầu dựa
trên nghiên cứu người dùng. Nội dung chi tiết còn cần thảo luận và rà chỉnh.

## 4. Thân cư

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

`than.palace` giữ dữ kiện chính tinh tại cung Thân, không truyền trạng thái
đắc/hãm. Tuần/Triệt tại Thân nằm riêng trong `tuan_triet.than`.
`than.basic_combination_id` nhận diện tổ hợp sao tại đây, đọc cùng lĩnh vực
và hướng vận dụng của `than`, không dựng chân dung thứ hai.

Tên lĩnh vực không phải kết luận về tham vọng, năng lực hoặc thành công.
Không xét thêm phụ tinh, Thái Tuế hay tam phương tứ chính của Thân. Thân không
có chính tinh thì chỉ dùng vị trí cư và Tuần/Triệt, không mượn sao hội chiếu.
Không tạo chân dung tính cách thứ hai hoặc section riêng.

Đối chiếu `position`/`component_id` để tránh double-counting: Thân trùng Mệnh
là cùng dữ kiện qua Thể–Dụng; Thân nằm trong tam phương tứ chính đã xét chỉ bổ
sung vai trò vận dụng, không cộng lại đặc tính hay tăng độ chắc chắn. Chỉ đưa
ảnh hưởng vào bài nếu làm pattern cụ thể hoặc có ý nghĩa hơn.

## 5. Cấu trúc code và luồng chạy

```text
personality_overview/
├── agent.py                 instruction, build agent, run structured/rendered
├── input/
│   ├── __init__.py          PERSONALITY_OVERVIEW_INPUT
│   ├── evidence.py          dữ kiện nền và context theo vai trò
│   ├── trung_chau.py        schema, bộ chọn và instruction 60 tinh hệ
│   └── thai_tue.py          bộ diễn giải Thái Tuế riêng
├── output/
│   └── overview.py          schema, output instruction, renderer
├── __init__.py              public API
├── tuviLM_60_tinh_he_merged.md    nguồn nội dung nghiên cứu
├── tuviLM_60_tinh_he_personality_research.md  tài liệu nghiên cứu bổ sung
├── README.md                hướng dẫn sử dụng
└── DESIGN.md                tài liệu này
```

Dùng `WorkflowInputDefinition` / `WorkflowOutputInstruction` trong
`packages/tuvi-agent/src/tuvi_agent/workflow/contracts.py`, không phải contract lưu lịch sử chat trong
`apps/api/src/tuvi_api/chat/contracts.py`. Một input/output cố định; chưa cần registry, ontology
hoặc thêm dependency.

```text
Existing chart + existing Trung Châu selector + existing Thái Tuế meanings
  → get_personality_overview_evidence
      menh: vị trí, sao, bản ghi knowledge, VCD support nếu cần
      thai_tue: vị trí, nghĩa sao và nhóm nếu có
      than: vị trí cư, bối cảnh vận dụng, basic_combination_id, same_as_menh
      tuan_triet: vị trí Mệnh/Thân chịu ảnh hưởng, placements, applicable_constraints
  → .model_dump_json() qua hook instructions trước model request
  → một agent tổng hợp A–E và trả PersonalityOverview
  → renderer Markdown, không gọi model viết lại
```

Getter trả thẳng `PersonalityOverviewEvidence` gồm bốn nhóm theo vai trò;
đây là schema duy nhất được serialize cho agent. Không có bước dựng lại
dictionary context, không thêm module, tầng knowledge hoặc cơ chế retrieval.
Schema không chứa trạng thái đắc/hãm và giới tính, chỉ có xung chiếu/tam hợp
khi Mệnh VCD. Các caller đọc trực tiếp `menh`, `thai_tue`, `than`, `tuan_triet`.
Agent không đăng ký function tool. Context được chuẩn bị trước model request;
Tật Ách không được truy xuất hoặc sử dụng.

Dynamic instructions dùng deps của lượt chạy hiện tại, tránh giữ context lá
số cũ khi tái dùng agent/history. Thư viện có thể dựng lại instructions ở
request retry; phép chọn vẫn từ static knowledge hiện có.

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
| `bieu_hien_thuong_thay` | Biểu hiện thường thấy | 1–2 biểu hiện có căn cứ của cùng khí chất |
| `mat_con_lai` | Mặt còn lại | Tension/cái giá của cùng đặc điểm |
| `mot_dieu_dang_de_y` | Một điều đáng để ý | Một câu khoảng 20–40 từ, xuất phát từ khí chất và mặt đánh đổi đã phân tích, không yêu cầu trả lời |

Viết tiếng Việt phổ thông, gọi người dùng là “bạn”, chỉ dùng thuật ngữ Tử Vi khi
cần để hiểu nhận định. Không thêm section, không lộ evidence ID/suy luận nội bộ.

**Reflection Lens:** agent chủ động chọn một hướng phù hợp nhất: điều kiện
xuất hiện; ngoại lệ/mặt đối lập; khoảng cách suy nghĩ–hành động; động cơ dưới
hành vi nếu có căn cứ; khác biệt giữa các lĩnh vực; hoặc ảnh hưởng tới quan hệ.
Không ghép nhiều hướng, lặp kết luận hoặc thêm nhận định tâm lý thiếu căn cứ.
Không kiểm tra đúng/sai, không khẳng định động cơ vô thức, không yêu cầu trả lời.
Giữ nguyên bốn field, renderer và độ ngắn của free layer; 20–40 từ là hướng
dẫn viết, không thêm bộ đếm từ/câu cứng vào validator.

**Code bảo đảm:** dữ kiện được lọc theo loại/cung/lớp natal, context Trung Châu
được chọn theo chính tinh và vị trí Mệnh, không truy xuất sách;
Tật Ách không nằm trong context và agent không có function tool;
output đúng bốn field không rỗng, danh sách có 1–2 mục, renderer cố định.

**Instruction yêu cầu, cần đánh giá bằng model thật:** tổng hợp theo A–E,
một pattern nhất quán, không tự phân cực, không đếm trùng tinh hệ/Thân, tension liên quan,
câu cuối một hướng, đúng một câu khoảng 20–40 từ và có góc nhìn mới. Hiện chưa có
state machine hoặc validator ngữ nghĩa cưỡng chế các yêu cầu này.

## 7. Giới hạn knowledge đang cấp

- Mệnh VCD có dữ kiện đối cung/tam hợp, chưa có tri thức nền đủ điều kiện
  trong context để xác lập khí chất. Phải nêu giới hạn thay vì mượn nguyên đối cung.
- Thân có bối cảnh cư và ID tổ hợp, chưa có knowledge cơ chế riêng của tổ hợp.
  ID không tự cung cấp ý nghĩa; dùng phần bối cảnh có nguồn, không tự ghép sao.
- `applicable_constraints` hiện rỗng: evidence chưa cấp quy tắc Tuần/Triệt đã
  khớp điều kiện trong phạm vi. Vì vậy dùng no_change. Tài liệu tổng quát tại
  `data/knowledge/` không đồng nghĩa có quy tắc runtime đã xác thực; không tự
  nạp thêm hay suy Chính Không/Bàng Không.

## 8. Trạng thái, kiểm tra và việc tiếp theo

- Đã triển khai standalone và CLI. Chưa nối main agent, API hoặc frontend;
  không tự thay thế workflow `personality` hiện có.
- Tests đối chiếu đủ 60 bản ghi với Markdown, kiểm tra bộ chọn qua 12 vị trí
  Tử Vi × 12 vị trí Mệnh, Mệnh/Thân VCD, thứ tự sao và cấu hình không hợp lệ.
  Tests workflow kiểm tra dữ kiện lá số, phạm vi, không đọc sách và không
  truy xuất Tật Ách. Model mô phỏng kiểm tra agent không có function tool,
  một request khi output hợp lệ, retry JSON khi output chưa hợp lệ, và context
  mới khi tái dùng history. Chưa đánh giá bằng model thật hoặc kiểm chứng tâm lý.
- Không cần dữ liệu `tuvitanbien_chunking` cho Personality Overview. Deps và
  công cụ sách dùng chung của các workflow khác giữ nguyên.

Chạy từ repo root:

```sh
rtk proxy .venv/bin/python -m pytest tests/test_personality_overview_trung_chau.py tests/test_agent_personality_overview_workflow.py tests/test_agent_vong_thai_tue.py tests/test_agent_personality_workflow.py tests/test_agent_personality_tools.py tests/test_placement_rules.py tests/test_workflow_cli.py -q
```

Tests dùng lá số thật để kiểm tra phép chiếu dữ liệu, chặn `require_book()`
để xác nhận không tra sách và dùng model mô phỏng kiểm tra context/JSON/retry.
Chúng không xác nhận chất lượng luận giải của model thật.

Thứ tự tiếp tục đề xuất:

1. Rà nội dung Thái Tuế cùng người dùng, bắt đầu một nhóm/ba sao; giữ rõ phần
   chung và phần riêng, đặc biệt giả thuyết Tử Phù.
2. Đánh giá bằng model thật trên chính tinh đơn/đôi, Vô Chính Diệu, Tuần/Triệt,
   Thân cư khác nhau. Kiểm tra cả
   độ ngắn, cụ thể, không khẳng định năng lực/thành quả, và câu gợi mở.
3. Khi nội dung ổn mới bàn cách tích hợp main agent/chat và điều hướng với
   workflow personality cũ. Không thêm hạ tầng mở rộng chỉ để dự phòng.
