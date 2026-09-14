"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useRef, useState } from "react";
import {
  Drawer,
  DrawerBody,
  DrawerClose,
  DrawerContent,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
} from "@/components/primitives/drawer";
import { useChartStore } from "@/store/chart-store";
import { showToast } from "@/lib/toast";
import { useIsHydrated } from "@/hooks/use-is-hydrated";
import { describe, isApiError } from "@/lib/http/errors";
import { CapabilityConnections } from "./capability-connections";
import { CapabilityIcon, CelestialOrb } from "./celestial-art";
import {
  capabilityKey,
  useCapabilityReport,
  useCapabilityStore,
  type CapabilityProfile,
} from "./data";
import styles from "./nang-luc.module.css";

export function CapabilityLauncher() {
  const birth = useChartStore((state) => state.birthInfo);
  const hasChart = useChartStore((state) => state.hasChart);
  const key = capabilityKey(birth);
  const unlocked = useCapabilityStore((state) => state.entries[key]?.unlocked);
  const router = useRouter();
  const hydrated = useIsHydrated();
  const available = hydrated && hasChart && birth !== null;
  return (
    <section className={styles.launcher} aria-labelledby="capability-title">
      <div className={styles.launcherContent}>
        <span className={styles.eyebrow}>CHIẾN LƯỢC THIÊN QUAN</span>
        <div className={styles.preview} aria-hidden="true">
          <CelestialOrb />
          {["shield", "target", "bulb", "balance", "chat", "work"].map((kind) => (
            <span key={kind} className={styles.floatingSkill}>
              <CapabilityIcon kind={kind} />
            </span>
          ))}
        </div>
        <h2 id="capability-title">Khám phá năng lực</h2>
        <p>
          Thấu hiểu điểm mạnh và những điều cần lưu ý<br />
          ẩn trong cấu trúc Mệnh của bạn.
        </p>
        {available ? (
          <button
            className={styles.unlockButton}
            onClick={() => {
              useCapabilityStore.getState().unlock(key);
              router.push("/nang-luc");
            }}
          >
            {unlocked ? "Xem phân tích" : "Trả phí để mở"}
            <span aria-hidden="true"> ↗</span>
          </button>
        ) : (
          <Link className={styles.unlockButton} href="/">
            Lập lá số để khám phá ↗
          </Link>
        )}
        {!unlocked && (
          <span className={styles.previewLabel}>Khám phá những năng lực ẩn trong lá số</span>
        )}
      </div>
    </section>
  );
}

export function NangLucScreen() {
  const birth = useChartStore((state) => state.birthInfo);
  const hasChart = useChartStore((state) => state.hasChart);
  const hydrated = useIsHydrated();
  const key = capabilityKey(birth);
  const unlocked = useCapabilityStore((state) => state.entries[key]?.unlocked) === true;
  const analysis = useCapabilityReport(birth, hydrated && hasChart && unlocked);
  if (!hydrated)
    return (
      <div className={styles.status} role="status">
        Đang mở hồ sơ năng lực…
      </div>
    );
  if (!hasChart || !birth || !unlocked)
    return (
      <div className={styles.gate}>
        <Link href="/thien-ban" className={styles.backLink}>
          ← Nâng cao
        </Link>
        <CapabilityLauncher />
      </div>
    );
  if (analysis.data) return <CapabilityReport key={key} report={analysis.data} />;
  return (
    <main className={styles.report}>
      <ReportHeader />
      <div className={styles.status}>
        <CelestialOrb />
        <h1>
          {analysis.isError ? "Chưa thể đọc năng lực của bạn" : "Đang khám phá cấu trúc Mệnh"}
        </h1>
        <p role={analysis.isError ? "alert" : "status"}>
          {analysis.isError
            ? isApiError(analysis.error)
              ? describe(analysis.error.error)
              : "Kết nối bị gián đoạn. Bạn có thể thử lại."
            : "Đang tổng hợp lá số và luận giải những năng lực nổi bật của bạn. Quá trình này có thể mất một chút thời gian."}
        </p>
        {analysis.isError && (
          <button className={styles.unlockButton} onClick={() => void analysis.refetch()}>
            Thử lại
          </button>
        )}
      </div>
    </main>
  );
}

function ReportHeader({ onShare }: { onShare?: () => void }) {
  return (
    <header className={styles.reportHeader}>
      <Link href="/thien-ban" className={styles.iconButton} aria-label="Quay lại Nâng cao">
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          aria-hidden="true"
        >
          <path d="m14 5-7 7 7 7" />
        </svg>
      </Link>
      <span>CHIẾN LƯỢC THIÊN QUAN</span>
      {onShare ? (
        <button className={styles.iconButton} onClick={onShare} aria-label="Chia sẻ phân tích">
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            aria-hidden="true"
          >
            <path d="M8 9H5v12h14V9h-3M12 15V2m-4 4 4-4 4 4" />
          </svg>
        </button>
      ) : (
        <span />
      )}
    </header>
  );
}

const strengthIcons: Record<string, string> = {
  tai_dinh_khung_van_de: "shield",
  xu_ly_khung_hoang: "target",
  dao_sau_van_de: "bulb",
  lap_luan_logic: "balance",
};
const weaknessIcons = { han_che_truc_tiep: "person", qua_da: "work", xung_dot: "chat" };

export function CapabilityReport({ report }: { report: CapabilityProfile }) {
  const constellationRef = useRef<HTMLDivElement>(null);
  const returnFocusRef = useRef<HTMLButtonElement>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selected, setSelected] = useState<{
    id: string;
    title: string;
    description: string;
    explanation?: string;
  } | null>(null);
  function openFinding(element: HTMLButtonElement, finding: NonNullable<typeof selected>) {
    returnFocusRef.current = element;
    setSelected(finding);
    setDrawerOpen(true);
  }
  async function share() {
    const text = [
      "Thấu hiểu cấu trúc Mệnh",
      report.tong_quan,
      "ĐIỂM MẠNH",
      ...report.diem_manh.map((item) => `${item.nang_luc}\n${item.mo_ta}`),
      "ĐIỂM CẦN LƯU Ý",
      ...report.diem_yeu.map((item) => `${item.ten}\n${item.mo_ta}`),
    ].join("\n\n");
    try {
      if (navigator.share) await navigator.share({ title: "Khám phá năng lực", text });
      else {
        await navigator.clipboard.writeText(text);
        showToast("Đã sao chép phân tích.");
      }
    } catch (error) {
      if (!(error instanceof DOMException && error.name === "AbortError"))
        showToast("Chưa thể chia sẻ. Vui lòng thử lại.");
    }
  }
  return (
    <main className={styles.report} data-detail-open={drawerOpen}>
      <ReportHeader onShare={() => void share()} />
      <h1 className="sr-only">Khám phá năng lực</h1>
      <section className={styles.strengthSection} aria-label="Điểm mạnh">
        <div className={styles.constellation} ref={constellationRef}>
          <CapabilityConnections
            containerRef={constellationRef}
            findingsKey={report.diem_manh.map((item) => item.nang_luc_id).join("|")}
          />
          <div
            className={styles.centralOrb}
            data-dimmed={drawerOpen && selected?.id !== "overview"}
          >
            <CelestialOrb decorativeTrails={false} />
            <button
              type="button"
              className={styles.overviewButton}
              data-capability-center
              aria-label="Thấu hiểu cấu trúc Mệnh"
              onClick={(event) =>
                openFinding(event.currentTarget, {
                  id: "overview",
                  title: "Thấu hiểu cấu trúc Mệnh",
                  description: report.tong_quan,
                })
              }
              aria-haspopup="dialog"
            ></button>
          </div>
          <div className={styles.strengthGrid}>
            {report.diem_manh.map((item) => (
              <button
                type="button"
                key={item.nang_luc_id}
                className={styles.strengthCard}
                data-dimmed={drawerOpen && selected?.id !== `strength:${item.nang_luc_id}`}
                data-selected={drawerOpen && selected?.id === `strength:${item.nang_luc_id}`}
                onClick={(event) =>
                  openFinding(event.currentTarget, {
                    id: `strength:${item.nang_luc_id}`,
                    title: item.nang_luc,
                    description: item.mo_ta,
                    explanation: item.giai_thich,
                  })
                }
                aria-label={`Xem luận giải: ${item.nang_luc}`}
                aria-haspopup="dialog"
              >
                <span className={styles.iconHalo} data-capability-anchor={item.nang_luc_id}>
                  <CapabilityIcon kind={strengthIcons[item.nang_luc_id] ?? "spark"} />
                </span>
                <span className={styles.findingTitle}>{item.nang_luc}</span>
              </button>
            ))}
          </div>
        </div>
        {!report.diem_manh.length && (
          <p className={styles.empty}>
            Chưa có đủ cơ sở để xác định điểm mạnh nổi bật trong lần phân tích này.
          </p>
        )}
      </section>
      <section className={styles.weaknessSection} aria-labelledby="weaknesses-title">
        <div className={styles.warningDivider}>
          <span aria-hidden="true">△</span>
        </div>
        <h2 id="weaknesses-title">ĐIỂM CẦN LƯU Ý</h2>
        <div className={styles.weaknessGrid}>
          {report.diem_yeu.map((item, index) => (
            <button
              type="button"
              key={`${item.ten}-${index}`}
              className={styles.weaknessCard}
              data-dimmed={drawerOpen && selected?.id !== `weakness:${index}`}
              data-selected={drawerOpen && selected?.id === `weakness:${index}`}
              onClick={(event) =>
                openFinding(event.currentTarget, {
                  id: `weakness:${index}`,
                  title: item.ten,
                  description: item.mo_ta,
                  explanation: item.giai_thich,
                })
              }
              aria-label={`Xem luận giải: ${item.ten}`}
              aria-haspopup="dialog"
            >
              <span className={styles.iconHalo}>
                <CapabilityIcon kind={weaknessIcons[item.loai]} />
              </span>
              <span className={styles.findingTitle}>{item.ten}</span>
            </button>
          ))}
        </div>
        {!report.diem_yeu.length && (
          <p className={styles.empty}>
            Chưa có đủ cơ sở để xác định điểm cần lưu ý trong lần phân tích này.
          </p>
        )}
      </section>
      <div className={styles.endingStar} aria-hidden="true">
        ✦
      </div>
      <Drawer
        open={drawerOpen}
        onOpenChange={setDrawerOpen}
        onOpenChangeComplete={(open) => {
          if (!open) setSelected(null);
        }}
      >
        <DrawerContent finalFocus={returnFocusRef}>
          <DrawerHeader>
            <DrawerTitle>{selected?.title}</DrawerTitle>
          </DrawerHeader>
          <DrawerBody>
            <div className={styles.explanation}>
              <span className={styles.eyebrow}>
                {selected?.explanation ? "MÔ TẢ NĂNG LỰC" : "TỔNG QUAN"}
              </span>
              <p>{selected?.description}</p>
              {selected?.explanation && (
                <>
                  <h3 className={styles.explanationHeading}>LUẬN GIẢI TỬ VI</h3>
                  <p>{selected.explanation}</p>
                </>
              )}
            </div>
          </DrawerBody>
          <DrawerFooter>
            <DrawerClose className={styles.closeButton}>Đóng luận giải</DrawerClose>
          </DrawerFooter>
        </DrawerContent>
      </Drawer>
    </main>
  );
}
