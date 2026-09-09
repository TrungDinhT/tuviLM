import type { NavIcon } from "@/config/site";

/**
 * Tab icons, transcribed from the prototype.
 *
 * Stroke colour comes from `currentColor`, so an item's active state is a
 * single colour change on the button. `.node` marks the parts that fill
 * instead of stroke.
 */
const PATHS: Record<NavIcon, React.ReactNode> = {
  banMenh: <path d="M12 3l2.4 5.3L20 9l-4 4 1 6-5-3-5 3 1-6-4-4 5.6-.7z" />,
  vanHan: (
    <>
      <circle className="fill-current stroke-none" cx="5" cy="8" r="1.6" />
      <circle className="fill-current stroke-none" cx="12" cy="5" r="1.6" />
      <circle className="fill-current stroke-none" cx="19" cy="9" r="1.6" />
      <circle className="fill-current stroke-none" cx="9" cy="16" r="1.6" />
      <circle className="fill-current stroke-none" cx="16" cy="19" r="1.6" />
      <path d="M5 8l7-3 7 4-10 7 3 3" strokeWidth="1.2" />
    </>
  ),
  hoiAi: (
    <>
      <path d="M12 4c4 0 7 2.6 7 6 0 1.7-1 3.2-2 4 .2 2 1 3 1 3-2 0-3.4-.8-4.2-1.4-.6.1-1.2.2-1.8.2-4 0-7-2.6-7-6s3-6 7-6z" />
      <circle className="fill-current stroke-none" cx="12" cy="9.5" r="1" />
    </>
  ),
  nangCao: (
    <>
      <circle cx="12" cy="12" r="8.6" />
      <circle cx="12" cy="12" r="3.2" />
      <path d="M12 3.4v3.4M12 17.2v3.4M3.4 12h3.4M17.2 12h3.4" />
      <path d="m6.6 6.6 2.2 2.2M15.2 15.2l2.2 2.2M17.4 6.6l-2.2 2.2M8.8 15.2l-2.2 2.2" strokeWidth="1" />
    </>
  ),
  hoSo: (
    <>
      <circle cx="12" cy="8" r="3.4" />
      <path d="M5.5 20a6.5 6.5 0 0 1 13 0" />
      <path d="M12 2v1.5M18.5 5.5l-1 1" strokeWidth="1" />
    </>
  ),
};

export function NavIconGlyph({ name, className }: { name: NavIcon; className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      className={className}
      fill="none"
      stroke="currentColor"
      strokeWidth={1.5}
      aria-hidden="true"
    >
      {PATHS[name]}
    </svg>
  );
}
