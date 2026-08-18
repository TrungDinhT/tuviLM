"use client";

import { useEffect, useMemo, useState } from "react";
import { createPortal } from "react-dom";

import type {
  ConclusionEvidence,
  StrengthFinding,
  UserProfile,
  WeaknessFinding,
  WeaknessKind,
} from "../_lib/types";
import { useStrengthWeakness } from "@/services/api/v1/laso/strength-weakness";
import { Btn } from "./Buttons";
import { Eyebrow } from "./Eyebrow";

const WEAKNESS_LABELS: Record<WeaknessKind, string> = {
  han_che_truc_tiep: "Hạn chế trực tiếp",
  qua_da: "Mặt trái của thế mạnh",
  xung_dot: "Xung đột khuynh hướng",
};

type CapabilityPanelState =
  | { view: "overview" }
  | {
      view: "detail";
      findingType: "strength" | "weakness";
      findingIndex: number;
    };

interface StrengthWeaknessPanelProps {
  profile: UserProfile;
  compact?: boolean;
}

export function StrengthWeaknessPanel({
  profile,
  compact = false,
}: StrengthWeaknessPanelProps) {
  const birthInfo = useMemo(
    () => ({
      day: profile.day,
      month: profile.month,
      year: profile.year,
      hour: profile.hour,
      gender: profile.gender,
    }),
    [profile.day, profile.gender, profile.hour, profile.month, profile.year],
  );
  const analysis = useStrengthWeakness(birthInfo);
  const result = analysis.data;
  const [panelState, setPanelState] = useState<CapabilityPanelState>({
    view: "overview",
  });
  const [summaryExpanded, setSummaryExpanded] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);

  useEffect(() => {
    if (!modalOpen) return;

    const previousOverflow = document.body.style.overflow;
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") setModalOpen(false);
    };
    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", closeOnEscape);
    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", closeOnEscape);
    };
  }, [modalOpen]);

  const showOverview = () => setPanelState({ view: "overview" });

  const analyze = async () => {
    showOverview();
    setSummaryExpanded(false);
    const response = await analysis.refetch();
    if (!response.error && response.data) setModalOpen(true);
  };

  const openModal = () => {
    showOverview();
    setSummaryExpanded(false);
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
    showOverview();
  };

  const selectedStrength =
    result && panelState.view === "detail" && panelState.findingType === "strength"
      ? result.diem_manh[panelState.findingIndex]
      : undefined;
  const selectedWeakness =
    result && panelState.view === "detail" && panelState.findingType === "weakness"
      ? result.diem_yeu[panelState.findingIndex]
      : undefined;

  const openStrength = (index: number) =>
    setPanelState({ view: "detail", findingType: "strength", findingIndex: index });
  const openWeakness = (index: number) =>
    setPanelState({ view: "detail", findingType: "weakness", findingIndex: index });
  const openRelatedStrength = (capabilityId: string) => {
    const index = result?.diem_manh.findIndex(
      (finding) => finding.nang_luc_id === capabilityId,
    );
    if (index !== undefined && index >= 0) openStrength(index);
  };

  return (
    <>
      <section
        className={`border border-[rgba(139,42,31,0.48)] ${compact ? "p-3" : "p-4"}`}
        style={{ background: "rgba(255,252,245,0.76)" }}
        aria-labelledby="strength-weakness-launcher-title"
      >
        <Eyebrow>✦ Khám phá năng lực</Eyebrow>
        <h2
          id="strength-weakness-launcher-title"
          className="font-serif text-[20px] leading-[1.15] mt-1 text-[var(--color-ink)]"
        >
          Chân dung năng lực
        </h2>
        <p className="mt-2 text-[12.5px] leading-[1.55] text-[var(--color-ink-2)]">
          Xem nhanh những điểm mạnh nổi bật, mặt trái và căn cứ Tử Vi trong một
          hồ sơ riêng.
        </p>
        <Btn
          type="button"
          variant="crimson"
          className="justify-center w-full mt-3"
          disabled={analysis.isFetching}
          onClick={() => {
            if (result) openModal();
            else void analyze();
          }}
        >
          {analysis.isFetching
            ? "Đang luận giải…"
            : result
              ? "Mở hồ sơ năng lực"
              : "✦ Xem điểm mạnh & điểm yếu"}
        </Btn>
        {result && (
          <button
            type="button"
            className="block mx-auto mt-2 text-[10.5px] text-[var(--color-ink-3)] cursor-pointer hover:text-[var(--color-crimson)] hover:underline underline-offset-2 disabled:opacity-50"
            disabled={analysis.isFetching}
            onClick={() => void analyze()}
          >
            Luận lại từ lá số
          </button>
        )}
        {analysis.isFetching && (
          <p className="text-[11px] text-[var(--color-ink-3)] mt-2 text-center">
            Đang đọc các căn cứ nổi bật, quá trình này có thể mất một lúc.
          </p>
        )}
        {analysis.error && (
          <div
            role="alert"
            className="mt-3 border-l-2 border-[var(--color-crimson)] pl-3 text-[12px] leading-[1.5] text-[var(--color-crimson)]"
          >
            {analysis.error instanceof Error
              ? analysis.error.message
              : "Không luận được năng lực. Vui lòng thử lại."}
          </div>
        )}
      </section>

      {modalOpen &&
        result &&
        createPortal(
          <CapabilityModal
            error={analysis.error}
            isDetail={panelState.view === "detail"}
            isFetching={analysis.isFetching}
            onBack={showOverview}
            onAnalyze={() => void analyze()}
            onClose={closeModal}
          >
            {panelState.view === "overview" && (
              <CapabilityOverview
                summary={result.tong_quan}
                summaryExpanded={summaryExpanded}
                strengths={result.diem_manh}
                weaknesses={result.diem_yeu}
                onToggleSummary={() =>
                  setSummaryExpanded((expanded) => !expanded)
                }
                onOpenStrength={openStrength}
                onOpenWeakness={openWeakness}
              />
            )}

            {selectedStrength && (
              <CapabilityDetail
                kind="strength"
                finding={selectedStrength}
                strengths={result.diem_manh}
                onOpenRelatedStrength={openRelatedStrength}
              />
            )}

            {selectedWeakness && (
              <CapabilityDetail
                kind="weakness"
                finding={selectedWeakness}
                strengths={result.diem_manh}
                onOpenRelatedStrength={openRelatedStrength}
              />
            )}
          </CapabilityModal>,
          document.body,
        )}
    </>
  );
}

interface CapabilityModalProps {
  error: Error | null;
  isDetail: boolean;
  isFetching: boolean;
  onBack: () => void;
  onAnalyze: () => void;
  onClose: () => void;
  children: React.ReactNode;
}

function CapabilityModal({
  error,
  isDetail,
  isFetching,
  onBack,
  onAnalyze,
  onClose,
  children,
}: CapabilityModalProps) {
  return (
    <div className="fixed inset-0 z-50">
      <div
        className="absolute inset-0 bg-[rgba(26,22,17,0.38)] anim-fade-in"
        style={{ backdropFilter: "blur(3px)" }}
        onClick={onClose}
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="capability-modal-title"
        aria-busy={isFetching}
        className="absolute inset-y-3 sm:inset-y-6 md:inset-y-10 left-1/2 w-[1120px] max-w-[calc(100vw-24px)] sm:max-w-[calc(100vw-48px)] flex flex-col overflow-hidden bg-[rgba(255,252,245,0.99)] border-[1.5px] border-[var(--color-ink)] anim-scale-up"
        style={{ boxShadow: "0 24px 80px rgba(26,22,17,0.3)" }}
      >
        <header className="shrink-0 px-4 sm:px-6 md:px-8 py-4 sm:py-5 border-b border-[rgba(26,22,17,0.14)] flex items-start justify-between gap-4">
          <div>
            <Eyebrow>✦ Khám phá năng lực</Eyebrow>
            <h2
              id="capability-modal-title"
              className="font-serif text-[22px] sm:text-[26px] md:text-[30px] leading-[1.12] mt-1 text-[var(--color-ink)]"
            >
              {isDetail
                ? "Chi tiết năng lực"
                : "Điểm mạnh & điểm cần lưu ý"}
            </h2>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            {isDetail && (
              <button
                type="button"
                className="text-[11px] sm:text-[12px] text-[var(--color-crimson)] cursor-pointer hover:underline underline-offset-2"
                onClick={onBack}
              >
                ← Tổng quan
              </button>
            )}
            {!isDetail && (
              <button
                type="button"
                className="hidden sm:inline text-[11px] text-[var(--color-ink-3)] cursor-pointer hover:text-[var(--color-crimson)] hover:underline underline-offset-2 disabled:opacity-50"
                disabled={isFetching}
                onClick={onAnalyze}
              >
                {isFetching ? "Đang luận…" : "Luận lại"}
              </button>
            )}
            <Btn
              type="button"
              variant="ghost"
              className="!px-2 text-[16px]"
              onClick={onClose}
              aria-label="Đóng hồ sơ năng lực"
            >
              ✕
            </Btn>
          </div>
        </header>

        <div className="flex-1 min-h-0 overflow-y-auto px-4 sm:px-6 md:px-8 pb-6 md:pb-8">
          {isFetching && (
            <div className="sticky top-0 z-10 -mx-4 sm:-mx-6 md:-mx-8 px-4 py-2 text-center text-[11px] text-[var(--color-crimson)] bg-[rgba(255,252,245,0.96)] border-b border-[rgba(139,42,31,0.14)]">
              Đang cập nhật hồ sơ từ lá số…
            </div>
          )}
          {error && (
            <div
              role="alert"
              className="mt-4 border-l-2 border-[var(--color-crimson)] pl-3 text-[12px] leading-[1.5] text-[var(--color-crimson)]"
            >
              {error.message}
            </div>
          )}
          {children}
        </div>
      </div>
    </div>
  );
}

interface CapabilityOverviewProps {
  summary: string;
  summaryExpanded: boolean;
  strengths: StrengthFinding[];
  weaknesses: WeaknessFinding[];
  onToggleSummary: () => void;
  onOpenStrength: (index: number) => void;
  onOpenWeakness: (index: number) => void;
}

function CapabilityOverview({
  summary,
  summaryExpanded,
  strengths,
  weaknesses,
  onToggleSummary,
  onOpenStrength,
  onOpenWeakness,
}: CapabilityOverviewProps) {
  return (
    <div className="mt-5 flex flex-col gap-7 anim-fade-in">
      <div className="max-w-[900px] border-y border-[rgba(26,22,17,0.12)] py-3.5">
        <div className="text-[9px] uppercase tracking-[1.1px] text-[var(--color-ink-3)]">
          Chân dung tổng quát
        </div>
        <p
          className={`font-serif text-[14px] sm:text-[15px] md:text-[16px] leading-[1.6] mt-1 text-[var(--color-ink)] ${
            summaryExpanded ? "" : "line-clamp-3"
          }`}
        >
          {summary}
        </p>
        <button
          type="button"
          className="mt-1.5 text-[10.5px] text-[var(--color-crimson)] cursor-pointer hover:underline underline-offset-2"
          aria-expanded={summaryExpanded}
          onClick={onToggleSummary}
        >
          {summaryExpanded ? "Thu gọn" : "Xem tổng quan đầy đủ"}
        </button>
      </div>

      <FindingSection
        title="Điểm mạnh nổi bật"
        count={strengths.length}
      >
        {strengths.map((finding, index) => (
          <FindingCard
            key={finding.nang_luc_id}
            kind="strength"
            title={finding.nang_luc}
            description={finding.mo_ta}
            onClick={() => onOpenStrength(index)}
          />
        ))}
      </FindingSection>

      <FindingSection
        title="Điểm cần lưu ý"
        count={weaknesses.length}
      >
        {weaknesses.map((finding, index) => (
          <FindingCard
            key={`${finding.loai}-${finding.ten}-${index}`}
            kind="weakness"
            title={finding.ten}
            description={finding.mo_ta}
            badge={WEAKNESS_LABELS[finding.loai]}
            onClick={() => onOpenWeakness(index)}
          />
        ))}
      </FindingSection>
    </div>
  );
}

interface FindingSectionProps {
  title: string;
  count: number;
  children: React.ReactNode;
}

function FindingSection({ title, count, children }: FindingSectionProps) {
  if (count === 0) return null;
  return (
    <section>
      <div className="flex items-baseline justify-between gap-2 mb-2">
        <h3 className="font-serif text-[18px] md:text-[20px] text-[var(--color-ink)]">
          {title}
        </h3>
        <span className="text-[9px] tabular-nums text-[var(--color-ink-3)]">
          {String(count).padStart(2, "0")}
        </span>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 items-start gap-3">
        {children}
      </div>
    </section>
  );
}

interface FindingCardProps {
  kind: "strength" | "weakness";
  title: string;
  description: string;
  badge?: string;
  onClick: () => void;
}

function FindingCard({
  kind,
  title,
  description,
  badge,
  onClick,
}: FindingCardProps) {
  const isStrength = kind === "strength";
  return (
    <button
      type="button"
      className={`group self-start w-full p-4 text-left border cursor-pointer transition-colors duration-150 ${
        isStrength
          ? "border-[rgba(26,22,17,0.2)] bg-[rgba(255,252,245,0.85)] hover:border-[rgba(26,22,17,0.48)]"
          : "border-[rgba(139,42,31,0.24)] bg-[rgba(139,42,31,0.035)] hover:border-[rgba(139,42,31,0.52)]"
      }`}
      onClick={onClick}
      aria-label={`Xem chi tiết: ${title}`}
    >
      <div className="flex items-start justify-between gap-2">
        <span
          className={`grid place-items-center size-7 shrink-0 rounded-full text-[12px] ${
            isStrength
              ? "bg-[rgba(26,22,17,0.08)] text-[var(--color-ink)]"
              : "bg-[rgba(139,42,31,0.1)] text-[var(--color-crimson)]"
          }`}
          aria-hidden="true"
        >
          {isStrength ? "✦" : "◇"}
        </span>
        <span className="text-[15px] leading-none text-[var(--color-ink-3)] transition-transform duration-150 group-hover:translate-x-0.5">
          ›
        </span>
      </div>
      {badge && (
        <span className="inline-block mt-2 text-[8.5px] uppercase tracking-[0.75px] text-[var(--color-crimson)]">
          {badge}
        </span>
      )}
      <h4 className={`font-serif text-[17px] leading-[1.25] ${badge ? "mt-1" : "mt-2"}`}>
        {title}
      </h4>
      <p className="line-clamp-3 text-[12.5px] leading-[1.55] mt-1.5 text-[var(--color-ink-2)]">
        {description}
      </p>
      <span className="inline-block mt-2 text-[9.5px] text-[var(--color-ink-3)] group-hover:text-[var(--color-crimson)]">
        Xem chi tiết
      </span>
    </button>
  );
}

type CapabilityDetailProps =
  | {
      kind: "strength";
      finding: StrengthFinding;
      strengths: StrengthFinding[];
      onOpenRelatedStrength: (capabilityId: string) => void;
    }
  | {
      kind: "weakness";
      finding: WeaknessFinding;
      strengths: StrengthFinding[];
      onOpenRelatedStrength: (capabilityId: string) => void;
    };

function CapabilityDetail(props: CapabilityDetailProps) {
  const isStrength = props.kind === "strength";
  const title = isStrength ? props.finding.nang_luc : props.finding.ten;
  const relatedIds = isStrength ? [] : props.finding.lien_quan_diem_manh;

  return (
    <article className="max-w-[780px] mx-auto mt-6 pb-2 anim-fade-in">
      <div
        className={`border-l-[3px] px-4 sm:px-5 py-4 ${
          isStrength
            ? "border-[var(--color-ink)] bg-[rgba(26,22,17,0.04)]"
            : "border-[var(--color-crimson)] bg-[rgba(139,42,31,0.045)]"
        }`}
      >
        <div className="flex items-center gap-2 text-[9px] uppercase tracking-[0.85px] text-[var(--color-ink-3)]">
          <span aria-hidden="true">{isStrength ? "✦" : "◇"}</span>
          <span>
            {isStrength
              ? "Điểm mạnh nổi bật"
              : WEAKNESS_LABELS[props.finding.loai]}
          </span>
        </div>
        <h3 className="font-serif text-[24px] sm:text-[28px] leading-[1.18] mt-2 text-[var(--color-ink)]">
          {title}
        </h3>
        <p className="text-[13px] sm:text-[14px] leading-[1.6] mt-2 text-[var(--color-ink-2)]">
          {props.finding.mo_ta}
        </p>
      </div>

      <section className="mt-4">
        <h4 className="text-[9px] uppercase tracking-[1px] text-[var(--color-ink-3)]">
          Giải thích
        </h4>
        <p className="mt-1.5 whitespace-pre-line font-serif text-[14px] sm:text-[15px] leading-[1.7] text-[var(--color-ink)]">
          {props.finding.giai_thich}
        </p>
      </section>

      {relatedIds.length > 0 && (
        <section className="mt-4 pt-3 border-t border-[rgba(26,22,17,0.12)]">
          <h4 className="text-[9px] uppercase tracking-[1px] text-[var(--color-ink-3)]">
            Mặt trái của
          </h4>
          <div className="flex flex-wrap gap-1.5 mt-2">
            {relatedIds.map((capabilityId) => {
              const strength = props.strengths.find(
                (finding) => finding.nang_luc_id === capabilityId,
              );
              return (
                <button
                  key={capabilityId}
                  type="button"
                  className="border border-[rgba(26,22,17,0.18)] bg-[rgba(255,252,245,0.9)] px-2 py-1 text-[10.5px] text-[var(--color-ink-2)] cursor-pointer hover:border-[var(--color-crimson)] hover:text-[var(--color-crimson)]"
                  onClick={() => props.onOpenRelatedStrength(capabilityId)}
                >
                  ✦ {strength?.nang_luc ?? "Điểm mạnh liên quan"}
                </button>
              );
            })}
          </div>
        </section>
      )}

      <Evidence evidence={props.finding.can_cu} />
    </article>
  );
}

function Evidence({ evidence }: { evidence: ConclusionEvidence[] }) {
  if (evidence.length === 0) return null;
  return (
    <details className="mt-4 pt-3 border-t border-[rgba(26,22,17,0.12)] group/evidence">
      <summary className="flex items-center justify-between gap-2 cursor-pointer list-none text-[10.5px] text-[var(--color-ink-2)] hover:text-[var(--color-crimson)]">
        <span className="uppercase tracking-[0.8px]">Căn cứ Tử Vi</span>
        <span className="text-[var(--color-ink-3)]">
          {evidence.length} căn cứ&nbsp;＋
        </span>
      </summary>
      <ul className="mt-2.5 flex flex-col gap-2.5">
        {evidence.map((item, index) => (
          <li
            key={`${item.evidence_id}-${index}`}
            className="border-l border-[rgba(139,42,31,0.32)] pl-2.5"
          >
            <div className="font-serif text-[12.5px] leading-[1.35] text-[var(--color-ink)]">
              {item.ten}
            </div>
            {item.mo_ta_ngan && (
              <p className="text-[10.5px] leading-[1.5] mt-0.5 text-[var(--color-ink-3)]">
                {item.mo_ta_ngan}
              </p>
            )}
          </li>
        ))}
      </ul>
    </details>
  );
}
