'use client';

import { useEffect, useState } from 'react';

export function useReducedMotion(): boolean {
  // Default to true (reduced motion) during SSR for safety
  const [prefersReduced, setPrefersReduced] = useState(true);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReduced(mediaQuery.matches);

    const handler = (event: MediaQueryListEvent) => {
      setPrefersReduced(event.matches);
    };

    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  return prefersReduced;
}
