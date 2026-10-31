"use client";

import { useEffect, useState } from "react";
import { CapabilityLoadingArt } from "./capability-loading-art";
import styles from "./capability-loading.module.css";

// An estimated display only: completion is controlled by the backend response.
const ESTIMATED_DURATION_MS = 50_000;

export function CapabilityLoading() {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const startedAt = Date.now();
    const timer = window.setInterval(() => {
      const next = Math.min(
        99,
        Math.floor(((Date.now() - startedAt) / ESTIMATED_DURATION_MS) * 99),
      );
      setProgress(next);
      if (next === 99) window.clearInterval(timer);
    }, 200);
    return () => window.clearInterval(timer);
  }, []);

  return (
    <div
      className={styles.loading}
      role="progressbar"
      aria-label="Tiến độ phân tích năng lực ước tính"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={progress}
      aria-valuetext={progress === 99 ? "99%, đang chờ kết quả phân tích" : `${progress}%`}
    >
      <CapabilityLoadingArt />
      <svg className={styles.ring} viewBox="0 0 100 100" fill="none" aria-hidden="true">
        <circle className={styles.track} cx="50" cy="50" r="47" />
        <circle
          className={styles.fill}
          cx="50"
          cy="50"
          r="47"
          pathLength="100"
          strokeDasharray="100"
          strokeDashoffset={100 - progress}
        />
      </svg>
      <span className={styles.percent} aria-hidden="true">
        {progress}%
      </span>
    </div>
  );
}
