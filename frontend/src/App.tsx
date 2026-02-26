import { useMemo, useState } from "react";
import BirthForm from "./components/BirthForm";
import LasoBoard from "./components/LasoBoard";
import AnalysisPanel from "./components/AnalysisPanel";
import ChatPanel from "./components/ChatPanel";
import { buildLaso, getAnalysis, streamChatReply } from "./api/mockApi";
import type { BirthInput, ChatMessage, LasoData } from "./types";

const INITIAL_INPUT: BirthInput = {
  date: 4,
  month: 4,
  year: 1998,
  hour: 8,
  gender: "M"
};

function id(prefix: string): string {
  return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export default function App() {
  const [input, setInput] = useState<BirthInput>(INITIAL_INPUT);
  const [laso, setLaso] = useState<LasoData | null>(null);
  const [selectedPosition, setSelectedPosition] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState("");

  const [building, setBuilding] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [chatBusy, setChatBusy] = useState(false);

  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: id("welcome"),
      role: "assistant",
      content: "Xin chào, bạn hãy lập lá số và chọn một cung để bắt đầu.",
      createdAt: new Date().toISOString()
    }
  ]);

  const canChat = useMemo(() => laso !== null, [laso]);

  const handleBuild = async () => {
    setBuilding(true);
    try {
      const result = await buildLaso(input);
      setLaso(result);
      const nextPosition = "Tị";
      setSelectedPosition(nextPosition);
      setAnalyzing(true);
      const analysisText = await getAnalysis(nextPosition);
      setAnalysis(analysisText);
    } finally {
      setAnalyzing(false);
      setBuilding(false);
    }
  };

  const handleSelectPosition = async (position: string) => {
    setSelectedPosition(position);
    setAnalyzing(true);
    try {
      const analysisText = await getAnalysis(position);
      setAnalysis(analysisText);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleSendChat = async (text: string) => {
    if (!canChat) return;

    const userMsg: ChatMessage = {
      id: id("user"),
      role: "user",
      content: text,
      createdAt: new Date().toISOString()
    };

    const assistantMsg: ChatMessage = {
      id: id("assistant"),
      role: "assistant",
      content: "",
      createdAt: new Date().toISOString()
    };

    setMessages((prev) => [...prev, userMsg, assistantMsg]);
    setChatBusy(true);

    try {
      await streamChatReply([...messages, userMsg], selectedPosition, (chunk) => {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantMsg.id
              ? {
                  ...m,
                  content: m.content + chunk
                }
              : m
          )
        );
      });
    } finally {
      setChatBusy(false);
    }
  };

  return (
    <main className="app-root">
      <header className="app-header">
        <h1>TuviLM UI</h1>
        <p>Input + Lá số + Phân tích + Chat (dummy API)</p>
      </header>

      <section className="top-layout">
        <BirthForm value={input} onChange={setInput} onSubmit={() => void handleBuild()} loading={building} />

        <LasoBoard
          laso={laso}
          selectedPosition={selectedPosition}
          onSelectPosition={(position) => void handleSelectPosition(position)}
        />

        <AnalysisPanel position={selectedPosition} content={analysis} loading={analyzing} />
      </section>

      <ChatPanel messages={messages} onSend={handleSendChat} busy={chatBusy || !canChat} />
    </main>
  );
}
