'use client';

import { useEffect, useState } from 'react';

export function useScrollProgress(threshold: number = 20): boolean {
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handler = () => {
      requestAnimationFrame(() => {
        setIsScrolled(window.scrollY > threshold);
      });
    };

    window.addEventListener('scroll', handler, { passive: true });
    return () => window.removeEventListener('scroll', handler);
  }, [threshold]);

  return isScrolled;
}
