"use client";

import { useMutation } from "@tanstack/react-query";

import { request } from "./client";
import { type BirthInfo, buildLasoResponseSchema } from "./schemas";

/**
 * Cast a chart from birth information.
 *
 * A mutation rather than a query: the call is user-initiated and has a side
 * effect on the backend, which stores the built lá số for the sao-lưu and chat
 * endpoints to read.
 *
 * The other endpoints get their hooks when the screens that need them land.
 * This one exists now to prove the whole path — env, headers, Zod parsing,
 * error normalization — end to end.
 */
export function useBuildLaso() {
  return useMutation({
    mutationFn: (birth: BirthInfo) =>
      request("/api/v1/laso/build", {
        method: "POST",
        body: birth,
        schema: buildLasoResponseSchema,
      }),
  });
}
