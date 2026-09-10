import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { AnSaoScreen } from "./an-sao-screen";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

vi.mock("@/lib/api/hooks", () => ({
  profileDisplayName: () => "01/01/2000",
  useBuildLaso: () => ({ mutateAsync: vi.fn() }),
  useCreateChartProfile: () => ({ mutateAsync: vi.fn() }),
  useLasoPreview: () => ({ data: undefined }),
}));

describe("AnSaoScreen hierarchy", () => {
  it("puts the primary action before the atmospheric reward in reading order", () => {
    render(<AnSaoScreen />);

    const action = screen.getByRole("button", { name: /Luận giải lá số của tôi/ });
    const reward = screen.getByText("CHÒM SAO MỆNH ĐANG NGỦ").parentElement;

    expect(reward).not.toBeNull();
    expect(action.compareDocumentPosition(reward as HTMLElement)).toBe(
      Node.DOCUMENT_POSITION_FOLLOWING,
    );
  });
});
