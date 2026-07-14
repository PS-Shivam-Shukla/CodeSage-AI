import type { ReactNode } from 'react';
import { Sidebar } from '@/components/Sidebar';
import { Topbar } from '@/components/Topbar';
import { StatusFooter } from '@/components/StatusFooter';

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="font-body-md text-on-surface">
      {/* Fixed left sidebar */}
      <Sidebar />

      {/* Fixed top header — sits to the right of the sidebar */}
      <Topbar />

      {/* Scrollable main content */}
      <main
        className="ml-sidebar-width pt-16 pb-8 min-h-screen"
        style={{ width: 'calc(100% - 280px)' }}
      >
        <div className="px-gutter py-stack-lg max-w-[1440px] mx-auto">
          {children}
        </div>
      </main>

      {/* Fixed status bar at the bottom */}
      <StatusFooter />
    </div>
  );
}
