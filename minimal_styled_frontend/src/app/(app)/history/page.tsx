import { HistoryList } from '@/features/chart-history/components/history-list';

export default function HistoryPage() {
  return (
    <div className="flex w-full flex-col gap-4 px-4 py-6 lg:px-12 lg:py-12">
      <div className="flex w-full max-w-3xl flex-col gap-1">
        <h1 className="font-heading text-lg font-medium">Lịch sử lá số</h1>
        <p className="text-xs text-muted-foreground">
          Tối đa 20 lá số gần nhất được lưu trên thiết bị của bạn.
        </p>
      </div>
      <div className="w-full max-w-3xl">
        <HistoryList />
      </div>
    </div>
  );
}
