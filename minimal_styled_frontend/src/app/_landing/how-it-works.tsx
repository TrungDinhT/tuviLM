import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const STEPS = [
  {
    n: '1',
    title: 'Nhập ngày, giờ sinh',
    body: 'Chỉ cần ngày dương lịch, giờ sinh (giờ nguyên) và giới tính. Vài giây là xong.',
  },
  {
    n: '2',
    title: 'AI an lá số 12 cung',
    body: 'Hệ thống xác định bản mệnh, cục mệnh, đại hạn và đặt sao vào 12 cung.',
  },
  {
    n: '3',
    title: 'Hỏi đáp & lưu trữ',
    body: 'Trò chuyện tự nhiên với AI về sự nghiệp, tình duyên, tài lộc. Lưu lại để xem lại.',
  },
] as const;

export function HowItWorks() {
  return (
    <section className="flex flex-col gap-4">
      <div className="flex flex-col gap-1">
        <h2 className="font-heading text-xl leading-tight font-medium">Quy trình</h2>
        <p className="text-sm text-muted-foreground">Ba bước, không cần kiến thức nền.</p>
      </div>
      <div className="grid gap-3 sm:grid-cols-3">
        {STEPS.map((step) => (
          <Card key={step.n} size="sm">
            <CardHeader className="flex-row items-center gap-2">
              <span className="flex size-7 items-center justify-center rounded-full bg-primary text-sm font-medium text-primary-foreground">
                {step.n}
              </span>
              <CardTitle className="text-sm">{step.title}</CardTitle>
            </CardHeader>
            <CardContent className="text-xs text-muted-foreground">{step.body}</CardContent>
          </Card>
        ))}
      </div>
    </section>
  );
}
