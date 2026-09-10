"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import type { Calendar, UserProfile } from "../_lib/types";
import {
  loadAnonymousOwnerId,
  saveAnonymousOwnerId,
  saveStash,
} from "../_lib/session-store";
import { EntryFormSchema } from "../_lib/schemas";
import { useBuildLaso } from "@/services/api/v1/laso/build";
import { getCauPhu } from "@/services/api/v1/laso/cau-phu";
import {
  createAnonymousOwner,
  createChartProfile,
  createChatSession,
} from "@/services/api/v1/conversation-history";
import { Btn } from "./Buttons";
import { Eyebrow } from "./Eyebrow";

export function EntryForm() {
  const router = useRouter();
  const buildLaso = useBuildLaso();
  const [name, setName] = useState("");
  const [gender, setGender] = useState<"M" | "F">("M");
  const [calendar, setCalendar] = useState<Calendar>("am");
  const [day, setDay] = useState(1);
  const [month, setMonth] = useState(1);
  const [year, setYear] = useState(1999);
  const [hour, setHour] = useState(12);
  const [minute, setMinute] = useState(30);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);

  async function submitForm() {
    const parsed = EntryFormSchema.safeParse({ day, month, year, hour, minute, gender });
    if (!parsed.success) {
      const errs: Record<string, string> = {};
      for (const issue of parsed.error.issues) {
        const key = issue.path.join(".") || "_form";
        if (!errs[key]) errs[key] = issue.message;
      }
      setFieldErrors(errs);
      return;
    }
    setFieldErrors({});

    const { minute: _m, ...apiPayload } = parsed.data;
    void _m;

    setSubmitting(true);
    try {
      let ownerId = loadAnonymousOwnerId();
      if (!ownerId) {
        ownerId = await createAnonymousOwner();
        saveAnonymousOwnerId(ownerId);
      }

      const laso = await buildLaso.mutateAsync(apiPayload);
      const cauPhu = await getCauPhu().catch(() => undefined);
      const chartProfileId = await createChartProfile({
        ownerId,
        idempotencyKey: clientOperationId(),
        displayName: name || "Giấu tên",
        birthInfo: apiPayload,
      });
      const sessionId = await createChatSession({
        ownerId,
        chartProfileId,
        idempotencyKey: clientOperationId(),
        title: name || "Lá số mới",
      });
      const profile: UserProfile = { name, gender, calendar, day, month, year, hour, minute };
      saveStash({
        laso,
        cauPhu,
        profile,
        ownerId,
        chartProfileId,
        sessionId,
        fetchedAt: new Date().toISOString(),
      });
      router.push("/chart");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Không lập được lá số. Thử lại?";
      setFieldErrors({ _form: msg });
    } finally {
      setSubmitting(false);
    }
  }

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    void submitForm();
  }

  return (
    <form
      noValidate
      onSubmit={onSubmit}
      className="relative bg-[rgba(255,252,245,0.85)] border border-[rgba(26,22,17,0.32)] p-9 max-w-[460px] w-full justify-self-center"
      style={{ boxShadow: "0 1px 0 rgba(26,22,17,0.08), 0 12px 32px rgba(26,22,17,0.06)" }}
    >
      <div className="absolute -top-px -left-px -right-px h-[5px] bg-[var(--color-crimson)]" />
      <Eyebrow>Thông tin lập lá số</Eyebrow>
      <h3 className="font-serif text-[28px] font-medium mt-1.5 mb-6 tracking-[-0.3px]">Năm sinh, giờ sinh, giới</h3>

      <div className="flex flex-col gap-4">
        <Field label="Họ tên">
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-3.5 py-2.5 border border-[rgba(26,22,17,0.32)] bg-[var(--color-paper)] font-serif text-[15px] outline-none focus:border-[var(--color-crimson)]"
            placeholder="Vui lòng nhập họ và tên..."
          />
        </Field>

        <div className="grid grid-cols-2 gap-3">
          <Group label="Giới tính">
            <div className="flex gap-1.5">
              <Btn type="button" variant={gender === "M" ? "primary" : "default"} className="flex-1 justify-center" onClick={() => setGender("M")}>Nam</Btn>
              <Btn type="button" variant={gender === "F" ? "primary" : "default"} className="flex-1 justify-center" onClick={() => setGender("F")}>Nữ</Btn>
            </div>
          </Group>
          <Group label="Lịch">
            <div className="flex gap-1.5">
              <Btn type="button" variant={calendar === "duong" ? "primary" : "default"} className="flex-1 justify-center" onClick={() => setCalendar("duong")}>Dương</Btn>
              <Btn type="button" variant={calendar === "am" ? "primary" : "default"} className="flex-1 justify-center" onClick={() => setCalendar("am")}>Âm</Btn>
            </div>
          </Group>
        </div>

        <Group label="Ngày sinh">
          <div className="flex gap-1.5">
            <NumInput label="Ngày" value={day} min={1} max={31} onChange={setDay} flex={1} />
            <NumInput label="Tháng" value={month} min={1} max={12} onChange={setMonth} flex={1} />
            <NumInput label="Năm" value={year} min={1900} max={2099} onChange={setYear} flex={1.6} />
          </div>
          {fieldErrors.day && <div className="text-[11px] text-[var(--color-crimson)] mt-1">{fieldErrors.day}</div>}
        </Group>

        <Group label="Giờ sinh">
          <div className="flex gap-1.5 items-center">
            <NumInput label="Giờ (0-23)" value={hour} min={0} max={23} onChange={setHour} flex={1} />
            <span className="text-[var(--color-ink-3)] font-serif text-[18px]">:</span>
            <NumInput label="Phút (0-59)" value={minute} min={0} max={59} onChange={setMinute} flex={1} />
          </div>
          {fieldErrors.hour && <div className="text-[11px] text-[var(--color-crimson)] mt-1">{fieldErrors.hour}</div>}
          {fieldErrors.minute && <div className="text-[11px] text-[var(--color-crimson)] mt-1">{fieldErrors.minute}</div>}
        </Group>

        {fieldErrors._form && <div className="text-[13px] text-[var(--color-crimson)]">{fieldErrors._form}</div>}

        <Btn
          type="button"
          variant="crimson"
          disabled={submitting}
          className="justify-center py-3.5 text-[15px] tracking-[0.4px] mt-2"
          onClick={() => void submitForm()}
        >
          {submitting ? "Đang an lá số…" : "✦ An lá số · trò chuyện với thầy"}
        </Btn>
        <div className="text-center text-[11px] text-[var(--color-ink-3)] -mt-1">
          Tiếp tục → bạn đồng ý <button type="button" className="text-[var(--color-crimson)] underline-offset-2 hover:underline cursor-pointer">điều khoản</button> & <button type="button" className="text-[var(--color-crimson)] underline-offset-2 hover:underline cursor-pointer">quyền riêng tư</button>
        </div>
      </div>
    </form>
  );
}

function clientOperationId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="text-[11px] text-[var(--color-ink-3)] tracking-[1px] uppercase mb-1.5 font-medium block">{label}</span>
      {children}
    </label>
  );
}

function Group({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <fieldset className="border-0 p-0 m-0">
      <legend className="text-[11px] text-[var(--color-ink-3)] tracking-[1px] uppercase mb-1.5 font-medium">{label}</legend>
      {children}
    </fieldset>
  );
}

function NumInput({
  value,
  min,
  max,
  onChange,
  flex,
  label,
}: {
  value: number;
  min?: number;
  max?: number;
  onChange: (v: number) => void;
  flex: number;
  label: string;
}) {
  return (
    <input
      type="number"
      aria-label={label}
      {...(min != null ? { min } : {})}
      {...(max != null ? { max } : {})}
      value={value}
      onChange={(e) => onChange(Number(e.target.value))}
      className="px-3.5 py-2.5 border border-[rgba(26,22,17,0.32)] bg-[var(--color-paper)] font-serif text-[20px] outline-none focus:border-[var(--color-crimson)] w-full"
      style={{ flex, minWidth: 0 }}
    />
  );
}
