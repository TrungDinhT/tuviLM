/**
 * The screen header shared by every tab — phone and tablet only.
 *
 * From `lg` up the desktop top bar already titles the screen, so this band
 * hides itself; rendering both stacks the same title twice ("Lá số của bạn /
 * Hỏi AI · Thiên Hạc" above "Hỏi AI / Thiên Hạc"). A screen that needs desktop
 * hero content beyond the top bar builds it as part of that screen, not here.
 *
 * Before this existed each screen set its own inline styles and they drifted —
 * title sizes of 30/24/26px, labels that were sometimes 12px muted and
 * sometimes 9px accent. One shape now: small uppercase eyebrow, Fraunces
 * title, optional subtitle.
 *
 * The negative horizontal margins let the band bleed to the edge of a padded
 * parent; without them, content scrolling underneath shows through the two
 * gutters. `top` is `--topbar-h`, which is `0px` until the desktop tier, so
 * the header rests below the top bar there and at the viewport edge elsewhere.
 *
 * The negative *top* margin matters just as much and is easy to miss: it
 * cancels `ScreenPad`'s `padding-top` so the band starts flush against the
 * sticky threshold. Without it the header rests that far below where it will
 * pin, leaving an unblurred strip for content to scroll through and making the
 * band appear to jump the moment it sticks. Keep it equal to `ScreenPad`'s
 * padding-top at every tier.
 */
export function StickyHeader({
  eyebrow,
  title,
  subtitle,
}: {
  eyebrow: string;
  title: string;
  subtitle?: string;
}) {
  return (
    <div
      className={[
        "bg-[linear-gradient(180deg,color-mix(in_srgb,var(--color-bg-2)_70%,transparent)_58%,color-mix(in_srgb,var(--color-bg-2)_38%,transparent)_82%,transparent)] sticky top-[var(--topbar-h)] z-14 mb-3 backdrop-blur-[22px] backdrop-saturate-[135%] lg:hidden",
        "-mt-[calc(10px+var(--safe-t))] -mx-[22px] px-[22px]",
        "pt-[calc(12px+var(--safe-t))] pb-3",
        "md:-mx-[30px] md:px-[30px]",
        "lg:-mt-[calc(18px+var(--safe-t))] lg:-mx-10 lg:px-10",
      ].join(" ")}
    >
      <div className="text-[10px] font-bold tracking-[0.26em] text-accent uppercase">
        {eyebrow}
      </div>
      <h2 className="mt-[7px] font-display text-[26px] leading-[1.06] font-semibold tracking-[-0.01em] md:text-[29px]">
        {title}
      </h2>
      {subtitle ? (
        <p className="mt-[7px] max-w-[54ch] text-[13.5px] leading-normal text-muted">
          {subtitle}
        </p>
      ) : null}
    </div>
  );
}
