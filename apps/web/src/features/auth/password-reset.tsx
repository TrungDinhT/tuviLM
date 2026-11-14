"use client";

import Link from "next/link";
import { type FormEvent, useState } from "react";
import { Result, Schema } from "effect";

import { authClient } from "@/lib/auth-client";
import { firstMessage, validate } from "@/lib/schema";
import { showToast } from "@/lib/toast";
import { cn } from "@/lib/utils";

import {
  AUTH_CARD_CLASS,
  AuthField,
  confirmPasswordField,
  emailField,
  INPUT_CLASS,
  PasswordInput,
  passwordsMatch,
  PRIMARY_BUTTON_CLASS,
  SECONDARY_BUTTON_CLASS,
} from "./auth-screen";

const NETWORK_ERROR = "Không thể kết nối máy chủ xác thực. Vui lòng thử lại sau.";
const RATE_LIMITED = "Bạn thao tác hơi nhanh. Vui lòng đợi một chút rồi thử lại.";

const newPasswordSchema = Schema.Struct({
  password: Schema.String.check(
    Schema.isMinLength(1, { message: "Vui lòng nhập mật khẩu mới." }),
    Schema.isMinLength(8, { message: "Mật khẩu phải có ít nhất 8 ký tự." }),
  ),
  confirmPassword: confirmPasswordField,
}).check(passwordsMatch);

export function ForgotPasswordScreen() {
  const [sentTo, setSentTo] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  const sendResetLink = async (email: string) => {
    setPending(true);
    try {
      const result = await authClient.requestPasswordReset({ email });
      if (result.error) {
        showToast(
          result.error.status === 429
            ? RATE_LIMITED
            : "Không gửi được email đặt lại mật khẩu. Vui lòng thử lại sau.",
        );
        return;
      }
      setSentTo(email);
    } catch {
      showToast(NETWORK_ERROR);
    } finally {
      setPending(false);
    }
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const result = validate(emailField, String(new FormData(event.currentTarget).get("email")));
    if (Result.isFailure(result)) {
      showToast(firstMessage(result.failure, "Email chưa đúng định dạng."));
      return;
    }
    void sendResetLink(result.success);
  };

  if (sentTo) {
    return (
      <AuthPage title="Kiểm tra hộp thư">
        <p role="status" className="text-[15px] leading-relaxed text-muted">
          Nếu <strong className="break-all text-ink">{sentTo}</strong> có tài khoản Thiên Hạc, bạn
          sẽ nhận được link đặt lại mật khẩu trong vài phút. Link có hiệu lực trong 1 giờ.
        </p>
        <p className="mt-3 text-sm text-muted">Không thấy email? Hãy xem cả mục Spam.</p>
        <div className="mt-7 grid gap-3">
          <button
            type="button"
            disabled={pending}
            className={PRIMARY_BUTTON_CLASS}
            onClick={() => void sendResetLink(sentTo)}
          >
            {pending ? "Đang gửi…" : "Gửi lại link"}
          </button>
          <Link href="/login" className={SECONDARY_BUTTON_CLASS}>
            Quay lại đăng nhập
          </Link>
        </div>
      </AuthPage>
    );
  }

  return (
    <AuthPage
      title="Quên mật khẩu"
      subtitle="Nhập email đã đăng ký, chúng tôi sẽ gửi link để bạn đặt mật khẩu mới."
    >
      <form className="flex flex-col gap-[17px]" noValidate onSubmit={handleSubmit}>
        <AuthField label="Email" htmlFor="email">
          <input
            id="email"
            name="email"
            type="email"
            inputMode="email"
            autoComplete="email"
            required
            className={INPUT_CLASS}
            placeholder="ban@example.com"
          />
        </AuthField>
        <button type="submit" disabled={pending} className={cn(PRIMARY_BUTTON_CLASS, "mt-1")}>
          {pending ? "Đang gửi…" : "Gửi link đặt lại mật khẩu"}
        </button>
        <BackToLogin />
      </form>
    </AuthPage>
  );
}

export function ResetPasswordScreen({ token }: { token: string | null }) {
  const [status, setStatus] = useState<"form" | "invalid" | "done">(token ? "form" : "invalid");
  const [pending, setPending] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!token) return;
    const form = new FormData(event.currentTarget);
    const parsed = validate(newPasswordSchema, {
      password: String(form.get("password") ?? ""),
      confirmPassword: String(form.get("confirmPassword") ?? ""),
    });
    if (Result.isFailure(parsed)) {
      showToast(firstMessage(parsed.failure, "Mật khẩu chưa hợp lệ."));
      return;
    }

    setPending(true);
    try {
      const result = await authClient.resetPassword({
        newPassword: parsed.success.password,
        token,
      });
      if (result.error) {
        if (result.error.code === "INVALID_TOKEN") setStatus("invalid");
        else showToast(result.error.status === 429 ? RATE_LIMITED : "Không thể đặt lại mật khẩu.");
        return;
      }
      setStatus("done");
    } catch {
      showToast(NETWORK_ERROR);
    } finally {
      setPending(false);
    }
  };

  if (status === "done") {
    return (
      <AuthPage title="Đã đặt lại mật khẩu">
        <p role="status" className="text-[15px] leading-relaxed text-muted">
          Mật khẩu mới đã được lưu và các phiên đăng nhập cũ đã được đăng xuất. Hãy đăng nhập lại
          bằng mật khẩu mới.
        </p>
        <Link href="/login" className={cn(PRIMARY_BUTTON_CLASS, "mt-7")}>
          Đăng nhập
        </Link>
      </AuthPage>
    );
  }

  if (status === "invalid") {
    return (
      <AuthPage title="Link không còn hiệu lực">
        <p role="alert" className="text-[15px] leading-relaxed text-muted">
          Link đặt lại mật khẩu không hợp lệ, đã được dùng hoặc đã hết hạn. Hãy yêu cầu link mới.
        </p>
        <div className="mt-7 grid gap-3">
          <Link href="/forgot-password" className={PRIMARY_BUTTON_CLASS}>
            Gửi link mới
          </Link>
          <Link href="/login" className={SECONDARY_BUTTON_CLASS}>
            Quay lại đăng nhập
          </Link>
        </div>
      </AuthPage>
    );
  }

  return (
    <AuthPage title="Đặt mật khẩu mới" subtitle="Chọn mật khẩu có ít nhất 8 ký tự.">
      <form className="flex flex-col gap-[17px]" noValidate onSubmit={(e) => void handleSubmit(e)}>
        <AuthField label="Mật khẩu mới" htmlFor="password">
          <PasswordInput
            id="password"
            name="password"
            autoComplete="new-password"
            placeholder="Ít nhất 8 ký tự"
            visible={showPassword}
            onToggle={() => setShowPassword((visible) => !visible)}
          />
        </AuthField>
        <AuthField label="Nhập lại mật khẩu" htmlFor="confirm-password">
          <PasswordInput
            id="confirm-password"
            name="confirmPassword"
            autoComplete="new-password"
            placeholder="Nhập lại mật khẩu"
            visible={showConfirmPassword}
            onToggle={() => setShowConfirmPassword((visible) => !visible)}
          />
        </AuthField>
        <button type="submit" disabled={pending} className={cn(PRIMARY_BUTTON_CLASS, "mt-1")}>
          {pending ? "Đang lưu…" : "Lưu mật khẩu mới"}
        </button>
        <BackToLogin />
      </form>
    </AuthPage>
  );
}

function AuthPage({
  children,
  subtitle,
  title,
}: {
  children: React.ReactNode;
  subtitle?: string;
  title: string;
}) {
  return (
    <div className="min-h-dvh bg-bg-0">
      <main className="grid min-h-dvh place-items-center px-5 pt-[calc(36px+var(--safe-t))] pb-[calc(36px+var(--safe-b))] sm:px-8">
        <section className={cn(AUTH_CARD_CLASS, "w-full max-w-[480px]")}>
          <div className="mb-7">
            <h1 className="font-display text-[clamp(30px,5vw,40px)] leading-[1.1] font-semibold">
              {title}
            </h1>
            {subtitle ? <p className="mt-2 text-sm text-muted">{subtitle}</p> : null}
          </div>
          {children}
        </section>
      </main>
    </div>
  );
}

function BackToLogin() {
  return (
    <p className="text-center text-sm text-muted">
      Nhớ ra mật khẩu?{" "}
      <Link
        href="/login"
        className="font-bold text-ink underline decoration-glass-line underline-offset-4 hover:decoration-ink"
      >
        Đăng nhập
      </Link>
    </p>
  );
}
