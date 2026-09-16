import type { WorkflowRun } from "./runs";

export function runFixture(overrides: Partial<WorkflowRun> = {}): WorkflowRun {
  return {
    id: "r1",
    workflow: "echo",
    resource_id: "chart:1",
    inputs: { question: "Hello" },
    status: "running",
    state: { text: "", progress: null, metadata: {} },
    result: null,
    error: null,
    seq: 1,
    cancel_requested: false,
    created_at: "2026-09-15T00:00:00Z",
    updated_at: "2026-09-15T00:00:00Z",
    ...overrides,
  };
}

export function jsonResponse(value: unknown, status = 200) {
  return new Response(JSON.stringify(value), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}
