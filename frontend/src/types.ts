export type Gender = "M" | "F";

export type BirthInput = {
  date: number;
  month: number;
  year: number;
  hour: number;
  gender: Gender;
};

export type TuviTimeInput = BirthInput;

export type StarData = {
  name: string;
  display: string;
  element: string;
  sao_type?: string[];
};

export type CungData = {
  position: string;
  role: string;
  chinhTinh: string[];
  phuTinh: StarData[];
  tuhoa: StarData[];
  trangSinh: string | null;
  isTuan: boolean;
  isTriet: boolean;
  isCungThan: boolean;
  ageDaiVan: number | null;
  saoLuu: StarData[];
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
