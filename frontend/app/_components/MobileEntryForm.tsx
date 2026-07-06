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
import {
  createAnonymousOwner,
  createChartProfile,
  createChatSession,
} from "@/services/api/v1/conversation-history";
import { Btn } from "./Buttons";

export function MobileEntryForm() {
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
      const laso = await buildLaso.mutateAsync(apiPayload);
      const profile: UserProfile = { name, gender, calendar, day, month, year, hour, minute };
      saveStash({
        laso,
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
      className="paper-tex flex-1 flex flex-col px-[18px] pt-7 pb-3.5"
    >
      <div className="text-center mb-4">
        <div className="eyebrow" style={{ fontSize: 9 }}>Phép cổ · Nam phái</div>
        <h1 className="font-serif text-[28px] leading-[1.1] font-medium mt-1 tracking-[-0.3px]">
          Lập lá số,<br />
          hỏi <em className="italic text-[var(--color-crimson)] not-italic-fallback" style={{ fontStyle: "italic" }}>Thầy Tuệ</em>
        </h1>
      </div>

      <div className="flex flex-col gap-2.5 flex-1">
        <MLabel label="Họ tên">
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-3 py-2 border border-[rgba(26,22,17,0.32)] bg-[var(--color-paper)] font-serif text-[14px] outline-none focus:border-[var(--color-crimson)]"
            placeholder="Vui lòng nhập họ và tên..."
          />
        </MLabel>

        <div className="grid grid-cols-2 gap-2">
          <MLabel label="Giới">
            <div className="flex gap-1">
              <Btn type="button" variant={gender === "M" ? "primary" : "default"} className="flex-1 justify-center text-[11px] px-2 py-1.5" onClick={() => setGender("M")}>Nam</Btn>
              <Btn type="button" variant={gender === "F" ? "primary" : "default"} className="flex-1 justify-center text-[11px] px-2 py-1.5" onClick={() => setGender("F")}>Nữ</Btn>
            </div>
          </MLabel>
          <MLabel label="Lịch">
            <div className="flex gap-1">
              <Btn type="button" variant={calendar === "duong" ? "primary" : "default"} className="flex-1 justify-center text-[11px] px-2 py-1.5" onClick={() => setCalendar("duong")}>Dương</Btn>
              <Btn type="button" variant={calendar === "am" ? "primary" : "default"} className="flex-1 justify-center text-[11px] px-2 py-1.5" onClick={() => setCalendar("am")}>Âm</Btn>
            </div>
          </MLabel>
        </div>

        <MLabel label="Ngày sinh">
          <div className="flex gap-1">
            <MNum label="Ngày" value={day} min={1} max={31} onChange={setDay} flex={1} />
            <MNum label="Tháng" value={month} min={1} max={12} onChange={setMonth} flex={1} />
            <MNum label="Năm" value={year} min={1900} max={2099} onChange={setYear} flex={1.6} />
          </div>
          {fieldErrors.day && <div className="text-[10px] text-[var(--color-crimson)] mt-1">{fieldErrors.day}</div>}
        </MLabel>

        <MLabel label="Giờ sinh">
          <div className="flex gap-1 items-center">
            <MNum label="Giờ (0-23)" value={hour} min={0} max={23} onChange={setHour} flex={1} />
            <span className="text-[var(--color-ink-3)] font-serif text-[16px]">:</span>
            <MNum label="Phút (0-59)" value={minute} min={0} max={59} onChange={setMinute} flex={1} />
          </div>
          <button
            type="button"
            className="text-[10px] text-[var(--color-crimson)] mt-1 inline-block"
            style={{ borderBottom: "1px dotted" }}
          >
            không biết giờ chính xác?
          </button>
          {fieldErrors.hour && <div className="text-[10px] text-[var(--color-crimson)] mt-1">{fieldErrors.hour}</div>}
          {fieldErrors.minute && <div className="text-[10px] text-[var(--color-crimson)] mt-1">{fieldErrors.minute}</div>}
        </MLabel>

        {fieldErrors._form && <div className="text-[12px] text-[var(--color-crimson)]">{fieldErrors._form}</div>}
      </div>

      <Btn
        type="button"
        variant="crimson"
        disabled={submitting}
        className="justify-center py-3 text-[13px] tracking-[0.4px] mt-3.5"
        onClick={() => void submitForm()}
      >
        {submitting ? "Đang an lá số…" : "✦ An lá số"}
      </Btn>
    </form>
  );
}

function clientOperationId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function MLabel({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="text-[9px] text-[var(--color-ink-3)] uppercase tracking-[1px] mb-1 font-medium block">{label}</span>
      {children}
    </label>
  );
}

function MNum({
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
      className="px-2.5 py-2 border border-[rgba(26,22,17,0.32)] bg-[var(--color-paper)] font-serif text-[16px] outline-none focus:border-[var(--color-crimson)] w-full"
      style={{ flex, minWidth: 0 }}
    />
  );
}
