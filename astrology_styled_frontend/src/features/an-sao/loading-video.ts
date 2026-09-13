/**
 * The Thiên Hạc crane that plays over the orbit rings while the chart builds.
 *
 * Its own module so the An sao route can preload it — a "use client" module's
 * exports reach a server component as client references, not as the value.
 *
 * The source has no alpha channel: the crane sits on pure black, so it is
 * composited with `mix-blend-mode: screen`, which drops the black entirely.
 */
export const CRANE_LOADING_SRC = "/assets/golden_crane_loading_md.webm";
