import { BookOpen, Compass, History, Sparkles } from 'lucide-react';
import { BirthForm } from '@/features/birth-input/components/birth-form';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const FEATURES = [
  { icon: Sparkles, title: 'AI hiểu Tử Vi', body: 'Phân tích theo phái Bắc Tông – Tử Vi đẩu số.' },
  { icon: BookOpen, title: 'Tra cứu linh hoạt', body: 'Hỏi đáp tự nhiên về sự nghiệp, tình duyên, tài lộc.' },
  { icon: History, title: 'Lưu trữ', body: 'Mọi tra cứu được lưu để xem lại.' },
] as const;

export default function OnboardingPage() {
  return (
    <div className="flex w-full flex-col items-center px-4 py-6 lg:px-12 lg:py-12">
      <div className="flex w-full max-w-2xl flex-col gap-4">
        <div className="flex items-center gap-2">
          <span className="flex size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <Compass className="size-4" />
          </span>
          <div>
            <div className="font-heading text-base leading-none font-medium">Tử Vi AI</div>
            <div className="mt-0.5 text-xs text-muted-foreground">An lá số bằng AI</div>
          </div>
        </div>

        <BirthForm />

        <div className="grid gap-3 sm:grid-cols-3">
          {FEATURES.map((f) => {
            const Icon = f.icon;
            return (
              <Card key={f.title} size="sm">
                <CardHeader className="flex-row items-center gap-2 [&_svg]:text-muted-foreground">
                  <Icon className="size-4" />
                  <CardTitle className="text-sm">{f.title}</CardTitle>
                </CardHeader>
                <CardContent className="text-xs text-muted-foreground">{f.body}</CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </div>
  );
}
