"use client";

import { useLayoutEffect, useRef, type RefObject } from "react";

/** FLIP measured nodes rather than transitioning grid-template/auto heights. */
export function useFindingLayout(ref: RefObject<HTMLElement | null>, layoutKey: string) {
  const previous = useRef(
    new Map<string, { x: number; y: number; width: number; height: number }>(),
  );
  const previousHeight = useRef(0);
  useLayoutEffect(() => {
    const root = ref.current;
    if (!root) return;
    const bounds = root.getBoundingClientRect();
    const nodes = root.querySelectorAll<HTMLElement>("[data-layout-id]");
    const next = new Map<string, { x: number; y: number; width: number; height: number }>();
    const animations: Animation[] = [];
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    for (const node of nodes) {
      const id = node.dataset.layoutId!;
      const rect = node.getBoundingClientRect();
      const parent = node.parentElement?.closest<HTMLElement>("[data-layout-id]");
      const origin = parent?.getBoundingClientRect() ?? bounds;
      const to = {
        x: rect.left - origin.left,
        y: rect.top - origin.top,
        width: rect.width,
        height: rect.height,
      };
      next.set(id, to);
      if (reduced || !node.animate || !rect.width) continue;
      const from = previous.current.get(id);
      const base = getComputedStyle(node).transform;
      const transform = base === "none" ? "" : base;
      animations.push(
        node.animate(
          from
            ? [
                {
                  transformOrigin: "top left",
                  transform: `translate(${from.x - to.x}px, ${from.y - to.y}px) ${transform} scale(${from.width / to.width}, ${from.height / to.height})`,
                },
                { transform: base, transformOrigin: "top left" },
              ]
            : [
                { opacity: 0, transform: `translateY(12px) ${transform} scale(.94)` },
                { opacity: 1, transform: base },
              ],
          { duration: 420, easing: "cubic-bezier(.22, 1, .36, 1)" },
        ),
      );
    }
    if (
      !reduced &&
      root.animate &&
      previousHeight.current &&
      bounds.height !== previousHeight.current
    ) {
      animations.push(
        root.animate(
          [{ height: `${previousHeight.current}px` }, { height: `${bounds.height}px` }],
          { duration: 420, easing: "cubic-bezier(.22, 1, .36, 1)" },
        ),
      );
    }
    previous.current = next;
    previousHeight.current = bounds.height;
    // Another finding may arrive during this transition. Start its FLIP from
    // the last painted positions rather than snapping to the previous target.
    let frame = 0;
    const until = performance.now() + 420;
    const remember = () => {
      const rootBounds = root.getBoundingClientRect();
      for (const node of nodes) {
        const rect = node.getBoundingClientRect();
        const parent = node.parentElement?.closest<HTMLElement>("[data-layout-id]");
        const origin = parent?.getBoundingClientRect() ?? rootBounds;
        previous.current.set(node.dataset.layoutId!, {
          x: rect.left - origin.left,
          y: rect.top - origin.top,
          width: rect.width,
          height: rect.height,
        });
      }
      previousHeight.current = rootBounds.height;
      if (performance.now() < until) frame = requestAnimationFrame(remember);
    };
    if (animations.length) frame = requestAnimationFrame(remember);
    return () => {
      cancelAnimationFrame(frame);
      animations.forEach((animation) => animation.cancel());
    };
  }, [ref, layoutKey]);
}
