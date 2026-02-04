import { cn } from '@/lib/utils';

interface GlassPanelProps {
  children: React.ReactNode;
  className?: string;
}

export function GlassPanel({ children, className }: GlassPanelProps) {
  return (
    <div
      className={cn(
        'bg-[var(--color-surface)]/80',
        'backdrop-blur-[4px]',
        'border border-[var(--color-text)]/5',
        'rounded-xl',
        className
      )}
    >
      {children}
    </div>
  );
}
