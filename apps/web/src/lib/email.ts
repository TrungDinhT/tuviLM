import "server-only";

type EmailMessage = {
  to: string;
  subject: string;
  text: string;
  html: string;
};

type AuthEmailInput = {
  name: string;
  url: string;
};

const RESEND_ENDPOINT = "https://api.resend.com/emails";

/**
 * Send a transactional email through the Resend HTTP API.
 *
 * Without `RESEND_API_KEY` and `EMAIL_FROM`, development prints the message —
 * link included — to the server console instead. Production refuses, so a
 * missing key shows up in the logs rather than as mail that never arrives.
 */
export async function sendEmail(message: EmailMessage): Promise<void> {
  const apiKey = process.env.RESEND_API_KEY;
  const from = process.env.EMAIL_FROM;

  if (!apiKey || !from) {
    if (process.env.NODE_ENV === "production") {
      throw new Error("RESEND_API_KEY and EMAIL_FROM must be set to send email.");
    }
    console.info(`[email] To: ${message.to}\nSubject: ${message.subject}\n\n${message.text}`);
    return;
  }

  const response = await fetch(RESEND_ENDPOINT, {
    method: "POST",
    headers: { Authorization: `Bearer ${apiKey}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      from,
      to: [message.to],
      subject: message.subject,
      text: message.text,
      html: message.html,
    }),
  });

  if (!response.ok) {
    throw new Error(`Resend rejected the email (${response.status}): ${await response.text()}`);
  }
}

export function verificationEmail({ name, url }: AuthEmailInput) {
  return authEmail({
    subject: "Xác nhận email · Thiên Hạc",
    preheader: "Một bước nữa thôi — xác nhận email để mở hồ sơ Thiên Hạc của bạn.",
    eyebrow: "Xác nhận email",
    heading: "Chào mừng bạn đến với Thiên Hạc",
    name,
    intro:
      "Cảm ơn bạn đã đăng ký. Bấm nút dưới đây để xác nhận địa chỉ email và kích hoạt tài khoản — lá số, luận giải và các cuộc trò chuyện của bạn sẽ được giữ trong một hồ sơ riêng.",
    action: "Xác nhận email",
    url,
    expiry: "Link có hiệu lực trong 1 giờ.",
    footnote: "Nếu bạn không đăng ký Thiên Hạc, hãy bỏ qua email này.",
  });
}

export function resetPasswordEmail({ name, url }: AuthEmailInput) {
  return authEmail({
    subject: "Đặt lại mật khẩu · Thiên Hạc",
    preheader: "Link đặt lại mật khẩu Thiên Hạc của bạn, có hiệu lực trong 1 giờ.",
    eyebrow: "Đặt lại mật khẩu",
    heading: "Chọn mật khẩu mới cho tài khoản của bạn",
    name,
    intro:
      "Chúng tôi nhận được yêu cầu đặt lại mật khẩu cho tài khoản Thiên Hạc của bạn. Bấm nút dưới đây để chọn mật khẩu mới.",
    action: "Đặt lại mật khẩu",
    url,
    expiry: "Link có hiệu lực trong 1 giờ và chỉ dùng được một lần.",
    footnote: "Nếu bạn không yêu cầu, hãy bỏ qua email này — mật khẩu hiện tại vẫn giữ nguyên.",
  });
}

/**
 * Text and line colours only. The email sets no background anywhere, so it
 * sits on whatever surface the mail client draws — Gmail's white pane above
 * all — and every colour here is dark enough to read on it. The ngũ hành stars
 * are the app's `--element-*` colours, darkened so the lightest still shows.
 */
const EMAIL_COLOURS = {
  heading: "#1A1033",
  body: "#3D3354",
  muted: "#6B6080",
  faint: "#776C8E",
  accent: "#5B3DB0",
  gold: "#C9A24A",
  line: "#E4DEEF",
} as const;
const ELEMENT_COLOURS = ["#928E87", "#4A9573", "#5B89BF", "#D94F4A", "#98714D"];

const SANS = "Arial,Helvetica,sans-serif";
const SERIF = "Georgia,'Times New Roman',serif";

function authEmail({
  subject,
  preheader,
  eyebrow,
  heading,
  name,
  intro,
  action,
  url,
  expiry,
  footnote,
}: {
  subject: string;
  preheader: string;
  eyebrow: string;
  heading: string;
  name: string;
  intro: string;
  action: string;
  url: string;
  expiry: string;
  footnote: string;
}) {
  const c = EMAIL_COLOURS;
  const greeting = name.trim() ? `Chào ${name.trim()},` : "Chào bạn,";
  const text = [
    greeting,
    "",
    intro,
    "",
    `${action}: ${url}`,
    "",
    expiry,
    footnote,
    "",
    "— Thiên Hạc",
  ].join("\n");
  const href = escapeHtml(url);
  // The link is always absolute (Better Auth builds it from baseURL), so the
  // logo is served by the same app that will open the link.
  const logo = escapeHtml(`${new URL(url).origin}/assets/icons/android-chrome-192x192.png`);
  const elementStars = ELEMENT_COLOURS.map(
    (colour) => `<span style="color:${colour}">&#10022;</span>`,
  ).join("&nbsp;&nbsp;");

  const html = `<!doctype html>
<html lang="vi">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>${escapeHtml(subject)}</title>
  </head>
  <body style="margin:0;padding:0">
    <div style="display:none;max-height:0;overflow:hidden;opacity:0;mso-hide:all">${escapeHtml(preheader)}</div>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
      <tr><td align="center" style="padding:36px 20px">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:520px">
          <tr><td align="center" style="padding:0 0 28px;font-family:${SANS}">
            <img src="${logo}" width="64" height="64" alt="" style="display:block;border:0;border-radius:18px">
            <p style="margin:14px 0 0;font-family:${SERIF};font-size:22px;font-weight:bold;letter-spacing:.02em;color:${c.heading}">Thiên Hạc</p>
            <p style="margin:8px 0 0;font-size:12px;line-height:1">${elementStars}</p>
          </td></tr>
          <tr><td style="font-family:${SANS}">
            <p style="margin:0 0 14px;font-size:12px;font-weight:bold;letter-spacing:.16em;text-transform:uppercase;color:${c.accent}"><span style="color:${c.gold}">&#10022;</span>&nbsp; ${escapeHtml(eyebrow)}</p>
            <h1 style="margin:0 0 20px;font-family:${SERIF};font-size:28px;line-height:1.2;font-weight:bold;color:${c.heading}">${escapeHtml(heading)}</h1>
            <p style="margin:0 0 10px;font-size:15px;line-height:1.65;color:${c.heading}">${escapeHtml(greeting)}</p>
            <p style="margin:0 0 28px;font-size:15px;line-height:1.65;color:${c.body}">${escapeHtml(intro)}</p>
            <a href="${href}" style="display:inline-block;padding:13px 28px;border:2px solid ${c.accent};border-radius:14px;font-family:${SANS};font-size:16px;font-weight:bold;color:${c.accent};text-decoration:none">${escapeHtml(action)} &rarr;</a>
            <p style="margin:22px 0 0;font-size:13px;line-height:1.6;color:${c.muted}">&#9203; ${escapeHtml(expiry)}</p>
          </td></tr>
          <tr><td style="padding:28px 0 0;font-family:${SANS}">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>
              <td style="border-top:1px solid ${c.line};padding-top:20px;font-size:12px;line-height:1.6;color:${c.muted}">Nút không hoạt động? Mở link sau:<br><a href="${href}" style="color:${c.accent};word-break:break-all">${href}</a></td>
            </tr></table>
          </td></tr>
          <tr><td style="padding:24px 0 0;font-family:${SANS};font-size:12px;line-height:1.7;color:${c.faint}">${escapeHtml(footnote)}<br>Thiên Hạc · An sao &amp; luận giải Tử Vi</td></tr>
        </table>
      </td></tr>
    </table>
  </body>
</html>`;

  return { subject, text, html };
}

function escapeHtml(value: string): string {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}
