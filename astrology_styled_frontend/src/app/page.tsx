import { ScreenPad } from "@/components/shell/app-shell";
import { AnSaoScreen } from "@/features/an-sao/an-sao-screen";

/**
 * An sao — the casting screen, and the only route that is never locked.
 * The screen owns its form/loading phases; everything below the shell chrome
 * here is client-side by nature.
 */
export default function Page() {
  return (
    <ScreenPad>
      <AnSaoScreen />
    </ScreenPad>
  );
}
