import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { Carousel, CarouselContent, CarouselDots, CarouselItem } from "./carousel";

function renderCarousel() {
  return render(
    <Carousel>
      <CarouselContent className="deck">
        <CarouselItem index={0} initialFocus={1}>
          <div>first</div>
        </CarouselItem>
        <CarouselItem index={1}>
          <div>second</div>
        </CarouselItem>
        <CarouselItem index={2}>
          <div>third</div>
        </CarouselItem>
      </CarouselContent>
      <CarouselDots count={3} className="deck-dots" />
    </Carousel>,
  );
}

describe("Carousel", () => {
  it("opens with the first item active and one dot per item", () => {
    const { container } = renderCarousel();

    const items = container.querySelectorAll('[aria-roledescription="slide"]');
    expect(items).toHaveLength(3);
    expect(items[0]?.className).toContain("is-active");
    expect(items[1]?.className).not.toContain("is-active");

    const dots = container.querySelectorAll(".deck-dots i");
    expect(dots).toHaveLength(3);
    expect(dots[0]?.className).toBe("on");
    expect(dots[1]?.className).toBe("");
  });

  it("gives every item its focus plumbing: initial var and a named view timeline", () => {
    const { container } = renderCarousel();

    const items = container.querySelectorAll<HTMLElement>('[aria-roledescription="slide"]');
    expect(items[0]?.style.getPropertyValue("--card-focus")).toBe("1");
    expect(items[1]?.style.getPropertyValue("--card-focus")).toBe("0");

    const timelines = [...items].map((item) => item.style.getPropertyValue("--card-tl"));
    expect(timelines.every((name) => name.startsWith("--tl-"))).toBe(true);
    expect(new Set(timelines).size).toBe(3);
  });
});
