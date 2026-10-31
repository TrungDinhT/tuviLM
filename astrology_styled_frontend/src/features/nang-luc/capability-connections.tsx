"use client";

import { useEffect, useState, type RefObject } from "react";
import styles from "./nang-luc.module.css";

type Point = { x: number; y: number };
type Connection = { id: string; start: Point; end: Point; path: string };

/** Measure the rendered circles, including changes caused by wrapping labels. */
export function CapabilityConnections({
  containerRef,
  findingsKey,
}: {
  containerRef: RefObject<HTMLDivElement | null>;
  findingsKey: string;
}) {
  const [drawing, setDrawing] = useState({ width: 0, height: 0, connections: [] as Connection[] });

  useEffect(() => {
    const container = containerRef.current;
    const center = container?.querySelector<HTMLElement>("[data-capability-center]");
    if (!container || !center) return;
    const targets = Array.from(container.querySelectorAll<HTMLElement>("[data-capability-anchor]"));
    let frame = 0;
    let disposed = false;
    const measure = () => {
      const bounds = container.getBoundingClientRect();
      const source = center.getBoundingClientRect();
      if (!bounds.width || !bounds.height || !source.width) return;
      const origin = {
        x: source.left + source.width / 2 - bounds.left,
        y: source.top + source.height / 2 - bounds.top,
      };
      const connections = targets.flatMap((target) => {
        const rect = target.getBoundingClientRect();
        const destination = {
          x: rect.left + rect.width / 2 - bounds.left,
          y: rect.top + rect.height / 2 - bounds.top,
        };
        const dx = destination.x - origin.x;
        const dy = destination.y - origin.y;
        const distance = Math.hypot(dx, dy);
        const sourceRadius = source.width / 2;
        const targetRadius = rect.width / 2;
        if (!rect.width || distance <= sourceRadius + targetRadius) return [];
        const ux = dx / distance;
        const uy = dy / distance;
        const start = { x: origin.x + ux * sourceRadius, y: origin.y + uy * sourceRadius };
        const end = { x: destination.x - ux * targetRadius, y: destination.y - uy * targetRadius };
        const span = distance - sourceRadius - targetRadius;
        const bend = span * 0.14;
        const c1 = {
          x: start.x + (ux * span) / 3 - uy * bend,
          y: start.y + (uy * span) / 3 + ux * bend,
        };
        const c2 = { x: end.x - (ux * span) / 3, y: end.y - (uy * span) / 3 };
        return [
          {
            id: target.dataset.capabilityAnchor ?? "",
            start,
            end,
            path: `M ${start.x} ${start.y} C ${c1.x} ${c1.y} ${c2.x} ${c2.y} ${end.x} ${end.y}`,
          },
        ];
      });
      setDrawing({ width: bounds.width, height: bounds.height, connections });
    };
    const schedule = () => {
      if (disposed) return;
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(measure);
    };
    const observer = new ResizeObserver(schedule);
    [
      container,
      center,
      ...targets,
      ...targets.flatMap((target) => (target.parentElement ? [target.parentElement] : [])),
    ].forEach((element) => observer.observe(element));
    window.addEventListener("resize", schedule);
    void document.fonts?.ready.then(schedule);
    schedule();
    return () => {
      disposed = true;
      cancelAnimationFrame(frame);
      observer.disconnect();
      window.removeEventListener("resize", schedule);
    };
  }, [containerRef, findingsKey]);

  return (
    <svg
      className={styles.connections}
      viewBox={`0 0 ${drawing.width || 1} ${drawing.height || 1}`}
      aria-hidden="true"
      fill="none"
    >
      {drawing.connections.map(({ id, start, end, path }) => (
        <g key={id} data-connection-for={id}>
          <path d={path} vectorEffect="non-scaling-stroke" />
          <circle cx={start.x} cy={start.y} r="2.5" />
          <circle cx={end.x} cy={end.y} r="2.5" />
        </g>
      ))}
    </svg>
  );
}
