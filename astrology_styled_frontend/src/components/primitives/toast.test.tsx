import { act, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { toast } from "sonner";

import { dismissToast, showToast } from "@/lib/toast";

import { Toast } from "./toast";

beforeEach(() => {
  dismissToast();
});

afterEach(() => {
  toast.dismiss();
});

describe("Toast", () => {
  it("keeps the styled message intact while Sonner animates it out", async () => {
    render(<Toast />);

    act(() => showToast("Vui lòng nhập tên hiển thị."));
    const message = await screen.findByText("Vui lòng nhập tên hiển thị.");

    expect(message.className).toContain("toast-surface");

    act(() => dismissToast());

    expect(screen.getByText("Vui lòng nhập tên hiển thị.")).toBeTruthy();
    await waitFor(() =>
      expect(message.closest("[data-sonner-toast]")?.getAttribute("data-removed")).toBe("true"),
    );
  });
});
