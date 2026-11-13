"use client";

import { useIsMutating } from "@tanstack/react-query";
import { useState } from "react";

import { mutationKeys } from "@/lib/api/queryKeys";

/**
 * The switcher panel's own state: whether it is open, and the list filter.
 *
 * The panel must not close while a chart is being opened. It does not hold
 * the mutation for that check: it reads the pending state through the
 * mutation key, so it works whichever unit started the request.
 */
export const useSwitcherPanel = () => {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const isOpening = useIsMutating({ mutationKey: mutationKeys.openChartProfile() }) > 0;

  const close = () => {
    setOpen(false);
    setSearch("");
  };

  const changeOpen = (next: boolean) => {
    if (isOpening) return;
    if (next) setOpen(true);
    else close();
  };

  return { open, search, setSearch, changeOpen, close, isOpening };
};
