import type { ButtonHTMLAttributes, ReactNode } from "react";

type BtnVariant = "default" | "primary" | "crimson" | "ghost";
type ChipVariant = "default" | "active" | "crimson";

interface BtnProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: BtnVariant;
  children: ReactNode;
}

const btnBase =
  "inline-flex items-center gap-2 text-[13px] px-4 py-2 cursor-pointer transition-all duration-150 tracking-[0.2px] font-sans disabled:opacity-50 disabled:cursor-not-allowed";

const btnVariants: Record<BtnVariant, string> = {
  default: "bg-[var(--color-paper)] text-[var(--color-ink)] border border-[rgba(26,22,17,0.32)] hover:bg-[var(--color-paper-2)]",
  primary: "bg-[var(--color-ink)] text-[var(--color-paper)] border border-[var(--color-ink)] hover:bg-[#2a241c]",
  crimson: "bg-[var(--color-crimson)] text-[#f9efe0] border border-[var(--color-crimson)] hover:bg-[#6d1f17]",
  ghost:   "bg-transparent text-[var(--color-ink-2)] border-0 hover:text-[var(--color-crimson)] hover:bg-[rgba(139,42,31,0.06)]",
};

export function Btn({ variant = "default", className = "", children, ...rest }: BtnProps) {
  return (
    <button {...rest} className={`${btnBase} ${btnVariants[variant]} ${className}`}>
      {children}
    </button>
  );
}

interface ChipProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ChipVariant;
  children: ReactNode;
}

const chipBase =
  "inline-flex items-center gap-1.5 whitespace-nowrap rounded-full text-[12.5px] px-3 py-1.5 cursor-pointer transition-all duration-150 font-sans tracking-[0.1px]";

const chipVariants: Record<ChipVariant, string> = {
  default: "bg-[rgba(255,252,245,0.6)] text-[var(--color-ink)] border border-[rgba(26,22,17,0.14)] hover:bg-[rgba(255,252,245,1)] hover:border-[var(--color-ink-3)]",
  active:  "bg-[var(--color-ink)] text-[var(--color-paper)] border border-[var(--color-ink)]",
  crimson: "bg-[var(--color-crimson)] text-[#f9efe0] border border-[var(--color-crimson)]",
};

export function Chip({ variant = "default", className = "", children, ...rest }: ChipProps) {
  return (
    <button {...rest} className={`${chipBase} ${chipVariants[variant]} ${className}`}>
      {children}
    </button>
  );
}
