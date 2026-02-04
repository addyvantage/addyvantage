'use client';

import dynamic from 'next/dynamic';
import { GameLoader } from './GameLoader';
import type { GameSlug } from '@/lib/games';

const BlackjackGame = dynamic(
  () =>
    import('./blackjack/BlackjackGame').then((mod) => mod.BlackjackGame),
  {
    ssr: false,
    loading: () => <GameLoader gameName="Blackjack" />,
  }
);

const games: Record<GameSlug, React.ComponentType> = {
  blackjack: BlackjackGame,
};

interface GameWrapperProps {
  gameSlug: GameSlug;
}

export function GameWrapper({ gameSlug }: GameWrapperProps) {
  const GameComponent = games[gameSlug];

  if (!GameComponent) {
    return (
      <div className="flex h-[100dvh] items-center justify-center">
        <p className="text-[var(--color-text-muted)]">Game not found</p>
      </div>
    );
  }

  return <GameComponent />;
}
