"use client";

import { createContext, useContext } from "react";

export const AccountRequestContext = createContext<{
  getSignal: () => AbortSignal | undefined;
  userId: string | null | undefined;
}>({ getSignal: () => undefined, userId: undefined });

/** Requests started by a previous account must stop when that account leaves. */
export function useAccountRequestScope() {
  return useContext(AccountRequestContext);
}
