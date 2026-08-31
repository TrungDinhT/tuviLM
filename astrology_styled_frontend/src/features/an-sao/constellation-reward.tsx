"use client";

import Image from "next/image";

import { CONSTELLATION_SCATTER } from "@/components/shared/constellation-art";
import styles from "@/components/shared/constellation-art.module.css";
import { GOD_CONSTELLATIONS, type GodConstellation } from "@/content/god-constellations";
import { GOD_PORTRAITS } from "@/content/god-portraits";
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

function GodConstellationArt({ shape, label }: { shape: GodConstellation; label: string }) {
  return (
    <svg
      role="img"
      aria-label={label}
      viewBox="0 0 100 100"
      preserveAspectRatio="xMidYMid meet"
      className={`${rewardStyles.vectorConstellation} absolute inset-0 h-full w-full overflow-visible`}
    >
      {shape.lines.map(([fromIndex, toIndex]) => {
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
          />
        );
      })}
      {shape.points.map(([cx, cy, pointPower], index) => {
        const power = pointPower ?? 1;
        return (
          <g key={index}>
            <circle className={rewardStyles.starHalo} cx={cx} cy={cy} r={2.7 * power} />
            <circle className={rewardStyles.starCore} cx={cx} cy={cy} r={0.72 * power} />
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
 * tinh maps to its god artwork through the content layer; song tinh show both
 * guardians side by side. Vô chính diệu and unknown stars retain the neutral
 * scattered-sky fallback.
 */
export function ConstellationReward({ stars, names }: ConstellationRewardProps) {
  const lit = stars !== null;
  const guardians =
    stars?.flatMap((key) => {
      const portrait = GOD_PORTRAITS[key];
      const constellation = GOD_CONSTELLATIONS[key];
      return portrait === undefined || constellation === undefined
        ? []
        : [{ key, portrait, constellation }];
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
          {guardians.map(({ key, portrait, constellation }, index) => (
            <div
              key={key}
              className={cn(
                rewardStyles.constellationFigure,
                "relative aspect-square",
                isSongTinh ? "w-[min(170px,44vw)]" : "w-[min(250px,78vw)]",
              )}
              style={{ animationDelay: `${index * 90}ms` }}
            >
              <Image
                src={portrait.src}
                alt=""
                fill
                loading="eager"
                unoptimized
                sizes={
                  isSongTinh ? "(max-width: 767px) 44vw, 170px" : "(max-width: 767px) 78vw, 250px"
                }
                className={rewardStyles.figureBackdrop}
              />
              <GodConstellationArt
                shape={constellation}
                label={`Chòm sao ${names[index] ?? "chính tinh"} trong hình tượng ${portrait.deity}`}
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
