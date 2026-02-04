import { notFound } from 'next/navigation';
import { GameWrapper } from '@/components/games/GameWrapper';
import { GAME_SLUGS, isValidGame } from '@/lib/games';

interface GamePageProps {
  params: Promise<{ game: string }>;
}

export default async function GamePage({ params }: GamePageProps) {
  const { game } = await params;

  if (!isValidGame(game)) {
    notFound();
  }

  return <GameWrapper gameSlug={game} />;
}

export function generateStaticParams() {
  return GAME_SLUGS.map((game) => ({ game }));
}
