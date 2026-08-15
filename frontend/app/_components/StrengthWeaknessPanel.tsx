"use client";

import { useMemo, useState } from "react";
import type {
  StrengthWeaknessAssessment,
  StrengthWeaknessDimension,
  StrengthWeaknessLevel,
} from "../_lib/types";
import { useStrengthWeaknessAssessment } from "@/services/api/v1/strength-weakness";
import { Btn } from "./Buttons";
import { Eyebrow } from "./Eyebrow";

interface StrengthWeaknessPanelProps {
  ownerId?: string;
  sessionId?: string;
  onClose: () => void;
}

interface DimensionMeta {
  id: StrengthWeaknessDimension;
  label: string;
  description: string;
}

const DIMENSIONS: DimensionMeta[] = [
  { id: "analysis_reasoning", label: "Phân tích", description: "Phân rã, đối chiếu và suy luận từ thông tin." },
  { id: "learning_absorption", label: "Học hỏi", description: "Tiếp nhận điều mới và cập nhật hiểu biết." },
  { id: "foresight_preparedness", label: "Nhìn trước", description: "Thấy hệ quả, rủi ro và phương án dự phòng." },
  { id: "decision_making", label: "Quyết định", description: "Cân nhắc đánh đổi và chốt lựa chọn." },
  { id: "action_execution", label: "Hành động", description: "Biến lựa chọn thành tiến độ và kết quả cụ thể." },
  { id: "structuring_organization", label: "Tổ chức", description: "Sắp xếp thông tin, nguồn lực và quy trình." },
  { id: "expression_persuasion", label: "Biểu đạt", description: "Diễn đạt, giải thích và thuyết phục." },
  { id: "adaptability", label: "Thích ứng", description: "Đổi cách vận hành theo hoàn cảnh và phản hồi." },
  { id: "creativity_new_approaches", label: "Sáng tạo", description: "Tạo khả năng và cách tiếp cận mới." },
  { id: "collaboration_coordination", label: "Phối hợp", description: "Phối hợp ngang với người khác." },
  { id: "leadership_mobilization", label: "Dẫn dắt", description: "Đặt hướng và huy động tập thể." },
];

const LEVEL_ORDER: StrengthWeaknessLevel[] = [
  "nearly_absent",
  "very_weak",
  "weak",
  "improvable",
  "normal",
  "above_normal",
  "good",
  "very_good",
  "excellent",
];

const LEVEL_META: Record<StrengthWeaknessLevel, { label: string; radius: number; color: string }> = {
  nearly_absent: { label: "Gần như không có", radius: 52, color: "#991b1b" },
  very_weak: { label: "Rất yếu", radius: 68, color: "#b72b27" },
  weak: { label: "Yếu", radius: 84, color: "#cf4d38" },
  improvable: { label: "Có thể cải thiện được", radius: 101, color: "#dc8042" },
  normal: { label: "Bình thường", radius: 119, color: "#aa945f" },
  above_normal: { label: "Hơn bình thường", radius: 136, color: "#7f9a67" },
  good: { label: "Tốt", radius: 152, color: "#548a67" },
  very_good: { label: "Rất tốt", radius: 165, color: "#34765d" },
  excellent: { label: "Xuất sắc", radius: 176, color: "#145f4b" },
};

const LEVEL_GRADIENT = `linear-gradient(90deg, ${LEVEL_ORDER.map(
  (level) => LEVEL_META[level].color,
).join(", ")})`;

const CENTER = 300;
const CORE_RADIUS = 38;
const MAX_RADIUS = 176;
const LABEL_RADIUS = 225;
const HALF_WING_ANGLE = 10.5;

function polarPoint(radius: number, angleDegrees: number): [number, number] {
  const radians = ((angleDegrees - 90) * Math.PI) / 180;
  return [
    CENTER + radius * Math.cos(radians),
    CENTER + radius * Math.sin(radians),
  ];
}

function wingPoints(angle: number, radius: number): string {
  const left = polarPoint(CORE_RADIUS, angle - HALF_WING_ANGLE);
  const tip = polarPoint(radius, angle);
  const right = polarPoint(CORE_RADIUS, angle + HALF_WING_ANGLE);
  return `${left[0]},${left[1]} ${tip[0]},${tip[1]} ${right[0]},${right[1]}`;
}

function StrengthWeaknessStar({
  assessment,
  selected,
  onSelect,
}: {
  assessment: StrengthWeaknessAssessment;
  selected: StrengthWeaknessDimension;
  onSelect: (dimension: StrengthWeaknessDimension) => void;
}) {
  return (
    <div className="relative mx-auto w-full max-w-[680px]" aria-label="Biểu đồ năng lực 11 cánh">
      <svg viewBox="0 0 600 600" className="block h-auto w-full overflow-visible" role="img">
        <title>Hoa thị điểm mạnh và điểm yếu gồm 11 cánh năng lực</title>

        {[52, 84, 119, 152, MAX_RADIUS].map((radius) => (
          <circle
            key={radius}
            cx={CENTER}
            cy={CENTER}
            r={radius}
            fill="none"
            stroke="rgba(26,22,17,0.10)"
            strokeDasharray="2 7"
          />
        ))}

        {DIMENSIONS.map((dimension, index) => {
          const angle = (360 / DIMENSIONS.length) * index;
          const level = assessment.scores[dimension.id];
          const levelMeta = LEVEL_META[level];
          const labelPoint = polarPoint(LABEL_RADIUS, angle);
          const selectedWing = dimension.id === selected;
          const textAnchor = labelPoint[0] < CENTER - 24
            ? "end"
            : labelPoint[0] > CENTER + 24
              ? "start"
              : "middle";

          return (
            <g
              key={dimension.id}
              role="button"
              tabIndex={0}
              aria-label={`${dimension.label}: ${levelMeta.label}`}
              onClick={() => onSelect(dimension.id)}
              onKeyDown={(event) => {
                if (event.key === "Enter" || event.key === " ") {
                  event.preventDefault();
                  onSelect(dimension.id);
                }
              }}
              className="cursor-pointer outline-none"
            >
              <polygon
                points={wingPoints(angle, MAX_RADIUS)}
                fill={selectedWing ? `${levelMeta.color}12` : "rgba(26,22,17,0.025)"}
                stroke={selectedWing ? levelMeta.color : "rgba(26,22,17,0.16)"}
                strokeWidth={selectedWing ? 2 : 1}
              />
              <polygon
                points={wingPoints(angle, levelMeta.radius)}
                fill={levelMeta.color}
                fillOpacity={selectedWing ? 0.94 : 0.72}
                stroke={levelMeta.color}
                strokeWidth={selectedWing ? 2.5 : 1}
              />
              <circle
                cx={polarPoint(levelMeta.radius, angle)[0]}
                cy={polarPoint(levelMeta.radius, angle)[1]}
                r={selectedWing ? 5 : 3}
                fill={selectedWing ? "#f4ede0" : levelMeta.color}
                stroke={levelMeta.color}
                strokeWidth={2}
              />
              <text
                x={labelPoint[0]}
                y={labelPoint[1]}
                textAnchor={textAnchor}
                dominantBaseline="middle"
                fill={selectedWing ? levelMeta.color : "#4a4239"}
                fontSize={selectedWing ? 13 : 12}
                fontWeight={selectedWing ? 700 : 500}
                fontFamily="var(--font-sans)"
              >
                {dimension.label}
              </text>
            </g>
          );
        })}

        <circle cx={CENTER} cy={CENTER} r={CORE_RADIUS + 5} fill="#f4ede0" stroke="#8b2a1f" strokeWidth="1.5" />
        <text x={CENTER} y={CENTER - 4} textAnchor="middle" fill="#8b2a1f" fontSize="18" fontFamily="var(--font-serif)" fontStyle="italic">11</text>
        <text x={CENTER} y={CENTER + 13} textAnchor="middle" fill="#7a705f" fontSize="8" letterSpacing="1.2">NĂNG LỰC</text>
      </svg>
    </div>
  );
}

function AssessmentContent({ assessment }: { assessment: StrengthWeaknessAssessment }) {
  const initialDimension = assessment.notable_dimensions[0]?.dimension ?? DIMENSIONS[0].id;
  const [selected, setSelected] = useState<StrengthWeaknessDimension>(initialDimension);
  const selectedMeta = DIMENSIONS.find((item) => item.id === selected) ?? DIMENSIONS[0];
  const level = assessment.scores[selected];
  const explanation = assessment.notable_dimensions.find((item) => item.dimension === selected);
  const orderedNotable = useMemo(
    () => DIMENSIONS.flatMap((dimension) => {
      const item = assessment.notable_dimensions.find((entry) => entry.dimension === dimension.id);
      return item ? [item] : [];
    }),
    [assessment.notable_dimensions],
  );

  return (
    <div className="grid min-h-0 flex-1 grid-cols-1 overflow-y-auto lg:grid-cols-[minmax(0,1.18fr)_minmax(320px,0.82fr)] lg:overflow-hidden">
      <section className="flex min-h-[520px] flex-col items-center justify-center border-b border-[rgba(26,22,17,0.14)] p-4 sm:p-7 lg:min-h-0 lg:border-b-0 lg:border-r">
        <StrengthWeaknessStar assessment={assessment} selected={selected} onSelect={setSelected} />
        <div className="w-full max-w-[620px] px-2 text-[9px] text-[var(--color-ink-3)] sm:text-[10px]">
          <div
            className="h-2.5 w-full rounded-full border border-[rgba(26,22,17,0.12)]"
            style={{ background: LEVEL_GRADIENT }}
            role="img"
            aria-label="Phổ năng lực từ gần như không có màu đỏ đến xuất sắc màu xanh"
          />
          <div className="mt-1 hidden grid-cols-9 gap-1 text-center leading-tight sm:grid">
            {LEVEL_ORDER.map((item) => (
              <span key={item}>{LEVEL_META[item].label}</span>
            ))}
          </div>
          <div className="mt-1 flex justify-between sm:hidden">
            <span>Gần như không có</span>
            <span>Bình thường</span>
            <span>Xuất sắc</span>
          </div>
        </div>
      </section>

      <section className="min-h-0 overflow-y-auto p-5 sm:p-7">
        <Eyebrow className="!text-[12px]">Tổng quan</Eyebrow>
        <p className="mt-2 font-serif text-[16px] leading-[1.7] text-[var(--color-ink-2)]">
          {assessment.overview}
        </p>

        <div className="my-6 border-t border-[rgba(26,22,17,0.14)]" />

        <div className="flex items-start justify-between gap-4">
          <div>
            <Eyebrow className="!text-[11px]">Cánh đang chọn</Eyebrow>
            <h3 className="mt-1 font-serif text-[25px] leading-tight text-[var(--color-ink)]">
              {selectedMeta.label}
            </h3>
          </div>
          <span
            className="shrink-0 border px-2.5 py-1 text-[11px] font-medium uppercase tracking-[0.8px]"
            style={{
              color: LEVEL_META[level].color,
              borderColor: LEVEL_META[level].color,
              background: `${LEVEL_META[level].color}10`,
            }}
          >
            {LEVEL_META[level].label}
          </span>
        </div>
        <p className="mt-2 text-[12px] leading-[1.6] text-[var(--color-ink-3)]">
          {selectedMeta.description}
        </p>

        {explanation ? (
          <div className="mt-4 space-y-3 text-[13px] leading-[1.65] text-[var(--color-ink-2)]">
            <p className="font-medium text-[var(--color-ink)]">{explanation.summary}</p>
            <p>{explanation.reasoning}</p>
            {explanation.tradeoff && (
              <div className="border-l-2 border-[var(--color-gold)] pl-3">
                <span className="font-medium text-[var(--color-ink)]">Mặt cần cân bằng: </span>
                {explanation.tradeoff}
              </div>
            )}
            {explanation.potential && (
              <div className="border-l-2 border-[var(--color-jade)] pl-3">
                <span className="font-medium text-[var(--color-ink)]">Hướng phát triển: </span>
                {explanation.potential}
              </div>
            )}
          </div>
        ) : (
          <p className="mt-4 border-l-2 border-[var(--color-paper-3)] pl-3 text-[12px] italic leading-[1.6] text-[var(--color-ink-3)]">
            Dimension này không được chọn làm nét nổi bật riêng trong lần đánh giá.
          </p>
        )}

        {orderedNotable.length > 0 && (
          <div className="mt-7">
            <Eyebrow className="!text-[11px]">Các nét đáng chú ý</Eyebrow>
            <div className="mt-2 flex flex-wrap gap-1.5">
              {orderedNotable.map((item) => {
                const meta = DIMENSIONS.find((dimension) => dimension.id === item.dimension);
                return (
                  <button
                    key={item.dimension}
                    type="button"
                    onClick={() => setSelected(item.dimension)}
                    className={`cursor-pointer rounded-full border px-3 py-1.5 text-[11px] transition-colors ${
                      selected === item.dimension
                        ? "border-[var(--color-crimson)] bg-[var(--color-crimson)] text-[var(--color-paper)]"
                        : "border-[rgba(26,22,17,0.18)] bg-transparent text-[var(--color-ink-2)] hover:border-[var(--color-crimson)]"
                    }`}
                  >
                    {meta?.label ?? item.dimension}
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </section>
    </div>
  );
}

export function StrengthWeaknessPanel({ ownerId, sessionId, onClose }: StrengthWeaknessPanelProps) {
  const assessment = useStrengthWeaknessAssessment(ownerId, sessionId);

  return (
    <div className="fixed inset-0 z-[70] flex items-center justify-center bg-[rgba(26,22,17,0.56)] p-0 backdrop-blur-[2px] sm:p-5">
      <button type="button" className="absolute inset-0 cursor-default" onClick={onClose} aria-label="Đóng bảng năng lực" />
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="strength-weakness-title"
        className="anim-modal-scale relative z-10 flex h-full w-full flex-col overflow-hidden border-[var(--color-ink)] bg-[var(--color-paper)] shadow-2xl sm:h-[min(900px,94vh)] sm:max-w-[1180px] sm:border"
      >
        <header className="flex items-start justify-between gap-5 border-b border-[rgba(26,22,17,0.14)] px-5 py-4 sm:px-7">
          <div>
            <Eyebrow className="!text-[11px] sm:!text-[12px]">Hoa thị năng lực</Eyebrow>
            <h2 id="strength-weakness-title" className="mt-0.5 font-serif text-[24px] leading-tight sm:text-[31px]">
              Điểm mạnh <span className="italic text-[var(--color-crimson)]">·</span> điểm yếu
            </h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="cursor-pointer border-0 bg-transparent p-1 text-[19px] text-[var(--color-ink-3)] hover:text-[var(--color-crimson)]"
            aria-label="Đóng"
          >
            ✕
          </button>
        </header>

        {!ownerId || !sessionId ? (
          <div className="grid flex-1 place-items-center p-8 text-center">
            <div>
              <div className="font-serif text-[22px] text-[var(--color-crimson)]">Chưa có hồ sơ lá số</div>
              <p className="mt-2 text-[13px] text-[var(--color-ink-3)]">Hãy mở lại lá số để tạo bản đánh giá năng lực.</p>
            </div>
          </div>
        ) : assessment.isPending ? (
          <div className="grid flex-1 place-items-center p-8 text-center">
            <div>
              <div className="mx-auto mb-5 h-20 w-20 animate-spin rounded-full border border-dashed border-[var(--color-crimson)] grid place-items-center">
                <span className="font-serif italic text-[22px] text-[var(--color-crimson)]">11</span>
              </div>
              <div className="font-serif text-[20px]">Đang dựng hoa thị năng lực…</div>
              <p className="mt-1 text-[12px] text-[var(--color-ink-3)]">Luận Mệnh, Thân, bộ chính tinh, phụ tinh và Tứ Hóa cho 11 dimension.</p>
            </div>
          </div>
        ) : assessment.isError ? (
          <div className="grid flex-1 place-items-center p-8 text-center">
            <div className="max-w-md">
              <div className="font-serif text-[22px] text-[var(--color-crimson)]">Chưa dựng được hoa thị</div>
              <p className="mt-2 text-[13px] text-[var(--color-ink-3)]">
                {assessment.error instanceof Error ? assessment.error.message : "Có lỗi không xác định."}
              </p>
              <Btn variant="crimson" className="mt-5" onClick={() => void assessment.refetch()}>
                Thử lại
              </Btn>
            </div>
          </div>
        ) : assessment.data ? (
          <AssessmentContent assessment={assessment.data} />
        ) : null}
      </div>
    </div>
  );
}
