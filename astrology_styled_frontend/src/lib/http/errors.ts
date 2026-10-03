import type { z } from "zod";

/**
 * Every failure reaching a component, in one shape.
 *
 * Components switch on `kind` to pick their Vietnamese copy. New failure modes
 * are added as new variants, never as a thrown string — a string carries no
 * status, no issues, and nothing a `switch` can be exhaustive over.
 */
type ApiError =
  | { kind: "network" }
  | { kind: "http"; status: number; body: unknown }
  | { kind: "parse"; issues: z.core.$ZodIssue[] }
  | { kind: "stream"; event: string };

/** Thrown by the client so TanStack Query can carry it as a rejection. */
export class ApiErrorException extends Error {
  readonly error: ApiError;

  constructor(error: ApiError) {
    super(describe(error));
    this.name = "ApiErrorException";
    this.error = error;
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
      return error.status >= 500
        ? "Máy chủ đang trục trặc. Bạn thử lại sau ít phút nhé."
        : "Yêu cầu không hợp lệ. Kiểm tra lại thông tin đã nhập nhé.";
    case "parse":
      return "Dữ liệu trả về không đúng định dạng mong đợi.";
    case "stream":
      return "Cuộc trò chuyện bị gián đoạn. Bạn thử gửi lại nhé.";
  }
}
