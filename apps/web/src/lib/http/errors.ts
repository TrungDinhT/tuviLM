import { Data } from "effect";

import type { Issue } from "@/lib/schema";

/**
 * Every failure reaching a component, in one shape.
 *
 * Components switch on `kind` to pick their Vietnamese copy. New failure modes
 * are added as new variants, never as a thrown string — a string carries no
 * status, no issues, and nothing a `switch` can be exhaustive over.
 */
export type ApiError =
  | { kind: "network" }
  | { kind: "http"; status: number; body: unknown }
  | { kind: "parse"; issues: ReadonlyArray<Issue> }
  | { kind: "stream"; event: string };

/**
 * The typed failure of every API effect. It is also the rejection that
 * TanStack Query carries when a request runs as a promise.
 */
export class ApiErrorException extends Data.TaggedError("ApiError")<{ readonly error: ApiError }> {
  constructor(error: ApiError) {
    super({ error });
  }

  override get message(): string {
    return describe(this.error);
  }
}

export function isApiError(value: unknown): value is ApiErrorException {
  return value instanceof ApiErrorException;
}

/** Vietnamese copy for a failure. Exhaustive by construction. */
export function describe(error: ApiError): string {
  switch (error.kind) {
    case "network":
      return "Không kết nối được máy chủ. Kiểm tra mạng rồi thử lại nhé.";
    case "http":
      if (error.status === 402) {
        return "Bạn không đủ xu. Trò chuyện với AI cần 3 xu cho mỗi tin nhắn.";
      }
      return error.status >= 500
        ? "Máy chủ đang trục trặc. Bạn thử lại sau ít phút nhé."
        : "Yêu cầu không hợp lệ. Kiểm tra lại thông tin đã nhập nhé.";
    case "parse":
      return "Dữ liệu trả về không đúng định dạng mong đợi.";
    case "stream":
      return "Cuộc trò chuyện bị gián đoạn. Bạn thử gửi lại nhé.";
  }
}
