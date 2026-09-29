"use client";

import Link from "next/link";
import { useState } from "react";

import { Dialog, DialogClose } from "@/components/primitives/dialog";
import { GOD_GHOSTS } from "@/content/god-ghosts";
import { displayStarName, menhChinhTinh } from "@/features/ban-menh/selectors";
import { useLasoChart } from "@/lib/api/hooks";
import type { BuildLasoResponse, Cung } from "@/lib/api/schemas";
import { nguHanhOf, starKeyFromName } from "@/lib/theme";
import { useChartStore } from "@/store/chart-store";

import styles from "./la-so.module.css";

// Traditional địa bàn, clockwise from the upper left. Position, not role,
// determines placement: the roles move when a different chart is cast.
const POSITIONS = [
  ["Tị", 1, 1],
  ["Ngọ", 1, 2],
  ["Mùi", 1, 3],
  ["Thân", 1, 4],
  ["Dậu", 2, 4],
  ["Tuất", 3, 4],
  ["Hợi", 4, 4],
  ["Tý", 4, 3],
  ["Sửu", 4, 2],
  ["Dần", 4, 1],
  ["Mão", 3, 1],
  ["Thìn", 2, 1],
] as const;

const ELEMENT_COLORS: Record<string, string> = {
  Kim: "var(--element-kim)",
  Mộc: "var(--element-moc)",
  Thủy: "var(--element-thuy)",
  Hỏa: "var(--element-hoa)",
  Thổ: "var(--element-tho)",
};

// Lục sát / lục cát plus the twelve stars in THAI_TUE_RING_STAR_IDS
// (src/agent/tool/thai_tue/vong_thai_tue.py). Preserve accents to distinguish
// Quan Phù in this cycle from Quan Phủ.
const PREVIEW_STAR_NAMES = new Set([
  "Kình Dương",
  "Đà La",
  "Địa Không",
  "Địa Kiếp",
  "Linh Tinh",
  "Hỏa Tinh",
  "Tả Phù",
  "Hữu Bật",
  "Thiên Khôi",
  "Thiên Việt",
  "Văn Xương",
  "Văn Khúc",
  "Thái Tuế",
  "Thiếu Dương",
  "Tang Môn",
  "Thiếu Âm",
  "Quan Phù",
  "Tử Phù",
  "Tuế Phá",
  "Long Đức",
  "Bạch Hổ",
  "Phúc Đức",
  "Điếu Khách",
  "Trực Phù",
]);

// The API supplies tứ hóa as names only. Elements follow the backend catalog:
// src/refactored/components/data/tuhoa.json.
const TU_HOA_ELEMENTS: Record<string, string> = {
  hoaloc: "Thổ",
  hoaquyen: "Mộc",
  hoakhoa: "Thủy",
  hoaky: "Thủy",
};

function elementColor(element?: string) {
  return (element && ELEMENT_COLORS[element]) || "var(--color-ink)";
}

function secondaryStarColor(star: { name: string; element?: string }) {
  return elementColor(star.element ?? TU_HOA_ELEMENTS[starKeyFromName(star.name)]);
}

function primaryStarColor(name: string) {
  const element = nguHanhOf(starKeyFromName(name));
  return element ? `var(--element-${element})` : "var(--color-ink)";
}

function ageRange(cung: Cung) {
  return cung.age_daivan === null ? null : `${cung.age_daivan}–${cung.age_daivan + 9}`;
}

function markers(cung: Cung) {
  return [cung.is_cung_than && "Cung Thân", cung.is_tuan && "Tuần", cung.is_triet && "Triệt"]
    .filter(Boolean)
    .join(" · ");
}

export function LaSoScreen() {
  const { data: chart } = useLasoChart();
  if (!chart) return null;
  // Changing charts also clears any open palace detail.
  return <LaSoBoard key={chart.id} chart={chart} />;
}

export function LaSoBoard({ chart }: { chart: BuildLasoResponse }) {
  const [selectedPosition, setSelectedPosition] = useState<string | null>(null);
  const birth = useChartStore((state) => state.birthInfo);
  const cungList = Object.values(chart.cung_by_position);
  const selected = cungList.find((cung) => cung.position === selectedPosition);
  const than = cungList.find((cung) => cung.is_cung_than);
  const guardians = menhChinhTinh(chart).flatMap((name) => {
    const key = starKeyFromName(name);
    const src = GOD_GHOSTS[key];
    return src ? [{ key, src }] : [];
  });

  return (
    <section className={styles.screen} aria-label="Lá số đầy đủ">
      <div className={styles.toolbar}>
        <Link href="/ban-menh" className={styles.back}>
          ← Bản mệnh
        </Link>
        <span>Chạm từng cung để xem chi tiết</span>
      </div>
      <p className={styles.summary}>{chart.summary}</p>
      <div className={styles.board} aria-label="12 cung lá số">
        {POSITIONS.map(([position, row, column]) => {
          const cung = cungList.find(
            (item) => item.position === position || (position === "Tị" && item.position === "Tỵ"),
          );
          if (!cung) return null;
          const age = ageRange(cung);
          const previewStars = [
            ...cung.tuhoa.map((name) => ({
              name,
              element: TU_HOA_ELEMENTS[starKeyFromName(name)],
            })),
            ...cung.phu_tinh.filter((star) =>
              PREVIEW_STAR_NAMES.has(displayStarName(star.name).normalize("NFC")),
            ),
          ].slice(0, 2);
          const hiddenStarCount = cung.phu_tinh.length + cung.tuhoa.length - previewStars.length;
          return (
            <button
              type="button"
              key={position}
              className={styles.cell}
              style={{ gridRow: row, gridColumn: column }}
              onClick={() => setSelectedPosition(cung.position)}
              aria-label={`Xem cung ${cung.role ?? cung.position} tại ${cung.position}`}
              aria-haspopup="dialog"
            >
              <span className={styles.cellHeader}>
                <strong>{cung.role ?? "Cung"}</strong>
                <span>{cung.position}</span>
              </span>
              <span className={styles.primaryStars}>
                {cung.chinh_tinh.length ? (
                  cung.chinh_tinh.map((star) => (
                    <span key={star} style={{ color: primaryStarColor(star) }}>
                      {displayStarName(star)}
                    </span>
                  ))
                ) : (
                  <em>Vô chính diệu</em>
                )}
              </span>
              <span className={styles.secondaryStars}>
                <span className={styles.secondaryNames}>
                  {previewStars.map((star) => (
                    <span key={star.name} style={{ color: secondaryStarColor(star) }}>
                      {star.name}
                    </span>
                  ))}
                </span>
                {hiddenStarCount > 0 ? (
                  <span className={styles.hiddenCount}>+{hiddenStarCount}</span>
                ) : null}
              </span>
              <span className={styles.markers}>{markers(cung)}</span>
              <span className={styles.cellFooter}>
                <span>{cung.trang_sinh}</span>
                <span>{age}</span>
              </span>
            </button>
          );
        })}
        <div className={styles.center}>
          {guardians.length > 0 ? (
            <div className={styles.guardians} aria-hidden="true">
              {guardians.map(({ key, src }) => (
                <span
                  key={key}
                  className={styles.guardian}
                  style={{ backgroundImage: `url("${src}")` }}
                />
              ))}
            </div>
          ) : null}
          <div className={styles.centerContent}>
            <span className={styles.spark} aria-hidden="true">
              ✦
            </span>
            <h2 style={{ color: elementColor(chart.cuc_name.trim().split(/\s+/)[0]) }}>
              {chart.cuc_name}
            </h2>
            <p style={{ color: elementColor(chart.ban_menh_ngu_hanh) }}>{chart.ban_menh_name}</p>
            {birth ? <p>{birth.gender === "M" ? "Nam" : "Nữ"}</p> : null}
            {than?.role ? <p className={styles.than}>Thân cư {than.role}</p> : null}
            <span className={styles.centerDivider} />
            <p>{chart.menh_cuc_relation_label}</p>
          </div>
        </div>
      </div>

      <Dialog
        open={selected !== undefined}
        onOpenChange={(open) => {
          if (!open) setSelectedPosition(null);
        }}
        title={`Cung ${selected?.role ?? selected?.position ?? ""}`}
        description={
          selected
            ? [
                selected.position,
                selected.trang_sinh,
                ageRange(selected) ? `Đại vận ${ageRange(selected)}` : null,
              ]
                .filter(Boolean)
                .join(" · ")
            : undefined
        }
      >
        <DialogClose className={styles.close} aria-label="Đóng chi tiết cung">
          ×
        </DialogClose>
        {selected ? (
          <div className={styles.details}>
            {markers(selected) ? <p className={styles.detailMarkers}>{markers(selected)}</p> : null}
            <StarSection
              title="Chính tinh"
              stars={selected.chinh_tinh.map((name) => ({ name }))}
              primary
            />
            <StarSection
              title="Phụ tinh"
              stars={selected.phu_tinh.map((star) => ({
                name: star.display || star.name,
                element: star.element,
              }))}
            />
            {selected.tuhoa.length ? (
              <StarSection title="Tứ hóa" stars={selected.tuhoa.map((name) => ({ name }))} />
            ) : null}
            {selected.saoLuu.length ? (
              <StarSection
                title="Sao lưu"
                stars={selected.saoLuu.map((star) => ({
                  name: star.display || star.name,
                  element: star.element,
                }))}
              />
            ) : null}
          </div>
        ) : null}
      </Dialog>
    </section>
  );
}

function StarSection({
  title,
  stars,
  primary = false,
}: {
  title: string;
  stars: { name: string; element?: string }[];
  primary?: boolean;
}) {
  return (
    <section className={styles.starSection}>
      <h3>{title}</h3>
      {stars.length ? (
        <ul className={primary ? styles.primaryList : styles.starList}>
          {stars.map((star, index) => (
            <li
              key={`${star.name}-${index}`}
              style={{ color: primary ? primaryStarColor(star.name) : secondaryStarColor(star) }}
            >
              <span className={styles.dot} style={{ background: "currentColor" }} />
              {star.name}
            </li>
          ))}
        </ul>
      ) : (
        <p className={styles.empty}>{primary ? "Vô chính diệu" : "Không có phụ tinh"}</p>
      )}
    </section>
  );
}
