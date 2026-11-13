"use client";

import { createContext, useContext } from "react";

/** The account that starts a request, and the signal that stops it when the account leaves. */
export interface AccountRequestScope {
  getSignal: () => AbortSignal | undefined;
  userId: string | null | undefined;
}

export const AccountRequestContext = createContext<AccountRequestScope>({
  getSignal: () => undefined,
  userId: undefined,
});

/** Requests started by a previous account must stop when that account leaves. */
export const useAccountRequestScope = () => useContext(AccountRequestContext);
