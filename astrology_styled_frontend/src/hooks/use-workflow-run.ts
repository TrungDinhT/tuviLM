"use client";

import { useMemo } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { z } from "zod";

import { mintOwnerId, newIdempotencyKey } from "@/lib/api/client";
import { getOwnerId } from "@/lib/api/owner";
import {
  cancelRun,
  getRun,
  isRunTerminal,
  isTransientRunError,
  latestRuns,
  submitRun,
  type RunInputs,
  type WorkflowRun,
} from "@/lib/api/runs";
import { ApiErrorException } from "@/lib/http/errors";

const pendingSchema = z.object({ key: z.string(), inputs: z.record(z.string(), z.unknown()) });
type Pending = z.infer<typeof pendingSchema>;
type View = { run: WorkflowRun | null; pending: Pending | null; storageKey: string };
const keyFor = (workflow: string, resourceId: string | null) => [
  "workflow-run",
  workflow,
  resourceId,
];

function loadPending(key: string): Pending | null {
  try {
    return pendingSchema.parse(JSON.parse(localStorage.getItem(key) ?? "null"));
  } catch {
    return null;
  }
}
function savePending(key: string, value: Pending | null) {
  try {
    if (value) localStorage.setItem(key, JSON.stringify(value));
    else localStorage.removeItem(key);
  } catch {
    /* Accepted runs can still be discovered from the server. */
  }
}

/** Query owns HTTP retries/polling. The backend owns execution, even after unmount. */
export function useWorkflowRun<T = unknown>({
  workflow,
  resourceId,
  resultSchema,
}: {
  workflow: string;
  resourceId: string | null;
  resultSchema?: z.ZodType<T>;
}) {
  const client = useQueryClient();
  const queryKey = keyFor(workflow, resourceId);
  const query = useQuery({
    queryKey,
    enabled: resourceId !== null,
    queryFn: async ({ signal }): Promise<View> => {
      const owner = await getOwnerId(mintOwnerId);
      signal.throwIfAborted();
      const storageKey = `workflow-submit:${JSON.stringify([owner, workflow, resourceId])}`;
      const cached = client.getQueryData<View>(queryKey);
      const pending = loadPending(storageKey) ?? cached?.pending;
      let run: WorkflowRun | null;
      if (pending) {
        try {
          run = await submitRun(workflow, pending.inputs, pending.key, signal);
        } catch (error) {
          signal.throwIfAborted();
          if (!isTransientRunError(error)) savePending(storageKey, null);
          if (!(
            error instanceof ApiErrorException &&
            error.error.kind === "http" &&
            error.error.status === 409
          ))
            throw error;
          // Another tab already started this resource; follow its run.
          [run = null] = await latestRuns(workflow, resourceId!, signal);
          if (!run) throw error;
        }
        savePending(storageKey, null);
      } else if (cached?.run && !isRunTerminal(cached.run)) {
        run = await getRun(cached.run.id, signal);
      } else {
        [run = null] = await latestRuns(workflow, resourceId!, signal);
      }
      return { run, pending: null, storageKey };
    },
    staleTime: 0,
    refetchOnMount: "always",
    refetchOnWindowFocus: "always",
    refetchOnReconnect: "always",
    refetchInterval: ({ state }) =>
      state.data?.run && !isRunTerminal(state.data.run) ? 1_000 : false,
    retry: (_count, error) => isTransientRunError(error),
    retryDelay: (attempt) => Math.min(1_000 * 2 ** attempt, 10_000),
    structuralSharing: (previous, incoming) => {
      const old = previous as View | undefined,
        next = incoming as View;
      return old?.run && next.run?.id === old.run.id && next.run.seq < old.run.seq
        ? { ...next, run: old.run }
        : next;
    },
  });
  const run = query.data?.run ?? null;
  const submitting = !!query.data?.pending && !query.isError;
  const active = submitting || !!(run && !isRunTerminal(run));
  const cancel = useMutation({
    mutationFn: (id: string) => cancelRun(id),
    onSuccess: (next) =>
      client.setQueryData<View>(keyFor(next.workflow, next.resource_id), (view) =>
        view ? { ...view, run: view.run && view.run.seq > next.seq ? view.run : next } : view,
      ),
  });
  const decoded = useMemo(() => {
    if (run?.status !== "succeeded") return { result: undefined, error: null };
    if (!resultSchema) return { result: run.result as T, error: null };
    const parsed = resultSchema.safeParse(run.result);
    return parsed.success
      ? { result: parsed.data, error: null }
      : {
          result: undefined,
          error: new ApiErrorException({ kind: "parse", issues: parsed.error.issues }),
        };
  }, [run, resultSchema]);

  return {
    run,
    inputs: query.data?.pending?.inputs ?? run?.inputs ?? null,
    loading: resourceId !== null && query.isPending,
    submitting,
    active,
    result: decoded.result,
    error: query.error ?? decoded.error ?? cancel.error,
    start: (inputs: RunInputs) => {
      const view = client.getQueryData<View>(queryKey);
      if (
        !view ||
        query.isFetching ||
        (view.pending && !query.isError) ||
        (view.run && !isRunTerminal(view.run))
      )
        return;
      const pending = { inputs, key: newIdempotencyKey() };
      savePending(view.storageKey, pending);
      client.setQueryData<View>(queryKey, { ...view, run: null, pending });
      void query.refetch();
    },
    cancel: () => {
      if (run) cancel.mutate(run.id);
    },
    retry: () => {
      void query.refetch();
    },
  };
}
