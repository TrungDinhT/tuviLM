import { useMemo, useState } from "react";
import BirthForm from "./components/BirthForm";
import LasoBoard from "./components/LasoBoard";
import ChatPanel from "./components/ChatPanel";
import { buildLaso, buildSaoLuu, streamChatReply } from "./api/mockApi";
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
  const [viewYear, setViewYear] = useState<number>(new Date().getFullYear());
  const [laso, setLaso] = useState<LasoData | null>(null);
  const [selectedPosition, setSelectedPosition] = useState<string | null>(null);

  const [building, setBuilding] = useState(false);
  const [buildingSaoLuu, setBuildingSaoLuu] = useState(false);
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
    } finally {
      setBuilding(false);
    }
  };

  const handleSelectPosition = (position: string) => {
    setSelectedPosition(position);
  };

  const handleBuildSaoLuu = async () => {
    if (!laso) return;

    setBuildingSaoLuu(true);
    try {
      const result = await buildSaoLuu({
        laso: laso.laso,
        observationTime: {
          date: input.date,
          month: input.month,
          year: viewYear,
          hour: input.hour,
          gender: input.gender
        }
      });

      setLaso((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          laso: result.laso,
          cungByPosition: result.cungByPosition
        };
      });
    } finally {
      setBuildingSaoLuu(false);
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
      const toolCalls = await streamChatReply([...messages, userMsg], (chunk) => {
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

      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantMsg.id
            ? {
              ...m,
              toolCalls
            }
            : m
        )
      );
    } finally {
      setChatBusy(false);
    }
  };

  return (
    <main className="app-root">
      <header className="app-header">
        <h1>TuviLM UI</h1>
        <p>Input + Lá số + Chat</p>
      </header>

      <section className="top-layout">
        <BirthForm
          value={input}
          onChange={setInput}
          viewYear={viewYear}
          onViewYearChange={setViewYear}
          onSubmit={() => void handleBuild()}
          onBuildSaoLuu={() => void handleBuildSaoLuu()}
          loadingBuild={building}
          loadingSaoLuu={buildingSaoLuu}
          canBuildSaoLuu={Boolean(laso)}
        />

        <LasoBoard
          laso={laso}
          selectedPosition={selectedPosition}
          onSelectPosition={handleSelectPosition}
        />
      </section>

      <ChatPanel messages={messages} onSend={handleSendChat} busy={chatBusy || !canChat} />
    </main>
  );
}
