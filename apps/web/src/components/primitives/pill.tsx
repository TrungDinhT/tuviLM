import { cn } from "@/lib/utils";

const BASE =
  "inline-flex cursor-pointer items-center justify-center gap-[9px] rounded-full border-0 " +
  "px-[26px] py-[15px] text-base font-semibold " +
  "transition-[transform,box-shadow] duration-200 ease-out active:scale-[0.97] " +
  "focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--accent-glow)] " +
  "disabled:pointer-events-none disabled:opacity-40";

const VARIANTS = {
  primary: "pill-primary",
  ghost: "pill-ghost",
} as const;

type PillVariant = keyof typeof VARIANTS;

/**
 * The design's one button shape.
 *
 * `primary` carries the runtime accent, so it re-tints itself whenever the
 * chart changes — which is why the gradient lives in a CSS utility reading
 * `--accent` rather than in a prop.
 */
export function Pill({
  variant = "primary",
  className,
  type = "button",
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: PillVariant }) {
  return <button type={type} className={cn(BASE, VARIANTS[variant], className)} {...props} />;
}
