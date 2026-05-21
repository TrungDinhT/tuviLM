import { Compass } from 'lucide-react';
import { HeroCta } from './hero-cta';

export function Hero() {
  return (
    <section className="flex flex-col gap-6 py-6 lg:gap-8 lg:py-12">
      <div className="flex items-center gap-2">
        <span className="flex size-9 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <Compass className="size-5" />
        </span>
        <div>
          <div className="font-heading text-base leading-none font-medium">Tử Vi AI</div>
          <div className="mt-0.5 text-xs text-muted-foreground">Luận lá số bằng AI</div>
        </div>
      </div>

      <div className="flex flex-col gap-3">
        <h1 className="font-heading text-3xl leading-tight font-medium lg:text-4xl">
          Luận lá số Tử Vi bằng AI
        </h1>
        <p className="max-w-md text-sm leading-relaxed text-muted-foreground lg:text-base">
          Nhập ngày, giờ sinh — AI an lá số 12 cung và luận giải tự nhiên như một thầy
          tử vi. Mọi cuộc trò chuyện được lưu lại để xem lại.
        </p>
      </div>

      <div className="flex items-center gap-3">
        <HeroCta />
        <span className="text-xs text-muted-foreground">Miễn phí · không cần đăng ký</span>
      </div>
    </section>
  );
}
