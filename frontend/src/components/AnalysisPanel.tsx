import ReactMarkdown from "react-markdown";

type Props = {
  position: string | null;
  content: string;
  loading: boolean;
  hasAnalysis: boolean;
  error?: string | null;
  onAnalyze: () => void;
};

export default function AnalysisPanel({ position, content, loading, hasAnalysis, error, onAnalyze }: Props) {
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
        {position && !loading && hasAnalysis && content && <ReactMarkdown>{content}</ReactMarkdown>}
      </div>
    </section>
  );
}
