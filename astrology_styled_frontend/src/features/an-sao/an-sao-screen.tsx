"use client";

import Image from "next/image";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useRef, useState } from "react";

import { Pill } from "@/components/primitives/pill";
import { AuthLinks } from "@/components/shell/auth-links";
import { useDebouncedValue } from "@/hooks/use-debounced-value";
import {
  profileDisplayName,
  useBuildLaso,
  useCreateChartProfile,
  useLasoPreview,
} from "@/lib/api/hooks";
import { describe, isApiError } from "@/lib/http/errors";
import { starKeyFromName } from "@/lib/theme";
import { showToast } from "@/lib/toast";
import { useChartStore } from "@/store/chart-store";
import { usePreferencesStore } from "@/store/preferences-store";

import { BirthConfirmDialog } from "./birth-confirm-dialog";
import {
  type BirthDateInput,
  type BirthTimeInput,
  type Meridiem,
  MERIDIEM,
  canhGioOf,
  toApiBirthTime,
} from "./birth-time";
import { CastingLoader } from "./casting-loader";
import { ConstellationReward } from "./constellation-reward";
import { outcomeFromChart } from "./outcome";
import { SegmentedControl } from "./segmented-control";
import { TimePicker } from "./time-picker";
import { WheelPicker } from "./wheel-picker";

/** The loading interlude's floor, from the design. */
const MIN_LOADING_MS = 2600;
/** Dial-spin settling before a preview fires. */
const PREVIEW_DEBOUNCE_MS = 250;

const DAY_RANGE = { min: 1, max: 31 } as const;
const MONTH_RANGE = { min: 1, max: 12 } as const;
const YEAR_RANGE = { min: 1990, max: 2099 } as const;

const DEFAULT_DATE: BirthDateInput = { year: 2000, month: 1, day: 1 };

function pad2(value: number): string {
  return String(value).padStart(2, "0");
}

/**
 * The casting screen at `/`: birth date wheels, the AM/PM toggle and hour
 * clock, the giới tính selector, the constellation reward — then confirm,
 * loading, and the cast that unlocks the four chart tabs.
 */
export function AnSaoScreen() {
  const router = useRouter();
  const [phase, setPhase] = useState<"form" | "loading">("form");
  const [date, setDate] = useState<BirthDateInput>(DEFAULT_DATE);
  // AM/PM is picked above the face, so it stands on its own and defaults to
  // AM; the hour stays unpicked until touched, which is what the guard reads.
  const [meridiem, setMeridiem] = useState<Meridiem>(MERIDIEM.AM);
  const [hour12, setHour12] = useState<number | null>(null);
  const [gender, setGender] = useState<"M" | "F" | null>(null);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [clockPulse, setClockPulse] = useState(0);

  const time = useMemo<BirthTimeInput | null>(
    () => (hour12 === null ? null : { hour12, meridiem }),
    [hour12, meridiem],
  );

  const clockRef = useRef<HTMLDivElement>(null);
  const genderRef = useRef<HTMLDivElement>(null);

  const setPreviewOutcome = useChartStore((state) => state.setPreviewOutcome);
  const castChart = useChartStore((state) => state.castChart);
  const muteBirthConfirm = usePreferencesStore((state) => state.muteBirthConfirm);

  // --- Reward preview: debounce the dials, map to the API tuple, fetch. ---
  const previewInput = useMemo(() => (time === null ? null : { date, time }), [date, time]);
  const debouncedInput = useDebouncedValue(previewInput, PREVIEW_DEBOUNCE_MS);
  const previewBirth = useMemo(() => {
    if (debouncedInput === null) return null;
    const mapped = toApiBirthTime(debouncedInput.date, debouncedInput.time);
    return mapped.ok ? ({ calendar: "solar", ...mapped.value } as const) : null;
  }, [debouncedInput]);
  const preview = useLasoPreview(previewBirth);

  useEffect(() => {
    if (preview.data === undefined) return;
    setPreviewOutcome({ stars: preview.data.chinh_tinh.map(starKeyFromName) });
  }, [preview.data, setPreviewOutcome]);

  // The preview accent belongs to this screen. Leaving without casting — or
  // casting, which replaces it — must not leave it tinting the rest of the app.
  useEffect(() => () => setPreviewOutcome(null), [setPreviewOutcome]);

  // --- Casting -------------------------------------------------------------
  const buildLaso = useBuildLaso();
  const createProfile = useCreateChartProfile();

  const requestCast = () => {
    if (time === null) {
      showToast("Chọn giờ sinh để an sao chính xác nhé ✦");
      setClockPulse((count) => count + 1);
      clockRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
      return;
    }
    if (gender === null) {
      showToast("Cho Thiên Hạc biết giới tính của bạn nhé ✦");
      genderRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
      return;
    }
    if (muteBirthConfirm) {
      void cast();
    } else {
      setConfirmOpen(true);
    }
  };

  const cast = async () => {
    if (time === null || gender === null) return;
    const mapped = toApiBirthTime(date, time);
    if (!mapped.ok) {
      showToast("Ngày giờ này vượt quá phạm vi Thiên Hạc an được (năm 1990 – 2099) nhé.");
      return;
    }

    const birth = { calendar: "solar" as const, ...mapped.value, gender };

    setConfirmOpen(false);
    setPhase("loading");
    const minimumLoading = new Promise((resolve) => setTimeout(resolve, MIN_LOADING_MS));
    try {
      const chart = await buildLaso.mutateAsync(birth);
      const [, profileId] = await Promise.all([
        minimumLoading,
        // Auto-save starts only after a valid build. It must never fail the
        // cast, so it resolves to the profile id or null.
        createProfile
          .mutateAsync({ display_name: profileDisplayName(birth), birth_info: birth })
          .then((res) => res.chart_profile.id)
          .catch(() => null),
      ]);
      castChart(outcomeFromChart(chart), chart.id, birth, profileId);
      router.push("/ban-menh");
    } catch (error) {
      setPhase("form");
      showToast(
        isApiError(error) ? describe(error.error) : "Có lỗi xảy ra khi an sao. Bạn thử lại nhé.",
      );
    }
  };

  if (phase === "loading") return <CastingLoader />;

  const canhGio = time === null ? null : canhGioOf(time.hour12, time.meridiem);
  const confirmSummary =
    time === null || canhGio === null
      ? ""
      : `${pad2(date.day)} · ${pad2(date.month)} · ${date.year} · ${time.hour12} ${time.meridiem} · Giờ ${canhGio.chi}`;

  // The min-heights let `content-center` do its job: they give the grid the
  // vertical room left over after the shell chrome, so the two panes centre
  // instead of hugging the top. (ScreenPad top + bottom + tab bar at md;
  // top bar + ScreenPad at lg.)
  return (
    <div className="relative flex flex-col pt-[76px] md:grid md:min-h-[calc(100dvh-140px-var(--safe-t)-var(--safe-b))] md:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] md:content-center md:gap-x-10 md:gap-y-0 lg:min-h-[calc(100dvh-152px-var(--safe-t))] lg:pt-0">
      <div className="absolute top-0 right-0 left-0 flex h-14 items-center justify-between gap-3 lg:hidden">
        <div className="flex min-w-0 shrink-0 items-center gap-2 max-[349px]:gap-1.5">
          <Image
            src="/assets/icons/favicon-48x48.png"
            alt=""
            width={48}
            height={48}
            className="size-10 shrink-0 drop-shadow-[0_0_10px_rgba(255,222,143,0.26)] max-[349px]:size-8"
          />
          <span className="truncate font-display text-lg font-semibold text-ink max-[349px]:text-sm">
            Thiên Hạc
          </span>
        </div>
        <AuthLinks className="min-w-0 shrink-0 justify-end [&_a]:px-3 max-[349px]:gap-1 max-[349px]:[&_a]:px-2 max-[349px]:[&_a]:text-[11px]" />
      </div>
      {/* Head — story column on the left from md up. */}
      <div className="text-center md:col-start-1 md:row-start-1 md:text-left">
        <div className="text-[10px] font-bold tracking-[0.28em] text-accent uppercase [text-shadow:0_0_14px_var(--accent-glow)]">
          An sao · lập lá số
        </div>
        <h1 className="mt-[9px] font-display text-[clamp(26px,7.4vw,31px)] leading-[1.08] font-semibold tracking-[-0.01em] md:text-[clamp(30px,4.4vw,38px)]">
          Chạm vào bầu trời
          <br />
          ngày bạn sinh ra
        </h1>
        <p className="mt-[5px] text-[13.5px] font-light text-muted md:mt-[9px] md:max-w-[34ch] md:text-[15px]">
          Xoay các vòng sao để nhập ngày sinh — chòm sao mệnh của bạn sẽ dần hiện lên.
        </p>
      </div>

      {/* The machine */}
      <div className="glass mt-4 px-[14px] py-[12px] md:col-start-2 md:row-span-2 md:row-start-1 md:mt-0 md:self-center">
        <div className="relative grid grid-cols-[1fr_1fr_1.15fr] gap-[10px]">
          <div
            aria-hidden="true"
            className="pointer-events-none absolute right-[6px] bottom-[55px] left-[6px] z-2 h-[46px] rounded-[14px] border border-accent-glow bg-[linear-gradient(115deg,color-mix(in_srgb,var(--accent)_16%,transparent),color-mix(in_srgb,var(--accent-2)_16%,transparent))]"
          />
          <WheelPicker
            label="Ngày"
            min={DAY_RANGE.min}
            max={DAY_RANGE.max}
            pad
            value={date.day}
            onChange={(day) => setDate((current) => ({ ...current, day }))}
          />
          <WheelPicker
            label="Tháng"
            min={MONTH_RANGE.min}
            max={MONTH_RANGE.max}
            pad
            value={date.month}
            onChange={(month) => setDate((current) => ({ ...current, month }))}
          />
          <WheelPicker
            label="Năm"
            min={YEAR_RANGE.min}
            max={YEAR_RANGE.max}
            value={date.year}
            onChange={(year) => setDate((current) => ({ ...current, year }))}
          />
        </div>

        <div className="mt-[12px] text-center text-[11px] tracking-[0.24em] text-muted uppercase">
          Giờ sinh <span className="text-accent">· bắt buộc</span>
        </div>
        <div className="mx-auto mt-[8px] w-[min(218px,66vw)]">
          <SegmentedControl
            label="Buổi trong ngày"
            options={[
              { value: MERIDIEM.AM, label: "AM" },
              { value: MERIDIEM.PM, label: "PM" },
            ]}
            value={meridiem}
            onChange={setMeridiem}
          />
        </div>
        <TimePicker
          ref={clockRef}
          value={hour12}
          meridiem={meridiem}
          onChange={setHour12}
          pulseKey={clockPulse}
        />

        <div ref={genderRef} className="mt-[14px]">
          <div className="mb-[6px] text-center text-[11px] tracking-[0.24em] text-muted uppercase">
            Giới tính <span className="text-accent">· bắt buộc</span>
          </div>
          <SegmentedControl
            label="Giới tính"
            options={[
              { value: "M", label: "Nam" },
              { value: "F", label: "Nữ" },
            ]}
            value={gender}
            onChange={setGender}
          />
        </div>
      </div>

      {/* Right above the cast button on phone: the reward has to be in view at
          the moment the dials are being turned, and by then the head of the
          page has scrolled away. From md up it sits under the story column. */}
      <div className="mt-2 md:col-start-1 md:row-start-2 md:mt-6 md:self-start">
        <ConstellationReward
          stars={preview.data?.chinh_tinh.map(starKeyFromName) ?? null}
          names={preview.data?.chinh_tinh ?? []}
        />
      </div>

      <div className="mt-[10px] flex flex-col gap-[10px] md:col-start-2 md:row-start-3 md:mt-[22px]">
        <Pill className="w-full" onClick={requestCast}>
          ✦ Luận giải lá số của tôi
        </Pill>
      </div>

      <BirthConfirmDialog
        open={confirmOpen}
        onOpenChange={setConfirmOpen}
        summary={confirmSummary}
        onConfirm={() => void cast()}
      />
    </div>
  );
}
