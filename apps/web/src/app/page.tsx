import { ScreenPad } from "@/components/shell/app-shell";
import { AnSaoScreen } from "@/features/an-sao/an-sao-screen";
import { CRANE_LOADING_SRC } from "@/features/an-sao/loading-video";

/**
 * An sao — the casting screen, and the only route that is never locked.
 * The screen owns its form/loading phases; everything below the shell chrome
 * here is client-side by nature.
 */
export default function Page() {
  return (
    <>
      {/* The loading interlude is one tap away and lasts ~2.6 s; fetching the
          crane only then would leave the ring empty for most of it. Warm the
          cache from the first HTML response instead.
          `rel=prefetch`, not `preload`: Chromium ignores `as="video"` on a
          preload link and downloads nothing — verified in the browser. */}
      <link rel="prefetch" href={CRANE_LOADING_SRC} as="video" type="video/webm" />
      <ScreenPad reserveTabBar={false}>
        <AnSaoScreen />
      </ScreenPad>
    </>
  );
}
