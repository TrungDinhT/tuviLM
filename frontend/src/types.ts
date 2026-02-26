export type Gender = "M" | "F";

export type BirthInput = {
  date: number;
  month: number;
  year: number;
  hour: number;
  gender: Gender;
};

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
};

export type LasoData = {
  id: string;
  summary: string;
  cungByPosition: Record<string, CungData>;
};

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  createdAt: string;
};
