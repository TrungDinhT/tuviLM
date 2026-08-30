"use client";

import { useEffect, useRef, useState } from "react";

/**
 * Stick-to-bottom for the document-scrolling chat.
 *
 * The page itself scrolls (there is no inner scroll container), so this tracks
 * the window: while the user is near the bottom, growing content auto-scrolls
 * to keep the latest message visible; once they scroll up it stays put, and a
 * jump-back button is exposed via `isAtBottom`.
 */
export function useStickToBottom(contentKey: string) {
  const [isAtBottom, setIsAtBottom] = useState(true);
  const stickRef = useRef(true);

  useEffect(() => {
    const onScroll = () => {
      const el = document.documentElement;
      const nearBottom = el.scrollHeight - (window.innerHeight + el.scrollTop) < 96;
      stickRef.current = nearBottom;
      setIsAtBottom((prev) => (prev === nearBottom ? prev : nearBottom));
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll, { passive: true });
    return () => {
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
    };
  }, []);

  useEffect(() => {
    if (stickRef.current) {
      window.scrollTo(0, document.documentElement.scrollHeight);
    }
  }, [contentKey]);

  return {
    isAtBottom,
    scrollToBottom: () => window.scrollTo(0, document.documentElement.scrollHeight),
  };
}
