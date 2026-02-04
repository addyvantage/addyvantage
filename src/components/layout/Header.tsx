'use client';

import { cn } from '@/lib/utils';
import { useScrollProgress } from '@/hooks/useScrollProgress';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
import { Container } from './Container';

export function Header() {
  const isScrolled = useScrollProgress(20);

  return (
    <header
      className={cn(
        'fixed top-0 left-0 right-0 z-50',
        'transition-colors duration-300',
        isScrolled
          ? 'bg-[var(--color-surface)]/90 border-b border-[var(--color-text)]/5'
          : 'bg-transparent'
      )}
    >
      <Container className="flex h-14 items-center justify-between">
        <a
          href="/"
          className="text-xs font-medium text-[var(--color-text-muted)] opacity-60 hover:opacity-100 transition-all duration-300"
        >
          Aditya Singh
        </a>
        <nav className="flex items-center gap-6">
          <a
            href="/play"
            className="text-sm text-[var(--color-text-muted)] hover:text-[var(--color-text)] transition-colors duration-200"
          >
            Play
          </a>
          <ThemeToggle />
        </nav>
      </Container>
    </header>
  );
}
