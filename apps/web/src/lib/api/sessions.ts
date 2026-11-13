import { mutationOptions } from "@tanstack/react-query";

import type { AccountRequestScope } from "./account-request";
import { newIdempotencyKey, request } from "./client";
import { apiEndpoints } from "./endpoints";
import { mutationKeys, queryKeys } from "./queryKeys";
import { createSessionRequestSchema, createSessionResponseSchema } from "./schemas";

/**
 * Create a new session under a chart profile and refresh the session list.
 *
 * Each invocation mints a fresh `Idempotency-Key`; mutations never auto-retry,
 * so a manual retry is a fresh create action with its own key.
 */
export const createSessionMutationOptions = ({
  getSignal,
  userId,
  profileId,
}: AccountRequestScope & { profileId: string | null }) =>
  mutationOptions({
    mutationKey: mutationKeys.createSession(profileId),
    mutationFn: () => {
      if (profileId === null) throw new Error("chart profile id required");
      return request(apiEndpoints.profileSessions(profileId), {
        method: "POST",
        body: createSessionRequestSchema.parse({ title: null }),
        schema: createSessionResponseSchema,
        withAuth: true,
        expectedUserId: userId,
        idempotencyKey: newIdempotencyKey(),
        signal: getSignal(),
      });
    },
    onSuccess: (_data, _variables, _onMutateResult, { client }) => {
      if (getSignal()?.aborted) return;
      if (profileId === null) return;
      void client.invalidateQueries({ queryKey: queryKeys.sessions.byProfile(profileId) });
    },
  });
