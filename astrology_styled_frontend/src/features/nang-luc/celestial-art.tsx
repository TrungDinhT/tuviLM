import styles from "./nang-luc.module.css";

export function CapabilityIcon({ kind = "spark" }: { kind?: string }) {
  const paths: Record<string, React.ReactNode> = {
    shield: (
      <>
        <path d="M24 5 40 11v13c0 10-9 16-16 19C17 40 8 34 8 24V11Z" />
        <path d="M24 14v20m-8-12 8 5 9-10" />
      </>
    ),
    target: (
      <>
        <circle cx="23" cy="26" r="16" />
        <circle cx="23" cy="26" r="10" />
        <path d="m23 26 17-18m-1-4 1 8 7 1" />
      </>
    ),
    bulb: (
      <>
        <path d="M18 34c0-8-7-8-7-17a13 13 0 0 1 26 0c0 9-7 9-7 17m-12 2h12m-11 5h10m-8 4h6M24 23v12m-5-15 5 4 5-4M4 18H1m46 0h-3M7 6 4 3m37 3 3-3" />
      </>
    ),
    balance: (
      <>
        <path d="M24 6v34m-9 3h18M9 14h30M12 14 4 30h16Zm24 0-8 16h16Z" />
        <circle cx="24" cy="9" r="3" />
      </>
    ),
    person: (
      <>
        <circle cx="24" cy="14" r="8" />
        <path d="M9 42v-5a15 15 0 0 1 30 0v5Zm27-19 5 5" />
      </>
    ),
    work: (
      <>
        <rect x="5" y="15" width="38" height="27" rx="5" />
        <path d="M16 15V9a3 3 0 0 1 3-3h10a3 3 0 0 1 3 3v6M5 26h15m8 0h15" />
        <rect x="20" y="22" width="8" height="9" rx="2" />
      </>
    ),
    chat: (
      <>
        <path d="M9 7h30a5 5 0 0 1 5 5v20a5 5 0 0 1-5 5H23L12 45v-8H9a5 5 0 0 1-5-5V12a5 5 0 0 1 5-5Z" />
        <circle cx="15" cy="22" r="1" />
        <circle cx="24" cy="22" r="1" />
        <circle cx="33" cy="22" r="1" />
      </>
    ),
    lock: (
      <>
        <rect x="10" y="21" width="28" height="22" rx="5" />
        <path d="M16 21V13a8 8 0 0 1 16 0v8m-8 10v4" />
      </>
    ),
    spark: <path d="m24 4 5 15 15 5-15 5-5 15-5-15-15-5 15-5Z" />,
  };
  return (
    <svg
      viewBox="0 0 48 48"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {paths[kind] ?? paths.spark}
    </svg>
  );
}

export function CelestialOrb() {
  return (
    <div className={styles.orbStage} aria-hidden="true">
      <svg className={styles.orbits} viewBox="0 0 500 500" fill="none">
        <circle cx="250" cy="250" r="210" />
        <circle cx="250" cy="250" r="150" />
        <path d="M4 16C155 30 77 160 193 185S425 399 495 327M11 356C120 281 176 421 313 357S299 103 492 38" />
        {[
          [4, 16],
          [114, 98],
          [157, 174],
          [193, 185],
          [379, 94],
          [446, 57],
          [313, 357],
          [407, 310],
          [463, 324],
          [49, 337],
          [116, 332],
          [286, 444],
        ].map(([cx, cy], i) => (
          <circle key={i} cx={cx} cy={cy} r={i % 3 === 0 ? 5 : 3} className={styles.orbitDot} />
        ))}
      </svg>
      <div className={styles.orb}>
        <div className={styles.orbMist} />
        <div className={styles.orbMistTwo} />
        <svg className={styles.wisps} viewBox="0 0 200 200" fill="none">
          <path d="M28 35C87-7 190 22 155 60S31 43 28 102 164 191 179 128" />
          <path d="M15 82C39 14 138 18 155 74S69 125 56 157 115 197 162 165" />
          <path d="M24 129C2 68 116 16 148 52S96 149 47 130 39 40 87 17" />
          <path d="M37 168C114 200 189 132 153 103S72 125 83 159 161 161 181 113" />
        </svg>
        <div className={styles.innerRing} />
        <svg className={styles.meditation} viewBox="0 0 100 120" fill="currentColor">
          <circle cx="50" cy="22" r="10" />
          <path d="M43 33c-13 3-11 20-17 32L10 78l5 5 21-12 5-12 1 20-21 16c-9 7-5 14 6 13l23-5 23 5c11 1 15-6 6-13L58 79l1-20 5 12 21 12 5-5-16-13c-6-12-4-29-17-32Z" />
        </svg>
      </div>
      <span className={styles.starOne}>✦</span>
      <span className={styles.starTwo}>✦</span>
      <span className={styles.starThree}>✦</span>
    </div>
  );
}
