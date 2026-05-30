export type HeaderConfig = {
  title: string;
  subtitle: string;
};

export const HEADER_CONFIG: Record<string, HeaderConfig> = {
  '/chat': {
    title: 'Tử Vi AI',
    subtitle: 'Phiên đọc lá số',
  },
  '/history': {
    title: 'Lịch sử',
    subtitle: 'Các lá số đã lưu',
  },
};

export const DEFAULT_HEADER: HeaderConfig = {
  title: 'Tử Vi AI',
  subtitle: 'Phiên đọc lá số',
};
