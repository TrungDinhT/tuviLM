"use client";

import { CONSTELLATION_SCATTER } from "@/components/shared/constellation-art";
import constelStyles from "@/components/shared/constellation-art.module.css";
import { destinyFor } from "@/content/destiny";
import { GOD_GHOSTS } from "@/content/god-ghosts";
import { GOD_LANDMARK_CONSTELLATIONS } from "@/content/god-landmark-constellations";
import { GOD_SILHOUETTES } from "@/content/god-silhouettes";
import { GodConstellationArt } from "@/features/an-sao/constellation-reward";
import type { BuildLasoResponse } from "@/lib/api/schemas";
import { starKeyFromName } from "@/lib/theme";

import deckStyles from "./deck.module.css";
import cardStyles from "./destiny-card.module.css";
import { displayStarName, menhChinhTinh, menhStarKey } from "./selectors";

/**
 * Lá Bài Bản Mệnh — the deck's main card.
 *
 * Everything on it resolves from the chính tinh of cung Mệnh through the
 * destiny table: archetype chip, mantra, and its guardian deity portrait.
 * Vô chính diệu gets its authored reading and the scattered sky — a reading
 * in its own right, never an empty stage.
 */
export function DestinyCard({ chart }: { chart: BuildLasoResponse }) {
  const names = menhChinhTinh(chart);
  const keys = names.map(starKeyFromName);
  const entry = destinyFor(menhStarKey(chart));
  const songTinh = names.length === 2;
  const label = names.map(displayStarName).join(" · ");
  const guardians = keys.flatMap((key) => {
    const src = GOD_GHOSTS[key];
    const constellation = GOD_LANDMARK_CONSTELLATIONS[key];
    const silhouette = GOD_SILHOUETTES[key];
    return src === undefined || constellation === undefined || silhouette === undefined
      ? []
      : [{ key, src, constellation, silhouette }];
  });
  const hasGuardians = keys.length > 0 && guardians.length === keys.length;

  return (
    <article
      data-testid="destiny-card"
      className={`${cardStyles.destiny} ${cardStyles.reveal} relative flex aspect-[9/16] min-h-0 min-w-0 flex-[1_1_auto] flex-col overflow-hidden rounded-[22px] px-6 pt-[26px] pb-6 md:pt-[28px]`}
    >
      <div className={deckStyles.cardBack} aria-hidden="true">
        <span className={deckStyles.cardBackSigil}>✦</span>
      </div>
      <div className={deckStyles.cardFace}>
        <div className="font-display text-base font-semibold tracking-[0.06em] md:text-[20px]">
          TỬ VI CÁ NHÂN
        </div>
        <div className="mt-[5px] text-xs text-muted md:text-[14px]">
          {names.length > 0 ? (
            <>
              Chính tinh chiếu mệnh: <b className="font-semibold text-ink">{label}</b>
              {songTinh ? " · sao đôi" : ""}
            </>
          ) : (
            <>
              Mệnh <b className="font-semibold text-ink">vô chính diệu</b> — cả bầu trời soi chiếu
            </>
          )}
        </div>
        <div
          data-testid="destiny-chip"
          className="mt-[14px] inline-flex items-center gap-2 self-start rounded-full border bg-[rgba(255,255,255,0.05)] px-[14px] py-[7px] text-[12.5px] font-semibold text-ink [border-color:color-mix(in_srgb,var(--accent)_52%,transparent)]"
        >
          <i className="not-italic text-accent">✦</i> {entry.archetype}
        </div>
        <div
          data-testid="destiny-guardian-stage"
          className={`${constelStyles.constelLit} ${cardStyles.guardianStage} ${songTinh ? cardStyles.guardianStageDouble : ""} min-h-0 flex-[1_1_auto]`}
          aria-hidden="true"
        >
          {hasGuardians ? (
            guardians.map(({ key, src, constellation, silhouette }, index) => (
              <div
                key={key}
                data-testid="destiny-guardian"
                className={cardStyles.guardianPortrait}
                style={{ animationDelay: `${index * 110}ms` }}
              >
                <div
                  data-testid="destiny-guardian-ghost"
                  className={cardStyles.guardianGhost}
                  style={{ backgroundImage: `url(${src})` }}
                />
                <GodConstellationArt
                  shape={constellation}
                  silhouette={silhouette}
                  renderSilhouette={false}
                  label={`Chòm sao ${names[index] ?? "chính tinh"} trong hình tượng ${silhouette.deity}`}
                  pointScale={songTinh ? 0.9 : 0.82}
                />
              </div>
            ))
          ) : (
            <svg
              viewBox="0 0 320 220"
              preserveAspectRatio="xMidYMid meet"
              className="h-full w-full"
            >
              {/* The scattered sky — the authored vô chính diệu treatment. */}
              {CONSTELLATION_SCATTER.map(([cx, cy], index) => (
                <circle
                  key={index}
                  className={constelStyles.constelNode}
                  cx={cx}
                  cy={cy * 2.2}
                  r="2.4"
                />
              ))}
            </svg>
          )}
        </div>
        <div
          data-testid="destiny-mantra"
          className="border-t pt-[14px] font-display text-[15px] leading-[1.42] italic [border-top-color:color-mix(in_srgb,var(--accent)_22%,transparent)] md:text-[17px]"
        >
          {entry.mantra}
        </div>
      </div>
    </article>
  );
}
