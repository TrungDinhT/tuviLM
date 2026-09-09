"use client";

import * as RadixDialog from "@radix-ui/react-dialog";
import { useEffect, useRef } from "react";

import { cn } from "@/lib/utils";

/**
 * Remembers what had focus before the dialog opened.
 *
 * Radix restores focus to `Dialog.Trigger`'s ref on close. Our dialogs are
 * opened from wherever the design says — a chart cell, a nav item, a menu row
 * — so there is often no `Trigger`, and that ref is null: focus would land on
 * `<body>` and a keyboard user would lose their place. Tracking focus while
 * the dialog is closed gives us the element to hand it back to.
 */
function useRestoreFocus(open: boolean) {
  const lastFocused = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (open) return;
    const remember = () => {
      const active = document.activeElement;
      if (!(active instanceof HTMLElement)) return;
      // Radix focuses the first control inside the dialog on open, and that
      // happens before this parent effect tears its listener down — child
      // effects run first. Without this guard we would remember a button that
      // is about to unmount, and focus would fall to <body> after all.
      if (active.closest('[role="dialog"]')) return;
      lastFocused.current = active;
    };
    remember();
    document.addEventListener("focusin", remember);
    return () => document.removeEventListener("focusin", remember);
  }, [open]);

  return (event: Event) => {
    // Preventing default stops Radix from focusing its (absent) trigger.
    event.preventDefault();
    lastFocused.current?.focus();
  };
}

/**
 * The application's overlay.
 *
 * Radix supplies the parts that are genuinely hard and easy to get subtly
 * wrong: focus trap, focus restore, Escape, `aria-modal`, and background
 * scroll lock. Everything visual is ours.
 *
 * Two variants, because the design has two real shapes:
 *
 * - `center` — a card in the middle of the viewport. The two confirm boxes.
 * - `panel`  — full-screen on phone and tablet, a right-anchored drawer from
 *              the `lg` tier where the scrim disappears entirely and the panel
 *              sits beside the content rather than over it.
 *
 * The panel pins its title to the top edge and `footer` to the bottom edge;
 * only the body between them scrolls. The center card scrolls as one block.
 *
 * Padding accounts for the safe-area insets and for `--tabbar-h`, which is
 * `0px` at the desktop tier — so the same expression is correct at every size.
 */
type DialogVariant = "center" | "panel";

const CONTENT: Record<DialogVariant, string> = {
  center: [
    "fixed top-1/2 left-1/2 z-55 w-[calc(100%-48px)] max-w-[380px]",
    "-translate-x-1/2 -translate-y-1/2",
    "overlay-card rounded-3xl p-[26px] pt-7",
    "max-h-[calc(100dvh-48px)] overflow-y-auto",
  ].join(" "),
  panel: [
    // A flex column, so the header and footer stay put while the body scrolls.
    "fixed z-55 overlay-card flex flex-col",
    // Phone and tablet: a sheet filling the column.
    "top-[calc(24px+var(--safe-t))] bottom-[calc(24px+var(--tabbar-h))]",
    "left-1/2 w-[calc(100%-32px)] max-w-[370px] -translate-x-1/2 rounded-2xl p-5 pt-6",
    // Desktop: a drawer anchored to the right of the working area.
    "lg:top-[calc(var(--topbar-h)+18px)] lg:bottom-7 lg:left-auto lg:right-7",
    "lg:w-[376px] lg:max-w-none lg:translate-x-0",
  ].join(" "),
};

export function Dialog({
  open,
  onOpenChange,
  variant = "center",
  title,
  description,
  footer,
  children,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  variant?: DialogVariant;
  /** Required for accessibility. */
  title: React.ReactNode;
  description?: React.ReactNode;
  /** Pinned to the bottom of the `panel` variant; follows the content in `center`. */
  footer?: React.ReactNode;
  children?: React.ReactNode;
}) {
  const onCloseAutoFocus = useRestoreFocus(open);

  const header = (
    <>
      <RadixDialog.Title
        className={cn(
          "font-display text-[23px] leading-tight font-semibold",
          variant === "center" && "text-center",
        )}
      >
        {title}
      </RadixDialog.Title>
      {description ? (
        <RadixDialog.Description
          className={cn(
            "mt-[11px] text-[13.5px] leading-relaxed text-muted",
            variant === "center" && "text-center",
          )}
        >
          {description}
        </RadixDialog.Description>
      ) : null}
    </>
  );

  return (
    <RadixDialog.Root open={open} onOpenChange={onOpenChange}>
      <RadixDialog.Portal>
        {/* The desktop drawer sits beside the content, so it drops the scrim
            rather than dimming a page the user is still reading. */}
        <RadixDialog.Overlay
          className={cn(
            "overlay-scrim fixed inset-0 z-50",
            variant === "panel" && "lg:hidden",
          )}
        />
        <RadixDialog.Content
          aria-modal="true"
          onCloseAutoFocus={onCloseAutoFocus}
          className={CONTENT[variant]}
        >
          {variant === "panel" ? (
            <>
              <div className="shrink-0">{header}</div>
              <div className="min-h-0 flex-1 overflow-y-auto">{children}</div>
              {footer ? <div className="shrink-0 pt-3">{footer}</div> : null}
            </>
          ) : (
            <>
              {header}
              {children}
              {footer}
            </>
          )}
        </RadixDialog.Content>
      </RadixDialog.Portal>
    </RadixDialog.Root>
  );
}

export const DialogClose = RadixDialog.Close;
