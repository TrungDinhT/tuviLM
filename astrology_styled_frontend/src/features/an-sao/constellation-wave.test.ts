import { describe, expect, it } from "vitest";

import type { GodConstellation } from "@/content/god-constellations";

import { CONSTELLATION_WAVE, constellationWaveSchedule } from "./constellation-wave";

describe("constellationWaveSchedule", () => {
  it("finishes one connected group before moving to an interleaved group", () => {
    const shape: GodConstellation = {
      points: [
        [0, 0],
        [1, 0],
        [2, 0],
        [3, 0],
        [4, 0],
      ],
      lines: [
        [0, 2],
        [1, 3],
        [3, 4],
      ],
    };
    const schedule = constellationWaveSchedule(shape);

    expect(schedule.order).toEqual([0, 2, 1, 3, 4]);
    expect(schedule.pointDelays[2]).toBeLessThan(schedule.pointDelays[1]!);
    expect(schedule.lineDirections).toEqual([
      [0, 2],
      [1, 3],
      [3, 4],
    ]);
    expect(Math.max(...schedule.lineDelays) + CONSTELLATION_WAVE.linkTravelMs).toBeLessThan(
      CONSTELLATION_WAVE.cycleMs,
    );
  });
});
