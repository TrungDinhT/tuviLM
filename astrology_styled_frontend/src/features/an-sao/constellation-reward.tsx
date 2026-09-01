"use client";

import { CONSTELLATION_SCATTER } from "@/components/shared/constellation-art";
import styles from "@/components/shared/constellation-art.module.css";
import type { GodConstellation } from "@/content/god-constellations";
import { GOD_GHOSTS } from "@/content/god-ghosts";
import { GOD_LANDMARK_CONSTELLATIONS } from "@/content/god-landmark-constellations";
import { GOD_SILHOUETTES, type GodSilhouette } from "@/content/god-silhouettes";
import { cn } from "@/lib/utils";

import rewardStyles from "./constellation-reward.module.css";

interface ConstellationRewardProps {
  /**
   * Star keys of the previewed cung Mệnh, or null while no preview has
   * resolved — the sleeping state.
   */
  stars: readonly string[] | null;
  /** Backend display names, for the caption ("Thái Dương · …"). */
  names: readonly string[];
}

export function GodConstellationArt({
  shape,
  silhouette,
  renderSilhouette,
  label,
  pointScale = 1,
}: {
  shape: GodConstellation;
  silhouette: GodSilhouette;
  renderSilhouette: boolean;
  label: string;
  pointScale?: number;
}) {
  return (
    <svg
      role="img"
      aria-label={label}
      viewBox="0 0 100 100"
      preserveAspectRatio="xMidYMid meet"
      className={`${rewardStyles.vectorConstellation} absolute inset-0 h-full w-full overflow-visible`}
    >
      {renderSilhouette ? (
        <>
          <ellipse className={rewardStyles.godAura} cx="50" cy="53" rx="35" ry="43" />
          {silhouette.fillPaths.map((path, index) => (
            <path key={`fill-${index}`} className={rewardStyles.godFill} d={path} />
          ))}
          {silhouette.detailPaths.map((path, index) => (
            <path key={`detail-${index}`} className={rewardStyles.godDetail} d={path} />
          ))}
          {silhouette.symbolPaths.map((path, index) => (
            <path key={`symbol-${index}`} className={rewardStyles.godSymbol} d={path} />
          ))}
        </>
      ) : null}
      {shape.lines.map(([fromIndex, toIndex], lineIndex) => {
        const from = shape.points[fromIndex];
        const to = shape.points[toIndex];
        if (from === undefined || to === undefined) return null;
        return (
          <line
            key={`${fromIndex}-${toIndex}`}
            className={rewardStyles.starLine}
            x1={from[0]}
            y1={from[1]}
            x2={to[0]}
            y2={to[1]}
            pathLength="1"
            style={{ animationDelay: `${180 + lineIndex * 50}ms` }}
          />
        );
      })}
      {shape.points.map(([cx, cy, pointPower], index) => {
        const power = pointPower ?? 1;
        return (
          <g
            key={index}
            className={rewardStyles.starNode}
            style={{ animationDelay: `${110 + index * 45}ms` }}
          >
            <circle
              className={rewardStyles.starHalo}
              cx={cx}
              cy={cy}
              r={2.7 * power * pointScale}
            />
            <circle
              className={rewardStyles.starCore}
              cx={cx}
              cy={cy}
              r={0.72 * power * pointScale}
            />
          </g>
        );
      })}
    </svg>
  );
}

/**
 * The guardian portrait that wakes as the birth data completes.
 *
 * Fed by the preview endpoint — never by birth-date arithmetic. Each chính
 * tinh maps to a tiny ghost backdrop with an anatomy-following SVG constellation;
 * song tinh show both guardians side by side. Vô chính diệu and unknown stars
 * retain the neutral scattered-sky fallback.
 */
export function ConstellationReward({ stars, names }: ConstellationRewardProps) {
  const lit = stars !== null;
  const guardians =
    stars?.flatMap((key) => {
      const silhouette = GOD_SILHOUETTES[key];
      const constellation = GOD_LANDMARK_CONSTELLATIONS[key];
      return silhouette === undefined || constellation === undefined
        ? []
        : [{ key, silhouette, constellation, ghostSrc: GOD_GHOSTS[key] }];
    }) ?? [];
  const hasGuardians = lit && stars.length > 0 && guardians.length === stars.length;
  const isSongTinh = guardians.length > 1;

  const caption = !lit
    ? "CHÒM SAO MỆNH ĐANG NGỦ"
    : stars.length === 0
      ? "MỆNH VÔ CHÍNH DIỆU · TRỜI RỘNG MỞ"
      : `CHÒM SAO ${names.join(" · ").toUpperCase()} ĐÃ THỨC`;

  return (
    <div
      className={cn(
        "relative mt-[6px] mb-[2px]",
        hasGuardians
          ? isSongTinh
            ? "h-[clamp(190px,58vw,220px)]"
            : "h-[clamp(230px,82vw,278px)]"
          : "h-[154px]",
        lit && styles.constelLit,
      )}
    >
      {hasGuardians ? (
        <div
          className={cn(
            "absolute inset-x-0 top-0 flex items-start justify-center",
            isSongTinh ? "h-[clamp(150px,44vw,172px)] gap-[2px]" : "h-[clamp(210px,78vw,252px)]",
          )}
        >
          {guardians.map(({ key, silhouette, constellation, ghostSrc }, index) => (
            <div
              key={key}
              className={cn(
                rewardStyles.constellationFigure,
                "relative aspect-square",
                isSongTinh ? "w-[min(170px,44vw)]" : "w-[min(250px,78vw)]",
              )}
              style={{ animationDelay: `${index * 90}ms` }}
            >
              {ghostSrc === undefined ? null : (
                <div
                  aria-hidden="true"
                  className={rewardStyles.ghostBackdrop}
                  style={{ backgroundImage: `url(${ghostSrc})` }}
                />
              )}
              <GodConstellationArt
                shape={constellation}
                silhouette={silhouette}
                renderSilhouette={ghostSrc === undefined}
                label={`Chòm sao ${names[index] ?? "chính tinh"} trong hình tượng ${silhouette.deity}`}
              />
            </div>
          ))}
        </div>
      ) : (
        <svg
          aria-hidden="true"
          viewBox="0 0 320 100"
          preserveAspectRatio="xMidYMid meet"
          className="absolute inset-0 h-[116px] w-full overflow-visible transition-opacity duration-[350ms]"
        >
          {CONSTELLATION_SCATTER.map(([cx, cy], index) => (
            <circle
              key={index}
              className={cn(
                styles.constelNode,
                lit && stars.length === 0 && styles.constelNodeNeutral,
              )}
              cx={cx}
              cy={cy}
              r="2.4"
            />
          ))}
        </svg>
      )}
      <div
        className={cn(
          "absolute right-0 bottom-[4px] left-0 z-2 px-[8px] text-center whitespace-normal text-muted",
          isSongTinh
            ? "text-[10px] leading-[1.45] tracking-[0.08em]"
            : "text-[12px] tracking-[0.2em]",
        )}
      >
        {caption}
      </div>
    </div>
  );
}
