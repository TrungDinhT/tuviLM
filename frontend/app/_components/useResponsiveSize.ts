"use client";
import { useEffect, useState } from "react";

const PADDING_BUFFER = 48; // outer padding allowance on mobile

function pickSize(width: number): number {
  if (width >= 1280) return 690;
  if (width >= 1024) return 560;
  if (width >= 768) return 500;
  // mobile: fit viewport, minimum 300, leave room for padding
  return Math.max(300, Math.min(420, width - PADDING_BUFFER));
}

export function useResponsiveSize(): number {
  const [size, setSize] = useState<number>(690);
  useEffect(() => {
    function update() {
      setSize(pickSize(window.innerWidth));
    }
    update();
    window.addEventListener("resize", update);
    return () => window.removeEventListener("resize", update);
  }, []);
  return size;
}
