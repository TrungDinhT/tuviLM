import { BookOpen, History, Sparkles } from 'lucide-react';
import { Hero } from './_landing/hero';
import { HowItWorks } from './_landing/how-it-works';
import { BirthForm } from '@/features/birth-input/components/birth-form';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const FEATURES = [
  { icon: Sparkles, title: 'AI hiểu Tử Vi', body: 'Phân tích theo phái Bắc Tông – Tử Vi đẩu số.' },
  { icon: BookOpen, title: 'Tra cứu linh hoạt', body: 'Hỏi đáp tự nhiên về sự nghiệp, tình duyên, tài lộc.' },
  { icon: History, title: 'Lưu trữ', body: 'Mọi tra cứu được lưu để xem lại.' },
] as const;

export default function OnboardingPage() {
  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-10 px-4 py-6 lg:px-8 lg:py-10">
      {/* Above-the-fold: hero + form, side by side on desktop */}
      <div className="grid grid-cols-1 items-center gap-8 lg:min-h-[calc(100svh-5rem)] lg:grid-cols-2">
        <Hero />
        <div className="lg:w-full lg:max-w-xl lg:justify-self-end">
          <BirthForm />
        </div>
      </div>

      <HowItWorks />

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
  );
}
