import { toast } from "sonner";

export const TOAST_DURATION_MS = 2200;
export const TOAST_ID = "thien-hac-toast";

const TOAST_CLASS =
  "toast-surface pointer-events-none mx-auto w-fit max-w-[calc(100vw-40px)] rounded-full px-5 py-3 text-center text-[13.5px] font-medium text-ink";

/** Show or replace the app's single transient message. */
export function showToast(message: string): void {
  toast.custom(() => <div className={TOAST_CLASS}>{message}</div>, {
    id: TOAST_ID,
    className: "pointer-events-none w-full",
    duration: TOAST_DURATION_MS,
  });
}

export function dismissToast(): void {
  toast.dismiss(TOAST_ID);
}
