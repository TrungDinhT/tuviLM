'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Compass, Plus, Sparkles } from 'lucide-react';
import { ConversationSwitcher } from '@/features/chat-panel/components/conversation-switcher';
import { cn } from '@/lib/utils';

const NAV = [
  { href: '/chat', label: 'Đọc lá số', icon: Sparkles },
] as const;

interface SidebarProps {
  collapsed: boolean;
}

export function Sidebar({ collapsed }: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside
      className={cn(
        'sticky top-0 hidden h-screen shrink-0 flex-col gap-1 overflow-y-auto border-r border-border bg-sidebar text-sidebar-foreground transition-all duration-200 ease-linear lg:flex',
        collapsed ? 'w-16 items-center px-2 py-3' : 'w-60 p-3',
      )}
    >
      <Link
        href="/"
        className={cn(
          'flex items-center overflow-hidden py-3',
          collapsed ? 'justify-center gap-0 px-0' : 'gap-2 px-2',
        )}
      >
        <span className="flex size-7 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <Compass className="size-4" />
        </span>
        <span
          className={cn(
            'font-heading text-sm font-medium overflow-hidden whitespace-nowrap transition-[max-width,opacity] duration-200 ease-linear',
            collapsed ? 'max-w-0 opacity-0' : 'max-w-[200px] opacity-100',
          )}
        >
          Tử Vi AI
        </span>
      </Link>

      <nav className={cn('flex flex-col gap-1', collapsed && 'items-center')}>
        {NAV.map((item) => {
          const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              title={collapsed ? item.label : undefined}
              className={cn(
                'flex items-center overflow-hidden rounded-md py-1.5 text-sm transition-colors',
                collapsed ? 'justify-center gap-0 px-2' : 'gap-2 px-2',
                active
                  ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                  : 'text-muted-foreground hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground',
              )}
            >
              <Icon className="size-4 shrink-0" />
              <span
                className={cn(
                  'overflow-hidden whitespace-nowrap transition-[max-width,opacity] duration-200 ease-linear',
                  collapsed ? 'max-w-0 opacity-0' : 'max-w-[200px] opacity-100',
                )}
              >
                {item.label}
              </span>
            </Link>
          );
        })}
        {collapsed ? (
          <Link
            href="/"
            title="Lá số mới"
            className="flex items-center justify-center overflow-hidden rounded-md px-2 py-1.5 text-sm text-muted-foreground transition-colors hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground"
          >
            <Plus className="size-4 shrink-0" />
          </Link>
        ) : null}
      </nav>

      {!collapsed ? <ConversationSwitcher variant="sidebar" /> : null}
    </aside>
  );
}
