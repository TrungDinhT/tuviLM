# TuviLM

See the [API guide](apps/api/README.md) and [frontend guide](apps/web/README.md)
for application setup.

Chọn model khi chạy workflow bằng `--model` (trước hoặc sau `run`):

```bash
uv run tuvilm --model openrouter:qwen/qwen3.8-flash run data/workflow_profiles.yaml --workflow strength_weakness
```

Nếu bỏ qua `--model`, CLI dùng `TUVILM_WORKFLOW_MODEL` hoặc model mặc định.

Mở dashboard riêng cho workflow điểm mạnh–điểm yếu:

```bash
uv run tuvilm view
```

Dashboard tự tìm `reports/strength_weakness*.yaml` / `.yml`. Chọn nhiều lần chạy trong sidebar hoặc upload nhiều report để đối chiếu model. Để mở sẵn một report:

```bash
uv run tuvilm view reports/strength_weakness_qwen3.8-flash.yaml --port 8501
```

Ba phần của dashboard:

- **Hồ sơ từng người:** đọc tổng quan, điểm mạnh, điểm yếu, luận giải và metric từng hồ sơ cạnh nhau giữa các model.
- **Token & thời gian:** input, output, thinking, total, cache, requests, tool calls, thời gian batch và latency từng người. Thinking nằm trong output; metric thiếu hiển thị trống.
- **So sánh độ đa dạng:** số nhãn khác nhau, độ rộng trong mỗi người, Jaccard giữa người, mức tập trung top 3, tần suất nhãn và ma trận trùng lặp. Có kỳ vọng chính xác khi chỉ giữ 2 nhận định/người để kiểm soát độ dài danh sách.

So sánh dùng phần giao của các hồ sơ thành công, ghép bằng tên, ngày sinh, giờ sinh và giới tính. Số liệu gốc và chuẩn hóa được hiển thị riêng; các số chuẩn hóa không tính nếu có người dưới 2 nhận định. Đa dạng không phải thước đo tính đúng của luận giải.

Năng lực dùng ontology hiện tại. Chủ đề điểm yếu dùng nhãn thủ công đã review trong `data/strength_weakness_review_annotations.json`, kiểm tra SHA-256 của report và tên nhận định trước khi áp dụng. Report mới vẫn đọc được, nhưng chưa có metric chủ đề điểm yếu cho tới khi được review và bổ sung bộ nhãn; không tự suy ra sự khác biệt ngữ nghĩa từ tên gọi.

Có thể xuất bảng metric và độ đa dạng thành CSV. Viewer chỉ đọc file, không gọi model.

## Bootstrap an administrator

Administrator access is granted by a private server-side script, not a public
signup option or API. The script promotes an existing account; it
does not create password hashes or change the account's plan, balance or email
verification status.

1. Register an account at `/register` using an email you control and a strong,
   unique password, then open the confirmation link sent to that email. The app
   does not let an unverified email/password account sign in.
2. On a trusted machine with private MongoDB access, run the script from the
   repository root. First check that the `.env` values `AUTH__MONGO_URI` and
   `AUTH__DATABASE_NAME` point to the database the API uses.

   ```bash
   uv sync
   uv run python -m tuvi_api.auth.bootstrap_admin --email admin@example.com
   ```

3. The script finds the account by email; you do not need to look up a user ID.
   Check the printed database, email and user ID, then type the full email to
   confirm. The script revokes existing sessions **before** granting the admin
   role. A missing account, duplicate email or cancelled confirmation does not
   change data. Email matching ignores leading/trailing spaces and letter case.
4. Sign in again and open `/admin/redeem-codes`, or use the admin link in your
   profile. Choose the coin amount, code type and lifetime to create a code.

The script never asks for or prints a password; use the password you registered.
An already-admin account is left unchanged. The script works on standalone
MongoDB as well as replica sets, without adding a dependency. Session revocation
and role promotion are separate writes: run it before using the new account,
without concurrent sign-ins. If a database write fails, inspect the account role
before retrying; sessions may already have been revoked.

Keep MongoDB private and authenticated in production. Never expose this script
through an HTTP route, run it during startup, or store database credentials in Git.

Coin redemption itself requires a MongoDB replica set; see the
[redemption requirements](apps/api/README.md#coin-redemption-codes).
