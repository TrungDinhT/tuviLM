import type { ZodIssue } from 'zod';

export type ApiError =
  | { kind: 'network' }
  | { kind: 'http'; status: number; body: unknown }
  | { kind: 'parse'; issues: ZodIssue[] }
  | { kind: 'no-session' }
  | { kind: 'stream'; message: string };

export function isApiError(value: unknown): value is ApiError {
  if (!value || typeof value !== 'object') return false;
  const kind = (value as { kind?: unknown }).kind;
  return kind === 'network' || kind === 'http' || kind === 'parse' || kind === 'no-session' || kind === 'stream';
}

export function apiErrorMessage(err: ApiError): string {
  switch (err.kind) {
    case 'network':
      return 'Không kết nối được đến máy chủ. Vui lòng kiểm tra mạng.';
    case 'http':
      if (err.status === 422) return 'Dữ liệu nhập không hợp lệ.';
      if (err.status >= 500) return 'Máy chủ gặp lỗi. Vui lòng thử lại sau.';
      return `Máy chủ trả về lỗi (${err.status}).`;
    case 'parse':
      return 'Phản hồi từ máy chủ không đúng định dạng.';
    case 'no-session':
      return 'Phiên trò chuyện chưa sẵn sàng. Vui lòng tạo lại lá số.';
    case 'stream':
      return err.message;
  }
}
