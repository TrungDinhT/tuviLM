import type { ReactNode } from 'react';
import { AppHeader } from './app-header';
import { Sidebar } from './sidebar';
import { BottomTabBar } from './bottom-tab-bar';

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="flex h-screen w-full overflow-hidden bg-muted/40">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
        <div className="sticky top-0 z-50">
          <AppHeader />
        </div>
        <main className="flex-1 overflow-y-auto">{children}</main>
        <BottomTabBar />
      </div>
    </div>
  );
}
