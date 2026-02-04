'use client';

import { GlassPanel } from '@/components/ui/GlassPanel';

interface GameLoaderProps {
  gameName: string;
}

export function GameLoader({ gameName }: GameLoaderProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-[var(--color-surface)]">
      <GlassPanel className="p-8 text-center">
        <h2 className="text-xl font-semibold text-[var(--color-text)]">
          {gameName}
        </h2>
        <p className="mt-2 text-sm text-[var(--color-text-muted)]">Loading...</p>
      </GlassPanel>
    </div>
  );
}
