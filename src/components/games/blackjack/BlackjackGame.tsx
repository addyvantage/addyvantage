'use client';

import { useState } from 'react';
import { GameShell } from '@/components/games/GameShell';
import { GameStart } from '@/components/games/GameStart';
import { GlassPanel } from '@/components/ui/GlassPanel';

export function BlackjackGame() {
  const [hasStarted, setHasStarted] = useState(false);

  if (!hasStarted) {
    return (
      <GameStart
        gameName="Blackjack"
        description="Classic card game. Try to get as close to 21 as possible without going over."
        onStart={() => setHasStarted(true)}
      />
    );
  }

  return (
    <GameShell title="Blackjack">
      <div className="flex h-full items-center justify-center">
        <GlassPanel className="p-8 text-center max-w-sm">
          <h2 className="text-xl font-semibold text-[var(--color-text)]">
            Coming Soon
          </h2>
          <p className="mt-3 text-sm text-[var(--color-text-muted)]">
            Full Blackjack game with physical card animations is being built.
          </p>
        </GlassPanel>
      </div>
    </GameShell>
  );
}
