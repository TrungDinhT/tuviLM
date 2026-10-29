import { apiUrl, safeBody } from "@/lib/api/client";
import { readSseData } from "@/lib/api/sse";
import type { BirthInfo } from "@/lib/api/schemas";
import { ApiErrorException } from "@/lib/http/errors";
import { capabilityEventSchema, type CapabilityEvent, type CapabilityProfile } from "./schema";

export async function streamCapabilityReport(
  birth: BirthInfo,
  signal: AbortSignal,
  onEvent: (event: CapabilityEvent) => void | Promise<void>,
): Promise<CapabilityProfile> {
  let response: Response;
  try {
    response = await fetch(apiUrl("/api/v1/laso/strength-weakness/stream"), {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
      body: JSON.stringify(birth),
      signal,
    });
  } catch (error) {
    signal.throwIfAborted();
    throw error instanceof ApiErrorException ? error : new ApiErrorException({ kind: "network" });
  }
  signal.throwIfAborted();
  if (!response.ok)
    throw new ApiErrorException({
      kind: "http",
      status: response.status,
      body: await safeBody(response),
    });
  if (!response.body) throw new ApiErrorException({ kind: "stream", event: "Empty body" });
  let attempt = -1;
  for await (const data of readSseData(response.body)) {
    signal.throwIfAborted();
    const parsed = capabilityEventSchema.safeParse(data);
    if (!parsed.success)
      throw new ApiErrorException({ kind: "parse", issues: parsed.error.issues });
    const event = parsed.data;
    if (event.type === "error") throw new Error(event.message);
    if (event.type === "started" || event.type === "reset") {
      if (event.attempt <= attempt) continue;
      attempt = event.attempt;
    } else if (event.attempt !== attempt) {
      throw new ApiErrorException({ kind: "stream", event: "Unexpected attempt" });
    }
    await onEvent(event);
    if (event.type === "done") return event.profile;
  }
  throw new Error("Kết nối bị gián đoạn trước khi hoàn tất phân tích. Bạn có thể thử lại.");
}
