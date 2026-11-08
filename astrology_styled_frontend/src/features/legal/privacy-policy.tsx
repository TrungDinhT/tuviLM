import Link from "next/link";

const CONTACT_EMAIL = "lphuockhanh1@gmail.com";

const LINK_CLASS =
  "font-medium text-ink underline decoration-glass-line underline-offset-4 transition-colors hover:decoration-ink";

export function PrivacyPolicy() {
  return (
    <div className="min-h-dvh bg-bg-0">
      <main className="mx-auto w-full max-w-[760px] px-5 pt-[calc(28px+var(--safe-t))] pb-[calc(64px+var(--safe-b))] sm:px-8 md:pt-[calc(48px+var(--safe-t))]">
        <Link
          href="/"
          className="inline-flex min-h-11 items-center text-sm text-muted transition-colors hover:text-ink"
        >
          ← Về Thiên Hạc
        </Link>

        <header className="mt-6 border-b border-glass-line pb-8">
          <h1 className="font-display text-[clamp(34px,7vw,52px)] leading-[1.05] font-semibold tracking-[-0.03em] text-balance">
            Chính sách riêng tư
          </h1>
          <p className="mt-3 text-sm text-muted">Cập nhật lần cuối: 08/11/2026</p>
          <p className="mt-6 text-[15px] leading-[1.7] text-muted md:text-base">
            Thiên Hạc (tuvi.thienhac.app) là ứng dụng an sao và luận giải Tử Vi. Chính sách này giải
            thích chúng tôi thu thập dữ liệu gì khi bạn dùng Thiên Hạc, dùng vào việc gì, chia sẻ
            với ai và bạn có những quyền gì đối với dữ liệu của mình.
          </p>
        </header>

        <div className="mt-10 grid gap-10 text-[15px] leading-[1.7] text-muted md:text-base">
          <PolicySection title="1. Dữ liệu chúng tôi thu thập">
            <ul className="grid list-disc gap-2 pl-5">
              <li>
                <Strong>Thông tin tài khoản:</Strong> tên, địa chỉ email và mật khẩu khi bạn đăng ký
                bằng email. Mật khẩu chỉ được lưu ở dạng đã băm, chúng tôi không đọc được mật khẩu
                gốc.
              </li>
              <li>
                <Strong>Khi đăng nhập bằng Google:</Strong> tên, địa chỉ email, ảnh đại diện và mã
                định danh tài khoản Google của bạn, cùng token đăng nhập do Google cấp.
              </li>
              <li>
                <Strong>Thông tin ngày sinh:</Strong> ngày, tháng, năm sinh, giờ sinh và giới tính
                bạn nhập để an sao, cùng tên bạn đặt cho lá số đã lưu.
              </li>
              <li>
                <Strong>Nội dung trò chuyện:</Strong> câu hỏi bạn gửi cho Thiên Hạc và câu trả lời
                được tạo ra được mã hóa. Chúng tôi không đọc được nội dung cuộc trò chuyện.
              </li>
              <li>
                <Strong>Gói và xu:</Strong> gói sử dụng, số dư xu, mã nhận xu bạn đã dùng và số xu
                đã trừ cho mỗi câu hỏi.
              </li>
              <li>
                <Strong>Phiên đăng nhập:</Strong> cookie phiên, địa chỉ IP và thông tin trình duyệt
                gắn với mỗi lần đăng nhập.
              </li>
            </ul>
          </PolicySection>

          <PolicySection title="2. Chúng tôi dùng dữ liệu để làm gì">
            <ul className="grid list-disc gap-2 pl-5">
              <li>Tạo tài khoản, đăng nhập, gửi email xác minh và email đặt lại mật khẩu.</li>
              <li>An sao, hiển thị lá số và các phần luận giải dựa trên thông tin ngày sinh.</li>
              <li>Trả lời câu hỏi của bạn trong mục Hỏi AI và lưu lịch sử để bạn xem lại.</li>
              <li>Quản lý gói sử dụng và số xu của bạn.</li>
              <li>Giữ an toàn cho dịch vụ và phát hiện hành vi lạm dụng.</li>
            </ul>
            <p>
              Chúng tôi không bán dữ liệu của bạn, không dùng dữ liệu để quảng cáo và không cài công
              cụ quảng cáo hay theo dõi của bên thứ ba.
            </p>
          </PolicySection>

          <PolicySection title="3. Dữ liệu nhận từ Google">
            <p>
              Khi bạn chọn đăng nhập bằng Google, Thiên Hạc chỉ yêu cầu các quyền cơ bản{" "}
              <code className="text-ink">openid</code>, <code className="text-ink">email</code> và{" "}
              <code className="text-ink">profile</code>. Chúng tôi chỉ dùng tên, email và ảnh đại
              diện để tạo, đăng nhập và hiển thị tài khoản của bạn. Chúng tôi không truy cập Gmail,
              Google Drive, danh bạ hay bất kỳ dữ liệu Google nào khác.
            </p>
            <p>
              Dữ liệu nhận từ Google không được bán, không dùng cho quảng cáo và không được chuyển
              cho bên thứ ba, trừ các nhà cung cấp hạ tầng ở mục 4 khi cần để vận hành dịch vụ. Việc
              Thiên Hạc sử dụng và chuyển giao thông tin nhận từ Google API tuân thủ{" "}
              <a
                href="https://developers.google.com/terms/api-services-user-data-policy"
                className={LINK_CLASS}
                rel="noopener noreferrer"
                target="_blank"
              >
                Google API Services User Data Policy
              </a>
              , bao gồm các yêu cầu về Limited Use.
            </p>
            <p>
              Bạn có thể thu hồi quyền truy cập của Thiên Hạc bất cứ lúc nào tại{" "}
              <a
                href="https://myaccount.google.com/permissions"
                className={LINK_CLASS}
                rel="noopener noreferrer"
                target="_blank"
              >
                trang quản lý quyền của tài khoản Google
              </a>
              .
            </p>
          </PolicySection>

          <PolicySection title="4. Chia sẻ với bên thứ ba">
            <p>Chúng tôi chỉ chia sẻ dữ liệu với các nhà cung cấp cần thiết để vận hành dịch vụ:</p>
            <ul className="grid list-disc gap-2 pl-5">
              <li>
                <Strong>OpenRouter:</Strong> nhận câu hỏi của bạn, phần lịch sử trò chuyện liên quan
                và dữ liệu lá số (có thể gồm tên lá số, ngày giờ sinh, giới tính và vị trí các sao)
                để mô hình AI tạo câu trả lời. OpenRouter chuyển yêu cầu tới nhà cung cấp mô hình AI
                tương ứng.
              </li>
              <li>
                <Strong>Resend:</Strong> nhận tên và địa chỉ email của bạn để gửi email xác minh và
                email đặt lại mật khẩu.
              </li>
              <li>
                <Strong>Google:</Strong> xử lý việc đăng nhập khi bạn chọn đăng nhập bằng Google.
              </li>
              <li>
                <Strong>Nhà cung cấp máy chủ và cơ sở dữ liệu:</Strong> nơi lưu trữ và vận hành
                Thiên Hạc.
              </li>
            </ul>
            <p>
              Ngoài ra, chúng tôi chỉ cung cấp dữ liệu cho cơ quan nhà nước có thẩm quyền khi pháp
              luật yêu cầu.
            </p>
          </PolicySection>

          <PolicySection title="5. Cookie và bộ nhớ trình duyệt">
            <p>
              Thiên Hạc dùng một cookie phiên để giữ bạn đăng nhập. Trình duyệt của bạn cũng lưu lá
              số vừa an, tùy chọn “không nhắc lại” khi xác nhận ngày sinh và một mã định danh ẩn danh
              trong bộ nhớ cục bộ (localStorage) để ứng dụng chạy liền mạch giữa các lần mở. Bạn có
              thể xoá những dữ liệu này bằng cách xoá dữ liệu trang web trong cài đặt trình duyệt.
            </p>
          </PolicySection>

          <PolicySection title="6. Lưu trữ và bảo mật">
            <p>
              Dữ liệu được truyền qua kết nối mã hoá HTTPS và lưu trong cơ sở dữ liệu của Thiên Hạc.
              Chúng tôi giữ dữ liệu trong thời gian tài khoản của bạn còn tồn tại và xoá khi bạn yêu
              cầu xoá tài khoản, trừ trường hợp pháp luật yêu cầu lưu giữ lâu hơn.
            </p>
          </PolicySection>

          <PolicySection title="7. Quyền của bạn">
            <ul className="grid list-disc gap-2 pl-5">
              <li>Đổi tên hoặc xoá lá số đã lưu ngay trong mục Hồ sơ.</li>
              <li>
                Yêu cầu bản sao dữ liệu, chỉnh sửa thông tin, hoặc xoá toàn bộ tài khoản cùng lá số
                và lịch sử trò chuyện bằng cách gửi email cho chúng tôi.
              </li>
              <li>
                Rút lại sự đồng ý bất cứ lúc nào bằng cách ngừng sử dụng dịch vụ và yêu cầu xoá tài
                khoản.
              </li>
            </ul>
            <p>Chúng tôi xử lý các yêu cầu này trong thời hạn pháp luật quy định.</p>
          </PolicySection>

          <PolicySection title="8. Thay đổi chính sách">
            <p>
              Khi chính sách thay đổi, chúng tôi cập nhật trang này và ngày “Cập nhật lần cuối” ở đầu
              trang. Nếu thay đổi đáng kể, chúng tôi sẽ thông báo trong ứng dụng hoặc qua email.
            </p>
          </PolicySection>

          <PolicySection title="9. Liên hệ">
            <p>
              Mọi câu hỏi hoặc yêu cầu về dữ liệu cá nhân, vui lòng gửi email tới{" "}
              <a href={`mailto:${CONTACT_EMAIL}`} className={LINK_CLASS}>
                {CONTACT_EMAIL}
              </a>
              .
            </p>
          </PolicySection>
        </div>
      </main>
    </div>
  );
}

function PolicySection({ children, title }: { children: React.ReactNode; title: string }) {
  return (
    <section className="grid gap-4">
      <h2 className="font-display text-[22px] leading-[1.2] font-semibold text-ink md:text-2xl">
        {title}
      </h2>
      {children}
    </section>
  );
}

function Strong({ children }: { children: React.ReactNode }) {
  return <strong className="font-semibold text-ink">{children}</strong>;
}
