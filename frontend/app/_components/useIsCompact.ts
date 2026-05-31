"use client";
import { useEffect, useState } from "react";

export function useIsCompact(): boolean {
  const [isCompact, setIsCompact] = useState(false);
  useEffect(() => {
    const mq = window.matchMedia("(max-width: 1775px)");
    function update() {
      setIsCompact(mq.matches);
    }
    update();
    mq.addEventListener("change", update);
    return () => mq.removeEventListener("change", update);
  }, []);
  return isCompact;
}
