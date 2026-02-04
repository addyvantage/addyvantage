'use client';

import { useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { GlassPanel } from '@/components/ui/GlassPanel';
import { cn } from '@/lib/utils';

interface GameShellProps {
  children: React.ReactNode;
  title: string;
  className?: string;
}

export function GameShell({ children, title, className }: GameShellProps) {
  const router = useRouter();

  const handleExit = useCallback(() => {
    router.push('/play');
  }, [router]);

  // Handle Escape key
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') handleExit();
    };

    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [handleExit]);

  return (
    <div
      className={cn(
        'fixed inset-0 z-50 bg-[var(--color-surface)]',
        'touch-none', // Prevent scroll on touch devices
        className
      )}
    >
      {/* Exit button */}
      <GlassPanel className="fixed top-4 left-4 z-50">
        <button
          onClick={handleExit}
          className="flex h-10 w-10 items-center justify-center text-[var(--color-text-muted)] hover:text-[var(--color-text)] transition-colors duration-200"
          aria-label="Exit game"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M18 6 6 18" />
            <path d="m6 6 12 12" />
          </svg>
        </button>
      </GlassPanel>

      {/* Game title */}
      <GlassPanel className="fixed top-4 right-4 z-50 px-4 py-2">
        <span className="text-sm font-medium text-[var(--color-text)]">
          {title}
        </span>
      </GlassPanel>

      {/* Game content */}
      {children}
    </div>
  );
}
