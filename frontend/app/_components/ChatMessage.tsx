import type { ChatMessage as Msg } from "../_lib/types";

interface ChatMessageProps {
  msg: Msg;
  onRefClick: (kind: "ref" | "sao", value: string) => void;
}

const TOKEN_RE = /\[\[(ref|sao):([^\]]+)\]\]/g;

export function ChatMessage({ msg, onRefClick }: ChatMessageProps) {
  if (msg.sender === "me") {
    return (
      <div
        className="self-end px-4 py-2.5 max-w-[88%] text-[14px] text-[var(--color-ink)] border border-[rgba(26,22,17,0.14)]"
        style={{ background: "var(--color-paper-2)", borderRadius: "14px 14px 4px 14px" }}
      >
        {msg.body}
      </div>
    );
  }

  return (
    <div className="self-start max-w-[88%] font-serif text-[17px] leading-[1.5] text-[var(--color-ink)]">
      <span className="font-serif italic block mb-1 text-[13px] tracking-[0.5px] uppercase font-medium text-[var(--color-crimson)]">
        Thầy Tuệ
      </span>
      {renderBody(msg.body, onRefClick)}
    </div>
  );
}

function renderBody(body: string, onRefClick: (kind: "ref" | "sao", value: string) => void): React.ReactNode[] {
  const parts: React.ReactNode[] = [];
  let last = 0;
  let m: RegExpExecArray | null;
  let i = 0;
  const re = new RegExp(TOKEN_RE.source, "g");
  while ((m = re.exec(body)) != null) {
    if (m.index > last) parts.push(body.slice(last, m.index));
    const kind = m[1] as "ref" | "sao";
    const value = m[2];
    parts.push(
      <button
        key={`tok-${i++}-${value}`}
        type="button"
        onClick={() => onRefClick(kind, value)}
        className={kind === "ref" ? "ref" : "ref-sao"}
        style={{ background: "transparent", border: 0, padding: 0, font: "inherit", cursor: "pointer" }}
      >
        {value}
      </button>
    );
    last = m.index + m[0].length;
  }
  if (last < body.length) parts.push(body.slice(last));
  return parts;
}
