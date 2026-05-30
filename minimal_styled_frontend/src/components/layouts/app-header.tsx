'use client';

import { usePathname } from 'next/navigation';
import { PanelLeft, PanelLeftClose } from 'lucide-react';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { DEFAULT_HEADER, HEADER_CONFIG } from '@/config/header';
import { useChartStore } from '@/store/chart-store';

interface AppHeaderProps {
  collapsed: boolean;
  onToggleSidebar: () => void;
}

export function AppHeader({ collapsed, onToggleSidebar }: AppHeaderProps) {
  const pathname = usePathname();
  const selected = useChartStore((s) => s.selectedCungPosition);
  const current = useChartStore((s) => s.current);
  const selectedRole = selected && current ? current.cung_by_position[selected]?.role : null;

  const config = HEADER_CONFIG[pathname] ?? DEFAULT_HEADER;

  return (
    <header className="flex items-center justify-between gap-3 border-b border-border bg-background px-4 py-3 lg:px-6 lg:py-4">
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onToggleSidebar}
          title={collapsed ? 'Mở rộng sidebar' : 'Thu gọn sidebar'}
          className="flex size-8 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
        >
          {collapsed ? <PanelLeft className="size-5" /> : <PanelLeftClose className="size-5" />}
        </button>
        <Avatar>
          <AvatarFallback>T</AvatarFallback>
        </Avatar>
        <div>
          <div className="text-sm font-medium">{config.title}</div>
          <div className="text-xs text-muted-foreground">{config.subtitle}</div>
        </div>
      </div>
      {selected && (
        <Badge variant="secondary">
          {selected}
          {selectedRole && ` · ${selectedRole}`}
        </Badge>
      )}
    </header>
  );
}
