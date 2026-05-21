'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { History, Sparkles, User } from 'lucide-react';
import { cn } from '@/lib/utils';

const TABS = [
  { href: '/chat', label: 'Đọc', icon: Sparkles },
  { href: '/history', label: 'Lưu', icon: History },
  { href: '/', label: 'Hồ sơ', icon: User },
] as const;

export function BottomTabBar() {
  const pathname = usePathname();

  return (
    <nav className="sticky bottom-0 inset-x-0 z-30 border-t border-border bg-background lg:hidden">
      <ul className="flex items-stretch">
        {TABS.map((tab) => {
          const active =
            tab.href === '/' ? pathname === '/' : pathname === tab.href || pathname.startsWith(`${tab.href}/`);
          const Icon = tab.icon;
          return (
            <li key={tab.href} className="flex-1">
              <Link
                href={tab.href}
                className={cn(
                  'flex flex-col items-center gap-1 py-3 text-[11px]',
                  active ? 'text-foreground' : 'text-muted-foreground hover:text-foreground',
                )}
              >
                <Icon className="size-4" />
                {tab.label}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
