import ReactMarkdown from "react-markdown";
import type { ChatToolCall } from "../types";

type Props = {
  position: string | null;
  content: string;
  toolCalls?: ChatToolCall[];
  loading: boolean;
  hasAnalysis: boolean;
  error?: string | null;
  onAnalyze: () => void;
};

function formatToolCallLabel(toolCall: ChatToolCall): string {
  const args = toolCall.arguments;
  if (args === null || args === undefined) return `${toolCall.name}()`;

  if (typeof args === "string") {
    try {
      return formatToolCallLabel({ ...toolCall, arguments: JSON.parse(args) });
    } catch {
      return `${toolCall.name}(${args})`;
    }
  }

  if (Array.isArray(args)) {
    return `${toolCall.name}(${args.map(String).join(", ")})`;
  }

  if (typeof args === "object") {
    const values = Object.values(args as Record<string, unknown>)
      .filter((value) => value !== null && value !== undefined)
      .map(String);
    return `${toolCall.name}(${values.join(", ")})`;
  }

  return `${toolCall.name}(${String(args)})`;
}

function formatToolResult(result: unknown): string {
  if (result === null || result === undefined) return "";
  if (typeof result === "string") return result;
  try {
    return JSON.stringify(result, null, 2);
  } catch {
    return String(result);
  }
}

export default function AnalysisPanel({
  position,
  content,
  toolCalls,
  loading,
  hasAnalysis,
  error,
  onAnalyze
}: Props) {
  return (
    <section className="panel analysis-panel">
      <h2>Phân tích</h2>
      <div className="analysis-body">
        {!position && <p>Chọn một cung trong lá số để phân tích.</p>}
        {position && loading && <p>Đang phân tích {position}...</p>}
        {position && !loading && !hasAnalysis && (
          <div>
            <p>Cung {position} chưa được phân tích.</p>
            <button className="primary-btn" onClick={onAnalyze}>
              Phân tích cung này
            </button>
          </div>
        )}
        {position && !loading && error && <p>{error}</p>}
        {position && !loading && hasAnalysis && (
          <>
            {toolCalls && toolCalls.length > 0 && (
              <div className="tool-call-list">
                {toolCalls.map((toolCall, index) => {
                  const resultText = formatToolResult(toolCall.result);
                  const key = toolCall.id ?? `${toolCall.name}-${index}`;
                  if (!resultText) {
                    return (
                      <span className="tool-call" key={key}>
                        {formatToolCallLabel(toolCall)}
                      </span>
                    );
                  }
                  return (
                    <details className="tool-call tool-call-detail" key={key}>
                      <summary>{formatToolCallLabel(toolCall)}</summary>
                      <pre className="tool-call-result">{resultText}</pre>
                    </details>
                  );
                })}
              </div>
            )}
            {content && <ReactMarkdown>{content}</ReactMarkdown>}
          </>
        )}
      </div>
    </section>
  );
}
