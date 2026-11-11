import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ChatBubble } from "./chat-bubble";

describe("ChatBubble", () => {
  it("shows the current activity while the assistant is thinking", () => {
    render(
      <ChatBubble role="assistant" status="streaming" content="" activity="Đang tra cứu cách cục" />,
    );

    expect(screen.getByText("Đang tra cứu cách cục…")).toBeTruthy();
  });

  it("falls back to a thinking placeholder when no activity is set", () => {
    render(<ChatBubble role="assistant" status="streaming" content="" />);

    expect(screen.getByText("Thiên Hạc đang suy nghĩ…")).toBeTruthy();
  });

  it("renders assistant markdown as formatted elements", () => {
    const { container } = render(
      <ChatBubble role="assistant" status="confirmed" content={"**đậm** và *nghiêng*"} />,
    );

    expect(container.querySelector("strong")?.textContent).toBe("đậm");
    expect(container.querySelector("em")?.textContent).toBe("nghiêng");
  });

  it("renders a user message as plain text without markdown", () => {
    const { container } = render(
      <ChatBubble role="user" status="confirmed" content={"**không định dạng**"} />,
    );

    expect(container.querySelector("strong")).toBeNull();
    expect(screen.getByText("**không định dạng**")).toBeTruthy();
  });
});
