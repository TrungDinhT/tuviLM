'use client';

import { useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import { AppHeader } from './app-header';
import { Sidebar } from './sidebar';
import { BottomTabBar } from './bottom-tab-bar';

const SIDEBAR_STATE_KEY = 'sidebar:collapsed';

function getStoredCollapsed(): boolean {
  if (typeof window === 'undefined') return false;
  try {
    const raw = window.localStorage.getItem(SIDEBAR_STATE_KEY);
    return raw === 'true';
  } catch {
    return false;
  }
}

function setStoredCollapsed(value: boolean) {
  try {
    window.localStorage.setItem(SIDEBAR_STATE_KEY, String(value));
  } catch {
    // storage not available
  }
}

export function AppShell({ children }: { children: ReactNode }) {
  const [collapsed, setCollapsed] = useState(getStoredCollapsed);

  useEffect(() => {
    setStoredCollapsed(collapsed);
  }, [collapsed]);

  return (
    <div className="flex h-screen w-full overflow-hidden bg-muted/40">
      <Sidebar collapsed={collapsed} />
      <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
        <div className="sticky top-0 z-50">
          <AppHeader collapsed={collapsed} onToggleSidebar={() => setCollapsed((v) => !v)} />
        </div>
        <main className="flex-1 overflow-y-auto">{children}</main>
        <BottomTabBar />
      </div>
    </div>
  );
}
