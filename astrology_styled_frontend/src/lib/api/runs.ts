import { z } from "zod";

import { request } from "./client";
import { ApiErrorException } from "@/lib/http/errors";

export const runStatusSchema = z.enum(["queued", "running", "succeeded", "failed", "cancelled"]);
export const runSchema = z.object({
  id: z.string(),
  workflow: z.string(),
  resource_id: z.string(),
  inputs: z.record(z.string(), z.unknown()),
  status: runStatusSchema,
  state: z.object({
    text: z.string(),
    progress: z.string().nullable(),
    metadata: z.record(z.string(), z.unknown()),
  }),
  result: z.unknown(),
  error: z.string().nullable(),
  seq: z.number().int().nonnegative(),
  cancel_requested: z.boolean(),
  created_at: z.string(),
  updated_at: z.string(),
});
export type WorkflowRun = z.infer<typeof runSchema>;
export type RunInputs = Record<string, unknown>;

export const isRunTerminal = (run: WorkflowRun) =>
  run.status === "succeeded" || run.status === "failed" || run.status === "cancelled";

// Bound each HTTP request so a connection lost while backgrounded cannot stall observation.
function requestSignal(signal?: AbortSignal): AbortSignal {
  const timeout = AbortSignal.timeout(15_000);
  return signal ? AbortSignal.any([signal, timeout]) : timeout;
}

export function getRun(id: string, signal?: AbortSignal) {
  return request(`/api/v1/runs/${encodeURIComponent(id)}`, {
    schema: runSchema,
    withOwner: true,
    signal: requestSignal(signal),
  });
}

export function latestRuns(workflow: string, resourceId: string, signal?: AbortSignal) {
  const params = new URLSearchParams({ workflow, resource_id: resourceId });
  return request(`/api/v1/runs?${params}`, {
    schema: z.array(runSchema),
    withOwner: true,
    signal: requestSignal(signal),
  });
}

export function cancelRun(id: string, signal?: AbortSignal) {
  return request(`/api/v1/runs/${encodeURIComponent(id)}/cancel`, {
    method: "POST",
    schema: runSchema,
    withOwner: true,
    signal: requestSignal(signal),
  });
}

export function isTransientRunError(error: unknown): boolean {
  return (
    !(error instanceof ApiErrorException) ||
    error.error.kind === "network" ||
    (error.error.kind === "http" &&
      (error.error.status >= 500 || error.error.status === 429 || error.error.status === 408))
  );
}

export function submitRun(
  workflow: string,
  inputs: RunInputs,
  idempotencyKey: string,
  signal: AbortSignal,
) {
  return request("/api/v1/runs", {
    method: "POST",
    body: { workflow, inputs },
    schema: runSchema,
    withOwner: true,
    idempotencyKey,
    signal: requestSignal(signal),
  });
}
