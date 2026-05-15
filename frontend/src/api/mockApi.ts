import type { BirthInput, BuildSaoLuuInput, ChatMessage, ChatToolCall, CungData, LasoData } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

const BOARD_ORDER = [
  "Tý", "Sửu", "Dần", "Mão",
  "Thìn", "Tị", "Ngọ", "Mùi",
  "Thân", "Dậu", "Tuất", "Hợi"
];

const ROLE_BY_POSITION: Record<string, string> = {
  "Tị": "Mệnh",
  "Ngọ": "Phụ Mẫu",
  "Mùi": "Phúc Đức",
  "Thân": "Điền Trạch",
  "Dậu": "Quan Lộc",
  "Tuất": "Nô Bộc",
  "Hợi": "Thiên Di",
  "Tý": "Tật Ách",
  "Sửu": "Tài Bạch",
  "Dần": "Tử Tức",
  "Mão": "Phu Thê",
  "Thìn": "Huynh Đệ"
};

const CHINH_TINH = [
  "Tử Vi", "Thiên Phủ", "Thái Dương", "Vũ Khúc", "Liêm Trinh", "Thất Sát",
  "Tham Lang", "Phá Quân", "Thiên Đồng", "Thiên Cơ", "Thái Âm", "Thiên Lương", "Cự Môn", "Thiên Tướng"
];

const PHU_TINH = [
  "Văn Xương", "Văn Khúc", "Lộc Tồn", "Hóa Lộc", "Hóa Quyền", "Hóa Khoa",
  "Thiên Khôi", "Thiên Việt", "Hữu Bật", "Tả Phù", "Địa Không", "Địa Kiếp"
];

function randomPick<T>(arr: T[], index: number): T {
  return arr[index % arr.length];
}

function buildDummyCung(position: string, role: string, idx: number): CungData {
  const main1 = randomPick(CHINH_TINH, idx * 2);
  const main2 = randomPick(CHINH_TINH, idx * 2 + 1);
  const aux1 = randomPick(PHU_TINH, idx * 3);
  const aux2 = randomPick(PHU_TINH, idx * 3 + 1);

  return {
    position,
    role,
    chinhTinh: [main1, main2],
    phuTinh: [
      { name: aux1, display: aux1, element: "Thủy" },
      { name: aux2, display: aux2, element: "Mộc" }
    ],
    tuhoa: [],
    trangSinh: ["Tràng Sinh", "Mộc Dục", "Quan Đới", "Lâm Quan", "Đế Vượng", "Suy", "Bệnh", "Tử", "Mộ", "Tuyệt", "Thai", "Dưỡng"][idx],
    isTuan: false,
    isTriet: false,
    isCungThan: false,
    ageDaiVan: 0,
    saoLuu: []
  };
}

export async function buildLaso(input: BirthInput): Promise<LasoData> {
  const response = await fetch(`${API_BASE_URL}/api/v1/laso/build`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input)
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`Build lá số failed (${response.status}): ${detail}`);
  }

  const payload = await response.json() as {
    id: string;
    summary: string;
    cung_by_position: Record<string, {
      position: string;
      role: string | null;
      chinh_tinh: string[];
      phu_tinh: Array<{ name: string; display: string; element: string }>;
      tuhoa: string[];
      trang_sinh: string | null;
      is_tuan: boolean;
      is_triet: boolean;
      is_cung_than: boolean;
      age_daivan: number | null;
      saoLuu: Array<{ name: string; display: string; element: string }>;
    }>;
  };

  const mapped: Record<string, CungData> = {};
  for (const position of BOARD_ORDER) {
    const item = payload.cung_by_position[position];
    if (item) {
      mapped[position] = {
        position: item.position,
        role: item.role ?? ROLE_BY_POSITION[position] ?? "Cung",
        chinhTinh: item.chinh_tinh,
        phuTinh: item.phu_tinh,
        tuhoa: item.tuhoa,
        trangSinh: item.trang_sinh,
        isTuan: item.is_tuan,
        isTriet: item.is_triet,
        isCungThan: item.is_cung_than,
        ageDaiVan: item.age_daivan ?? null,
        saoLuu: item.saoLuu ?? []
      };
      continue;
    }

    const fallbackRole = ROLE_BY_POSITION[position] ?? "Cung";
    mapped[position] = buildDummyCung(position, fallbackRole, BOARD_ORDER.indexOf(position));
  }

  return {
    id: payload.id,
    summary: payload.summary,
    cungByPosition: mapped
  };
}

// TODO : This route is failed by unknown reason,
export async function buildSaoLuu(input: BuildSaoLuuInput): Promise<{
  cungByPosition: Record<string, CungData>;
}> {
  const response = await fetch(`${API_BASE_URL}/api/v1/laso/build_sao_luu`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      observation_time: {
        date: input.observationTime.date,
        month: input.observationTime.month,
        year: input.observationTime.year,
        hour: input.observationTime.hour,
        gender: input.observationTime.gender
      }
    })
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`Build sao lưu failed (${response.status}): ${detail}`);
  }

  const payload = await response.json() as {
    cung_by_position: Record<string, {
      position: string;
      role: string | null;
      chinh_tinh: string[];
      phu_tinh: Array<{ name: string; display: string; element: string }>;
      tuhoa: string[];
      trang_sinh: string | null;
      is_tuan: boolean;
      is_triet: boolean;
      is_cung_than: boolean;
      age_daivan: number | null;
      saoLuu: Array<{ name: string; display: string; element: string }>;
    }>;
  };

  const mapped: Record<string, CungData> = {};
  for (const position of BOARD_ORDER) {
    const item = payload.cung_by_position[position];
    if (item) {
      mapped[position] = {
        position: item.position,
        role: item.role ?? ROLE_BY_POSITION[position] ?? "Cung",
        chinhTinh: item.chinh_tinh,
        phuTinh: item.phu_tinh,
        tuhoa: item.tuhoa,
        trangSinh: item.trang_sinh,
        isTuan: item.is_tuan,
        isTriet: item.is_triet,
        isCungThan: item.is_cung_than,
        ageDaiVan: item.age_daivan ?? null,
        saoLuu: item.saoLuu ?? []
      };
      continue;
    }

    const fallbackRole = ROLE_BY_POSITION[position] ?? "Cung";
    mapped[position] = buildDummyCung(position, fallbackRole, BOARD_ORDER.indexOf(position));
  }

  return {
    cungByPosition: mapped
  };
}

export async function streamChatReply(
  messages: ChatMessage[],
  onChunk: (chunk: string) => void
): Promise<ChatToolCall[]> {
  const userMessages = messages.filter((m) => m.role === "user");
  const latest = userMessages.length > 0 ? userMessages[userMessages.length - 1].content : "";

  const response = await fetch(`${API_BASE_URL}/api/v1/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message: latest
    })
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`Chat failed (${response.status}): ${detail}`);
  }

  const payload = await response.json() as {
    answer: string;
    tool_calls?: Array<{
      id?: string | null;
      name?: string;
      tool_name?: string;
      arguments?: unknown;
      args?: unknown;
    }>;
  };

  const full = payload.answer;
  const toolCalls = (payload.tool_calls ?? []).map((call, index) => ({
    id: call.id ?? null,
    name: call.name ?? call.tool_name ?? `tool_${index + 1}`,
    arguments: call.arguments ?? call.args ?? {}
  }));

  for (let i = 0; i < full.length; i += 6) {
    await new Promise((r) => setTimeout(r, 24));
    onChunk(full.slice(i, i + 6));
  }

  return toolCalls;
}
