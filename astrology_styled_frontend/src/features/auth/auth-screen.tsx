"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { type FormEvent, useState } from "react";

import { authClient } from "@/lib/auth-client";
import { cn } from "@/lib/utils";
import { useToastStore } from "@/store/toast-store";

type AuthMode = "login" | "register";

const INPUT_CLASS =
  "min-h-[50px] w-full rounded-[14px] border border-glass-line bg-white/[0.07] px-3.5 py-3 text-[15px] text-ink outline-none caret-accent transition-[border-color,box-shadow,background] placeholder:text-muted/70 hover:border-[color-mix(in_oklch,var(--color-glass-line)_60%,var(--color-ink))] focus:border-accent focus:bg-[color-mix(in_oklch,var(--color-bg-1)_78%,rgba(255,255,255,.07))] focus:shadow-[0_0_0_4px_color-mix(in_oklch,var(--accent)_14%,transparent)]";

export function AuthScreen({ mode }: { mode: AuthMode }) {
  const isLogin = mode === "login";
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [passwordValue, setPasswordValue] = useState("");
  const [pendingAction, setPendingAction] = useState<"email" | "google" | null>(null);
  const showToast = useToastStore((state) => state.show);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);

    if (!isLogin && form.get("password") !== form.get("confirmPassword")) {
      showToast("Hai mật khẩu chưa trùng nhau.");
      return;
    }

    setPendingAction("email");
    try {
      const email = String(form.get("email") ?? "");
      const password = String(form.get("password") ?? "");
      const result = isLogin
        ? await authClient.signIn.email({ email, password })
        : await authClient.signUp.email({
            name: String(form.get("displayName") ?? ""),
            email,
            password,
          });

      if (result.error) {
        showToast(authErrorMessage(result.error.message, isLogin));
        return;
      }

      router.replace("/");
      router.refresh();
    } catch {
      showToast("Không thể kết nối máy chủ xác thực. Vui lòng thử lại sau.");
    } finally {
      setPendingAction(null);
    }
  };

  const signInWithGoogle = async () => {
    setPendingAction("google");
    try {
      const result = await authClient.signIn.social({
        provider: "google",
        callbackURL: "/",
        errorCallbackURL: "/login",
      });
      if (result.error) {
        showToast(authErrorMessage(result.error.message, true));
        setPendingAction(null);
      }
    } catch {
      showToast("Không thể mở đăng nhập Google. Vui lòng thử lại sau.");
      setPendingAction(null);
    }
  };

  return (
    <div className="min-h-dvh bg-bg-0">
      <main>
        <section className="grid min-h-[calc(100dvh-72px-var(--safe-t))] items-center py-9 md:min-h-[calc(100dvh-78px-var(--safe-t))] md:py-12 lg:py-5">
          <div
            className={cn(
              "mx-auto grid w-full max-w-[1200px] items-center gap-8 px-5 sm:px-8 md:gap-[clamp(44px,6vw,80px)] lg:px-14",
              isLogin
                ? "md:grid-cols-[minmax(0,1fr)_minmax(360px,1fr)] lg:grid-cols-[1.05fr_.95fr]"
                : "md:grid-cols-[minmax(0,.95fr)_minmax(390px,1.05fr)] lg:grid-cols-[.9fr_1.1fr]",
            )}
          >
            <AuthIntro mode={mode} />
            <AuthCard
              mode={mode}
              passwordLevel={getPasswordStrength(passwordValue)}
              pendingAction={pendingAction}
              showConfirmPassword={showConfirmPassword}
              showPassword={showPassword}
              onConfirmPasswordToggle={() => setShowConfirmPassword((visible) => !visible)}
              onGoogleSignIn={() => void signInWithGoogle()}
              onPasswordChange={setPasswordValue}
              onPasswordToggle={() => setShowPassword((visible) => !visible)}
              onSubmit={(event) => void handleSubmit(event)}
              onUnavailableLink={() => showToast("Nội dung này sẽ sớm được mở ✦")}
            />
          </div>
        </section>
      </main>
    </div>
  );
}

type AuthCardProps = {
  mode: AuthMode;
  passwordLevel: number;
  pendingAction: "email" | "google" | null;
  showConfirmPassword: boolean;
  showPassword: boolean;
  onConfirmPasswordToggle: () => void;
  onGoogleSignIn: () => void;
  onPasswordChange: (value: string) => void;
  onPasswordToggle: () => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onUnavailableLink: () => void;
};

function AuthCard({
  mode,
  passwordLevel,
  pendingAction,
  showConfirmPassword,
  showPassword,
  onConfirmPasswordToggle,
  onGoogleSignIn,
  onPasswordChange,
  onPasswordToggle,
  onSubmit,
  onUnavailableLink,
}: AuthCardProps) {
  const isLogin = mode === "login";

  return (
    <div
      className={cn(
        "min-w-0 justify-self-end rounded-card border border-glass-line bg-[color-mix(in_oklch,var(--color-bg-1)_92%,transparent)] p-6 shadow-[0_28px_80px_color-mix(in_oklch,var(--color-bg-0)_74%,transparent)] backdrop-blur-[18px] sm:p-8",
        isLogin ? "w-full max-w-[520px]" : "w-full max-w-[610px]",
      )}
    >
      <div className="mb-7">
        <h2 className="font-display text-[clamp(30px,5vw,40px)] leading-[1.1] font-semibold">
          {isLogin ? "Đăng nhập" : "Tạo tài khoản"}
        </h2>
        <p className="mt-2 text-sm text-muted">
          {isLogin
            ? "Dùng Google hoặc email đã liên kết với hồ sơ Tử Vi."
            : "Chỉ cần vài thông tin cơ bản để bắt đầu."}
        </p>
      </div>

      <form className="flex flex-col gap-[17px]" onSubmit={onSubmit}>
        {!isLogin ? (
          <div className="grid gap-[17px]">
            <AuthField label="Tên hiển thị" htmlFor="display-name">
              <input
                id="display-name"
                name="displayName"
                type="text"
                autoComplete="name"
                minLength={2}
                required
                className={INPUT_CLASS}
                placeholder="Tên của bạn"
              />
            </AuthField>

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

            <div className="grid gap-[17px] lg:grid-cols-2">
              <AuthField label="Mật khẩu" htmlFor="password">
                <PasswordInput
                  id="password"
                  name="password"
                  autoComplete="new-password"
                  placeholder="Ít nhất 8 ký tự"
                  visible={showPassword}
                  onChange={onPasswordChange}
                  onToggle={onPasswordToggle}
                />
                <div className="mt-2 grid grid-cols-4 gap-[5px]" aria-hidden="true">
                  {[1, 2, 3, 4].map((level) => (
                    <span
                      key={level}
                      className={cn(
                        "h-[3px] rounded-full",
                        passwordLevel >= level ? "bg-ink" : "bg-glass-line",
                      )}
                    />
                  ))}
                </div>
                <span className="mt-1 block min-h-[18px] text-xs text-muted">
                  Kết hợp chữ và số để tăng độ mạnh.
                </span>
              </AuthField>

              <AuthField label="Nhập lại mật khẩu" htmlFor="confirm-password">
                <PasswordInput
                  id="confirm-password"
                  name="confirmPassword"
                  autoComplete="new-password"
                  placeholder="Nhập lại mật khẩu"
                  visible={showConfirmPassword}
                  onToggle={onConfirmPasswordToggle}
                />
              </AuthField>
            </div>
          </div>
        ) : (
          <>
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

            <AuthField
              label="Mật khẩu"
              htmlFor="password"
              action={
                <button
                  type="button"
                  className="cursor-pointer border-0 text-[13px] text-muted underline decoration-glass-line underline-offset-4 transition-colors hover:text-ink"
                  onClick={onUnavailableLink}
                >
                  Quên mật khẩu?
                </button>
              }
            >
              <PasswordInput
                id="password"
                name="password"
                autoComplete="current-password"
                placeholder="Nhập mật khẩu"
                visible={showPassword}
                onToggle={onPasswordToggle}
              />
            </AuthField>
          </>
        )}

        {!isLogin ? (
          <div className="grid grid-cols-[24px_1fr] items-start gap-[11px] text-[13px] leading-relaxed text-muted">
            <input
              id="terms"
              type="checkbox"
              name="terms"
              required
              aria-labelledby="terms-label"
              className="mt-0 grid size-[22px] appearance-none place-content-center rounded-[7px] border border-glass-line bg-white/[0.07] before:h-1.5 before:w-2.5 before:-rotate-45 before:scale-0 before:border-b-2 before:border-l-2 before:border-bg-0 before:transition-transform before:content-[''] checked:border-accent checked:bg-accent checked:before:scale-100"
            />
            <span id="terms-label">
              <label htmlFor="terms" className="cursor-pointer">
                Tôi đồng ý với
              </label>{" "}
              <button
                type="button"
                className="cursor-pointer border-0 font-medium text-ink underline decoration-glass-line underline-offset-4"
                onClick={onUnavailableLink}
              >
                Điều khoản sử dụng
              </button>{" "}
              và{" "}
              <button
                type="button"
                className="cursor-pointer border-0 font-medium text-ink underline decoration-glass-line underline-offset-4"
                onClick={onUnavailableLink}
              >
                Chính sách riêng tư
              </button>
              .
            </span>
          </div>
        ) : null}

        <div className={cn("grid gap-[17px]", !isLogin && "lg:grid-cols-2")}>
          <button
            type="submit"
            disabled={pendingAction !== null}
            className="mt-1 inline-flex min-h-[50px] w-full cursor-pointer items-center justify-center rounded-[14px] border border-accent bg-accent px-5 font-bold text-bg-0 transition-[transform,background,border-color] hover:bg-[color-mix(in_oklch,var(--accent)_86%,var(--color-ink))] active:translate-y-px disabled:cursor-wait disabled:opacity-70"
          >
            {pendingAction === "email"
              ? isLogin
                ? "Đang đăng nhập…"
                : "Đang tạo tài khoản…"
              : isLogin
                ? "Đăng nhập"
                : "Tạo tài khoản"}
          </button>

          <div
            className={cn("flex items-center gap-3.5 text-xs text-muted", !isLogin && "lg:hidden")}
            aria-hidden="true"
          >
            <span className="h-px flex-1 bg-glass-line" />
            hoặc
            <span className="h-px flex-1 bg-glass-line" />
          </div>

          <button
            type="button"
            disabled={pendingAction !== null}
            className="inline-flex min-h-[50px] w-full cursor-pointer items-center justify-center gap-2.5 rounded-[14px] border border-glass-line bg-transparent px-5 font-bold text-ink transition-[transform,background,border-color] hover:border-ink hover:bg-white/[0.07] active:translate-y-px disabled:cursor-wait disabled:opacity-50"
            onClick={onGoogleSignIn}
          >
            <GoogleIcon />
            {pendingAction === "google" ? (
              "Đang đăng nhập Google…"
            ) : isLogin ? (
              "Tiếp tục với Google"
            ) : (
              <>
                <span className="lg:hidden">Đăng ký với Google</span>
                <span className="hidden lg:inline">Google</span>
              </>
            )}
          </button>
        </div>

        <p className="text-center text-sm text-muted">
          {isLogin ? "Chưa có tài khoản?" : "Đã có tài khoản?"}{" "}
          <Link
            href={isLogin ? "/register" : "/login"}
            className="font-bold text-ink underline decoration-glass-line underline-offset-4 hover:decoration-ink"
          >
            {isLogin ? "Đăng ký" : "Đăng nhập"}
          </Link>
        </p>
      </form>
    </div>
  );
}

function AuthIntro({ mode }: { mode: AuthMode }) {
  const isLogin = mode === "login";

  return (
    <div className={cn("relative min-w-0", !isLogin && "lg:pr-7")}>
      <p className="mb-[18px] font-mono text-xs tracking-[0.1em] text-muted uppercase">
        {isLogin ? "Trở lại hành trình" : "Bắt đầu hồ sơ"}
      </p>
      <h1
        className={cn(
          "font-display text-[clamp(42px,11vw,56px)] leading-[1.02] font-semibold tracking-[-0.035em] text-balance md:text-[clamp(40px,5vw,52px)] lg:text-[clamp(56px,5.5vw,70px)]",
          isLogin ? "max-w-[11ch]" : "max-w-[10ch]",
        )}
      >
        {isLogin ? "Tiếp tục nghiên cứu vận trình" : "Giữ lại từng dấu mốc"}
      </h1>
      <p className="mt-5 max-w-[48ch] text-base leading-[1.55] text-muted md:text-[17px]">
        {isLogin
          ? "Đăng nhập để mở lại lá số đã lưu, các luận giải và cuộc trò chuyện"
          : "Tạo tài khoản để lưu lá số, tiếp tục luận giải và quay lại các cuộc trò chuyện"}
      </p>

      {isLogin ? (
        <>
          <LoginConstellation />
          <span className="absolute top-[16%] right-[-42px] hidden h-[68%] w-px bg-glass-line lg:block" />
        </>
      ) : (
        <ul
          className="mt-[30px] hidden list-none gap-3.5 md:grid"
          aria-label="Lợi ích khi tạo tài khoản"
        >
          <PromiseItem icon="check">Lá số và luận giải được giữ trong một hồ sơ riêng.</PromiseItem>
          <PromiseItem icon="shield">
            Bạn kiểm soát thông tin cá nhân và có thể xóa hồ sơ bất cứ lúc nào.
          </PromiseItem>
        </ul>
      )}
    </div>
  );
}

function AuthField({
  action,
  children,
  htmlFor,
  label,
}: {
  action?: React.ReactNode;
  children: React.ReactNode;
  htmlFor: string;
  label: string;
}) {
  return (
    <div className="flex min-w-0 flex-col gap-2">
      <div className="flex items-center justify-between gap-4">
        <label htmlFor={htmlFor} className="text-sm font-semibold text-ink">
          {label}
        </label>
        {action}
      </div>
      {children}
    </div>
  );
}

function PasswordInput({
  autoComplete,
  id,
  name,
  onChange,
  onToggle,
  placeholder,
  visible,
}: {
  autoComplete: "current-password" | "new-password";
  id: string;
  name: string;
  onChange?: (value: string) => void;
  onToggle: () => void;
  placeholder: string;
  visible: boolean;
}) {
  return (
    <div className="relative">
      <input
        id={id}
        name={name}
        type={visible ? "text" : "password"}
        autoComplete={autoComplete}
        minLength={8}
        required
        className={`${INPUT_CLASS} pr-[54px]`}
        placeholder={placeholder}
        onChange={onChange ? (event) => onChange(event.currentTarget.value) : undefined}
      />
      <button
        type="button"
        className="absolute top-[3px] right-[3px] grid size-11 cursor-pointer place-items-center rounded-[11px] border-0 bg-transparent text-muted transition-colors hover:bg-white/[0.07] hover:text-ink"
        aria-label={visible ? "Ẩn mật khẩu" : "Hiện mật khẩu"}
        aria-controls={id}
        aria-pressed={visible}
        onClick={onToggle}
      >
        <EyeIcon crossed={visible} />
      </button>
    </div>
  );
}

function PromiseItem({ children, icon }: { children: React.ReactNode; icon: "check" | "shield" }) {
  return (
    <li className="grid grid-cols-[28px_1fr] items-start gap-3 text-sm text-muted">
      <svg
        viewBox="0 0 24 24"
        className="size-[22px] text-ink"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        aria-hidden="true"
      >
        {icon === "check" ? (
          <path d="M5 12.5 9.5 17 19 7" />
        ) : (
          <path d="M12 3 5 6v5c0 4.5 2.8 8 7 10 4.2-2 7-5.5 7-10V6l-7-3Z" />
        )}
      </svg>
      <span>{children}</span>
    </li>
  );
}

function LoginConstellation() {
  return (
    <svg
      viewBox="0 0 380 170"
      className="mt-[34px] hidden w-full max-w-[380px] text-accent opacity-80 md:block"
      role="img"
      aria-label="Chòm sao trang trí"
    >
      <path
        d="M26 118L94 62L168 90L230 34L296 74L350 28"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.2"
        opacity=".5"
      />
      <path
        d="M94 62L112 140L168 90L220 146L296 74"
        fill="none"
        stroke="currentColor"
        strokeWidth=".7"
        opacity=".28"
      />
      {[
        [26, 118, 3],
        [94, 62, 4],
        [112, 140, 2.5],
        [168, 90, 3],
        [220, 146, 2.5],
        [230, 34, 3.5],
        [296, 74, 4],
        [350, 28, 2.5],
      ].map(([cx, cy, radius]) => (
        <circle key={`${cx}-${cy}`} cx={cx} cy={cy} r={radius} fill="currentColor" />
      ))}
    </svg>
  );
}

function EyeIcon({ crossed }: { crossed: boolean }) {
  return (
    <svg
      viewBox="0 0 24 24"
      className="size-5"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      aria-hidden="true"
    >
      <path d="M3 12s3.3-5 9-5 9 5 9 5-3.3 5-9 5-9-5-9-5Z" />
      <circle cx="12" cy="12" r="2.5" />
      {crossed ? <path d="m4 4 16 16" /> : null}
    </svg>
  );
}

function GoogleIcon() {
  return (
    <svg viewBox="0 0 24 24" className="size-5 shrink-0 text-ink" aria-hidden="true">
      <path
        fill="currentColor"
        d="M21.35 12.18c0-.69-.06-1.35-.18-1.98H12v3.75h5.24a4.48 4.48 0 0 1-1.94 2.94v2.43h3.15c1.84-1.7 2.9-4.2 2.9-7.14Z"
      />
      <path
        fill="currentColor"
        d="M12 21.7c2.63 0 4.84-.87 6.45-2.35l-3.15-2.44c-.87.59-1.99.93-3.3.93-2.54 0-4.69-1.71-5.46-4.01H3.28v2.51A9.73 9.73 0 0 0 12 21.7Z"
        opacity=".78"
      />
      <path
        fill="currentColor"
        d="M6.54 13.83A5.85 5.85 0 0 1 6.23 12c0-.64.11-1.26.31-1.85V7.64H3.28A9.73 9.73 0 0 0 2.27 12c0 1.57.37 3.06 1.01 4.36l3.26-2.53Z"
        opacity=".56"
      />
      <path
        fill="currentColor"
        d="M12 6.16c1.43 0 2.71.49 3.72 1.45l2.79-2.79A9.36 9.36 0 0 0 12 2.3a9.73 9.73 0 0 0-8.72 5.34l3.26 2.51A5.84 5.84 0 0 1 12 6.16Z"
        opacity=".9"
      />
    </svg>
  );
}

function getPasswordStrength(value: string): number {
  if (!value) return 0;

  return [
    value.length >= 8,
    /[A-Za-zÀ-ỹ]/.test(value),
    /\d/.test(value),
    /[^A-Za-zÀ-ỹ0-9]/.test(value),
  ].filter(Boolean).length;
}

function authErrorMessage(message: string | undefined, isLogin: boolean): string {
  const normalizedMessage = message?.toLocaleLowerCase("vi");

  if (normalizedMessage?.includes("provider")) {
    return "Google OAuth chưa được cấu hình trên máy chủ.";
  }
  if (normalizedMessage?.includes("already")) {
    return "Email này đã có tài khoản. Hãy đăng nhập nhé.";
  }

  return isLogin
    ? "Email hoặc mật khẩu chưa đúng. Bạn kiểm tra lại nhé."
    : "Không thể tạo tài khoản. Bạn kiểm tra thông tin và thử lại nhé.";
}
