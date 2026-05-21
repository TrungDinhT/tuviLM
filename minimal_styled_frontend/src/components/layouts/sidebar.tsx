'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Compass, History, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';

const NAV = [
  { href: '/chat', label: 'Đọc lá số', icon: Sparkles },
  { href: '/history', label: 'Lịch sử', icon: History },
] as const;

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden w-60 shrink-0 flex-col gap-1 border-r border-border bg-sidebar p-3 text-sidebar-foreground lg:flex">
      <Link href="/" className="flex items-center gap-2 px-2 py-3">
        <span className="flex size-7 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <Compass className="size-4" />
        </span>
        <span className="font-heading text-sm font-medium">Tử Vi AI</span>
      </Link>

      <nav className="flex flex-col gap-1">
        {NAV.map((item) => {
          const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-2 rounded-md px-2 py-1.5 text-sm transition-colors',
                active
                  ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                  : 'text-muted-foreground hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground',
              )}
            >
              <Icon className="size-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
