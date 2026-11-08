import type { GodConstellation } from "@/content/god-constellations";

export const CONSTELLATION_WAVE = {
  cycleMs: 4200,
  waveStartMs: 150,
  waveDurationMs: 2100,
  linkTravelMs: 1900,
} as const;

export const STAR_PULSE_CYCLE_MS = 4500;

function starPulseSeed(seed: string, index: number) {
  let hash = 2166136261;
  const value = `${seed}-${index}`;
  for (let character = 0; character < value.length; character++) {
    hash = Math.imul(hash ^ value.charCodeAt(character), 16777619);
  }
  return hash >>> 0;
}

/** Spread stars evenly through one pulse cycle, with a seeded random assignment. */
export function constellationStarPulsePhases(seed: string, count: number) {
  const order = Array.from({ length: count }, (_, index) => index).sort(
    (left, right) => starPulseSeed(seed, left) - starPulseSeed(seed, right) || left - right,
  );
  const phases = Array.from({ length: count }, () => 0);
  order.forEach((index, slot) => {
    phases[index] = (slot * STAR_PULSE_CYCLE_MS) / count;
  });
  return phases;
}

/** Visit connected groups in marker order, then markers in order within each group. */
export function constellationWaveSchedule(shape: GodConstellation) {
  const neighbors = shape.points.map(() => [] as number[]);
  for (const [from, to] of shape.lines) {
    neighbors[from]!.push(to);
    neighbors[to]!.push(from);
  }

  const seen = new Set<number>();
  const groups: number[][] = [];
  for (let index = 0; index < shape.points.length; index++) {
    if (seen.has(index)) continue;
    const group: number[] = [];
    const stack = [index];
    while (stack.length) {
      const point = stack.pop()!;
      if (seen.has(point)) continue;
      seen.add(point);
      group.push(point);
      stack.push(...neighbors[point]!);
    }
    groups.push(group.sort((a, b) => a - b));
  }

  const slots = shape.points.map(() => 0);
  let slot = 0;
  groups.forEach((group, groupIndex) => {
    if (groupIndex > 0) slot++; // a short beat before the wave crosses to another group
    group.forEach((point) => {
      slots[point] = slot++;
    });
  });
  const stepMs = CONSTELLATION_WAVE.waveDurationMs / Math.max(1, slot - 1);
  const pointDelays = slots.map((position) => CONSTELLATION_WAVE.waveStartMs + position * stepMs);
  const lineDirections = shape.lines.map(([from, to]) =>
    pointDelays[from]! <= pointDelays[to]! ? ([from, to] as const) : ([to, from] as const),
  );
  const lineDelays = lineDirections.map(([from]) => pointDelays[from]!);

  return { order: groups.flat(), pointDelays, lineDelays, lineDirections };
}
