import type { ChatSessionSummary } from "@/lib/api/schemas";

/**
 * A readable label for a session in the history list. Sessions are created
 * without a title, so an untitled session falls back to its creation date and
 * message count rather than rendering blank.
 */
export function sessionLabel(session: ChatSessionSummary): string {
  if (session.title) return session.title;

  const created = new Date(session.created_at);
  const day = String(created.getDate()).padStart(2, "0");
  const month = String(created.getMonth() + 1).padStart(2, "0");
  const suffix = session.message_count > 0 ? ` · ${session.message_count} tin nhắn` : "";

  return `Cuộc trò chuyện ${day}/${month}${suffix}`;
}
