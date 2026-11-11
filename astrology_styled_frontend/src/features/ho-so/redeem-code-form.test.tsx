import type { ReactNode } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { AccountRequestContext } from "@/lib/api/account-request";
import { useAccountAccess } from "@/lib/api/hooks";

import { RedeemCodeForm } from "./redeem-code-form";

vi.mock("@/lib/auth-client", () => ({
  authClient: {
    token: vi.fn().mockResolvedValue({
      data: { token: "header.eyJzdWIiOiJ1c2VyLTEifQ.signature" },
      error: null,
    }),
  },
}));

afterEach(() => vi.unstubAllGlobals());

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status });
}

function AccountBalance() {
  const access = useAccountAccess();
  return <output aria-label="Số dư">{access.data?.balance}</output>;
}

function renderForm() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return (
      <QueryClientProvider client={client}>
        <AccountRequestContext.Provider value={{ getSignal: () => undefined, userId: "user-1" }}>
          {children}
        </AccountRequestContext.Provider>
      </QueryClientProvider>
    );
  }
  render(
    <Wrapper>
      <AccountBalance />
      <RedeemCodeForm />
    </Wrapper>,
  );
}

describe("RedeemCodeForm", () => {
  it("normalizes the code and refetches the active account balance after success", async () => {
    let balance = 6;
    const fetchMock = vi.fn((_url: string, options?: RequestInit) => {
      if (options?.method === "POST") {
        balance += 30;
        return Promise.resolve(jsonResponse({ coins: 30 }));
      }
      return Promise.resolve(
        jsonResponse({ user_id: "user-1", role: "user", plan: "normal", balance }),
      );
    });
    vi.stubGlobal("fetch", fetchMock);
    renderForm();
    await screen.findByText("6");

    fireEvent.change(screen.getByLabelText("Mã ưu đãi"), { target: { value: " welcome " } });
    fireEvent.click(screen.getByRole("button", { name: "Nhận xu" }));

    await screen.findByText("Nhập mã thành công! Bạn nhận được 30 xu.");
    expect(screen.getByLabelText("Số dư").textContent).toBe("36");
    expect((screen.getByLabelText("Mã ưu đãi") as HTMLInputElement).value).toBe("");
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/account/redeem-code"),
      expect.objectContaining({ method: "POST", body: JSON.stringify({ code: "WELCOME" }) }),
    );
  });

  it("shows a Vietnamese failure and leaves the balance unchanged for an already-used code", async () => {
    const fetchMock = vi.fn((_url: string, options?: RequestInit) =>
      Promise.resolve(
        options?.method === "POST"
          ? jsonResponse({ detail: "Code already redeemed." }, 409)
          : jsonResponse({ user_id: "user-1", role: "user", plan: "normal", balance: 6 }),
      ),
    );
    vi.stubGlobal("fetch", fetchMock);
    renderForm();
    await screen.findByText("6");

    fireEvent.change(screen.getByLabelText("Mã ưu đãi"), { target: { value: "USED" } });
    fireEvent.click(screen.getByRole("button", { name: "Nhận xu" }));

    expect((await screen.findByRole("alert")).textContent).toBe(
      "Nhập mã thất bại. Mã này đã được sử dụng.",
    );
    expect(screen.getByLabelText("Số dư").textContent).toBe("6");
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });
});
