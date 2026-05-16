"use client";
import { useEffect, useState } from "react";

const PADDING_BUFFER = 32; // outer padding allowance on mobile

function pickSize(width: number): number {
  if (width >= 1280) return 690;
  if (width >= 1024) return 580;
  if (width >= 768) return 520;
  // mobile: fit viewport, minimum 320, leave room for padding
  return Math.max(320, Math.min(420, width - PADDING_BUFFER));
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
