import type { ReactNode, CSSProperties } from "react";

interface EyebrowProps {
  children: ReactNode;
  style?: CSSProperties;
  className?: string;
}

export function Eyebrow({ children, style, className = "" }: EyebrowProps) {
  return <div className={`eyebrow ${className}`} style={style}>{children}</div>;
}
