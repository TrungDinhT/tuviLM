import ReactMarkdown from "react-markdown";

type Props = {
  position: string | null;
  content: string;
  loading: boolean;
};

export default function AnalysisPanel({ position, content, loading }: Props) {
  return (
    <section className="panel analysis-panel">
      <h2>Phân tích</h2>
      <div className="analysis-body">
        {!position && <p>Chọn một cung trong lá số để phân tích.</p>}
        {position && loading && <p>Đang phân tích {position}...</p>}
        {position && !loading && content && <ReactMarkdown>{content}</ReactMarkdown>}
      </div>
    </section>
  );
}
