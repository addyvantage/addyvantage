'use client';

import { GlassPanel } from '@/components/ui/GlassPanel';

interface GameStartProps {
  gameName: string;
  description?: string;
  onStart: () => void;
}

export function GameStart({ gameName, description, onStart }: GameStartProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-[var(--color-surface)]">
      <GlassPanel className="p-8 text-center max-w-sm mx-4">
        <h2 className="text-2xl font-semibold text-[var(--color-text)]">
          {gameName}
        </h2>
        {description && (
          <p className="mt-3 text-sm text-[var(--color-text-muted)]">
            {description}
          </p>
        )}
        <button
          onClick={onStart}
          className="mt-6 px-8 py-3 bg-[var(--color-text)] text-[var(--color-surface)] rounded-full text-sm font-medium hover:opacity-90 transition-opacity duration-200"
        >
          Start Game
        </button>
      </GlassPanel>
    </div>
  );
}
