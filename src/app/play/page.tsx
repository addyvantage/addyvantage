import { Container } from '@/components/layout/Container';
import Link from 'next/link';

const games = [
  {
    slug: 'blackjack',
    title: 'Blackjack',
    description: 'Classic card game with physical, weighted animations.',
  },
];

export default function PlayPage() {
  return (
    <Container>
      <section className="py-[var(--space-section)]">
        <h1 className="text-display font-semibold tracking-tight text-[var(--color-text)]">
          Play
        </h1>
        <p className="mt-4 text-body text-[var(--color-text-muted)]">
          Games built with care. Motion that feels physical.
        </p>

        <div className="mt-12 space-y-4">
          {games.map((game) => (
            <Link
              key={game.slug}
              href={`/play/${game.slug}`}
              className="block group"
            >
              <div className="p-6 rounded-2xl border border-black/5 dark:border-white/10 hover:bg-black/[0.02] dark:hover:bg-white/[0.02] transition-colors duration-200">
                <h2 className="text-lg font-medium text-[var(--color-text)] group-hover:text-[var(--color-text)]">
                  {game.title}
                </h2>
                <p className="mt-1 text-sm text-[var(--color-text-muted)]">
                  {game.description}
                </p>
              </div>
            </Link>
          ))}
        </div>
      </section>
    </Container>
  );
}
