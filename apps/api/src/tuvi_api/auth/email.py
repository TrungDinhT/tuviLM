"""Account emails: verification and password reset, sent through Resend."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from html import escape
from urllib.parse import urlsplit

import httpx

from tuvi_api.auth.settings import AuthSettings

logger = logging.getLogger(__name__)

RESEND_ENDPOINT = "https://api.resend.com/emails"


@dataclass(frozen=True, slots=True)
class EmailMessage:
    to: str
    subject: str
    text: str
    html: str


async def send_email(
    settings: AuthSettings,
    message: EmailMessage,
    *,
    client: httpx.AsyncClient | None = None,
) -> None:
    """Send through the Resend HTTP API. Without a key, log the mail and its link.

    The API refuses to start on https without a key (see main.py), so only local
    development reaches the logging branch.
    """
    if not settings.email_enabled:
        logger.info("[email] To: %s\nSubject: %s\n\n%s", message.to, message.subject, message.text)
        return
    owns_client = client is None
    http = client or httpx.AsyncClient(timeout=10)
    try:
        response = await http.post(
            RESEND_ENDPOINT,
            headers={"Authorization": f"Bearer {settings.resend_api_key}"},
            json={
                "from": settings.email_from,
                "to": [message.to],
                "subject": message.subject,
                "text": message.text,
                "html": message.html,
            },
        )
    finally:
        if owns_client:
            await http.aclose()
    if response.status_code >= 300:
        raise RuntimeError(f"Resend rejected the email ({response.status_code}): {response.text}")


async def send_email_logged(settings: AuthSettings, message: EmailMessage) -> None:
    """For background tasks: the response is already sent, so only log a failure."""
    try:
        await send_email(settings, message)
    except Exception:
        logger.exception("Could not send %r to %s", message.subject, message.to)


def verification_email(*, to: str, name: str, url: str) -> EmailMessage:
    return _auth_email(
        to=to,
        subject="Xác nhận email · Thiên Hạc",
        preheader="Một bước nữa thôi — xác nhận email để mở hồ sơ Thiên Hạc của bạn.",
        eyebrow="Xác nhận email",
        heading="Chào mừng bạn đến với Thiên Hạc",
        name=name,
        intro=(
            "Cảm ơn bạn đã đăng ký. Bấm nút dưới đây để xác nhận địa chỉ email và kích hoạt "
            "tài khoản — lá số, luận giải và các cuộc trò chuyện của bạn sẽ được giữ trong "
            "một hồ sơ riêng."
        ),
        action="Xác nhận email",
        url=url,
        expiry="Link có hiệu lực trong 1 giờ.",
        footnote="Nếu bạn không đăng ký Thiên Hạc, hãy bỏ qua email này.",
    )


def reset_password_email(*, to: str, name: str, url: str) -> EmailMessage:
    return _auth_email(
        to=to,
        subject="Đặt lại mật khẩu · Thiên Hạc",
        preheader="Link đặt lại mật khẩu Thiên Hạc của bạn, có hiệu lực trong 1 giờ.",
        eyebrow="Đặt lại mật khẩu",
        heading="Chọn mật khẩu mới cho tài khoản của bạn",
        name=name,
        intro=(
            "Chúng tôi nhận được yêu cầu đặt lại mật khẩu cho tài khoản Thiên Hạc của bạn. "
            "Bấm nút dưới đây để chọn mật khẩu mới."
        ),
        action="Đặt lại mật khẩu",
        url=url,
        expiry="Link có hiệu lực trong 1 giờ và chỉ dùng được một lần.",
        footnote=(
            "Nếu bạn không yêu cầu, hãy bỏ qua email này — mật khẩu hiện tại vẫn giữ nguyên."
        ),
    )


# Text and line colours only. The email sets no background anywhere, so it sits
# on whatever surface the mail client draws (Gmail's white pane above all), and
# every colour here is dark enough to read on it. The ngũ hành stars are the
# app's --element-* colours, darkened so the lightest still shows.
_HEADING = "#1A1033"
_BODY = "#3D3354"
_MUTED = "#6B6080"
_FAINT = "#776C8E"
_ACCENT = "#5B3DB0"
_GOLD = "#C9A24A"
_LINE = "#E4DEEF"
_ELEMENT_COLOURS = ["#928E87", "#4A9573", "#5B89BF", "#D94F4A", "#98714D"]

_SANS = "Arial,Helvetica,sans-serif"
_SERIF = "Georgia,'Times New Roman',serif"


def _auth_email(
    *,
    to: str,
    subject: str,
    preheader: str,
    eyebrow: str,
    heading: str,
    name: str,
    intro: str,
    action: str,
    url: str,
    expiry: str,
    footnote: str,
) -> EmailMessage:
    greeting = f"Chào {name.strip()}," if name.strip() else "Chào bạn,"
    text = "\n".join(
        [greeting, "", intro, "", f"{action}: {url}", "", expiry, footnote, "", "— Thiên Hạc"]
    )
    href = escape(url)
    # The link is always absolute, so the logo is served by the app that opens it.
    parts = urlsplit(url)
    logo = escape(f"{parts.scheme}://{parts.netloc}/assets/icons/android-chrome-192x192.png")
    element_stars = "&nbsp;&nbsp;".join(
        f'<span style="color:{colour}">&#10022;</span>' for colour in _ELEMENT_COLOURS
    )
    html = f"""<!doctype html>
<html lang="vi">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{escape(subject)}</title>
  </head>
  <body style="margin:0;padding:0">
    <div style="display:none;max-height:0;overflow:hidden;opacity:0;mso-hide:all">{escape(preheader)}</div>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
      <tr><td align="center" style="padding:36px 20px">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:520px">
          <tr><td align="center" style="padding:0 0 28px;font-family:{_SANS}">
            <img src="{logo}" width="64" height="64" alt="" style="display:block;border:0;border-radius:18px">
            <p style="margin:14px 0 0;font-family:{_SERIF};font-size:22px;font-weight:bold;letter-spacing:.02em;color:{_HEADING}">Thiên Hạc</p>
            <p style="margin:8px 0 0;font-size:12px;line-height:1">{element_stars}</p>
          </td></tr>
          <tr><td style="font-family:{_SANS}">
            <p style="margin:0 0 14px;font-size:12px;font-weight:bold;letter-spacing:.16em;text-transform:uppercase;color:{_ACCENT}"><span style="color:{_GOLD}">&#10022;</span>&nbsp; {escape(eyebrow)}</p>
            <h1 style="margin:0 0 20px;font-family:{_SERIF};font-size:28px;line-height:1.2;font-weight:bold;color:{_HEADING}">{escape(heading)}</h1>
            <p style="margin:0 0 10px;font-size:15px;line-height:1.65;color:{_HEADING}">{escape(greeting)}</p>
            <p style="margin:0 0 28px;font-size:15px;line-height:1.65;color:{_BODY}">{escape(intro)}</p>
            <a href="{href}" style="display:inline-block;padding:13px 28px;border:2px solid {_ACCENT};border-radius:14px;font-family:{_SANS};font-size:16px;font-weight:bold;color:{_ACCENT};text-decoration:none">{escape(action)} &rarr;</a>
            <p style="margin:22px 0 0;font-size:13px;line-height:1.6;color:{_MUTED}">&#9203; {escape(expiry)}</p>
          </td></tr>
          <tr><td style="padding:28px 0 0;font-family:{_SANS}">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>
              <td style="border-top:1px solid {_LINE};padding-top:20px;font-size:12px;line-height:1.6;color:{_MUTED}">Nút không hoạt động? Mở link sau:<br><a href="{href}" style="color:{_ACCENT};word-break:break-all">{href}</a></td>
            </tr></table>
          </td></tr>
          <tr><td style="padding:24px 0 0;font-family:{_SANS};font-size:12px;line-height:1.7;color:{_FAINT}">{escape(footnote)}<br>Thiên Hạc · An sao &amp; luận giải Tử Vi</td></tr>
        </table>
      </td></tr>
    </table>
  </body>
</html>"""
    return EmailMessage(to=to, subject=subject, text=text, html=html)
