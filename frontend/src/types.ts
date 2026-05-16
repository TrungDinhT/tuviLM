export type Gender = "M" | "F";

export type BirthInput = {
  date: number;
  month: number;
  year: number;
  hour: number;
  gender: Gender;
};

export type TuviTimeInput = BirthInput;

export type CungData = {
  position: string;
  role: string;
  chinhTinh: string[];
  phuTinh: Array<{
    name: string;
    display: string;
    element: string;
  }>;
  tuhoa: string[];
  trangSinh: string | null;
  isTuan: boolean;
  isTriet: boolean;
  isCungThan: boolean;
  ageDaiVan: number | null;
  saoLuu: Array<{
    name: string;
    display: string;
    element: string;
  }>;
};

export type LasoData = {
  id: string;
  summary: string;
  banMenhName: string;
  cucName: string;
  menhCucRelationLabel: string;
  cungByPosition: Record<string, CungData>;
};

export type BuildSaoLuuInput = {
  observationTime: TuviTimeInput;
};

export type ChatToolCall = {
  id?: string | null;
  name: string;
  arguments: unknown;
};

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  createdAt: string;
  toolCalls?: ChatToolCall[];
};
