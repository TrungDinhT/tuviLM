"use client";

import { Toaster } from "sonner";

import { TOAST_DURATION_MS } from "@/lib/toast";

import styles from "./toast.module.css";

const VIEWPORT_OFFSET = "calc(22px + max(var(--tabbar-h), var(--safe-b)))";

/** The global Sonner viewport; messages are sent through `showToast`. */
export function Toast() {
  return (
    <Toaster
      className={styles.toaster}
      position="bottom-center"
      duration={TOAST_DURATION_MS}
      gap={8}
      visibleToasts={1}
      offset={VIEWPORT_OFFSET}
      mobileOffset={VIEWPORT_OFFSET}
      theme="dark"
    />
  );
}
