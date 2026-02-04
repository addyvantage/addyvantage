import type { Transition } from 'framer-motion';

// Motion presets - reserved for games and interactive elements
// The portfolio shell uses stillness-first approach

export const transitions = {
  // For game cards and interactive elements
  physical: {
    type: 'spring',
    stiffness: 300,
    damping: 30,
  },
  // For subtle UI feedback
  quick: {
    duration: 0.2,
    ease: [0.4, 0, 0.2, 1],
  },
} satisfies Record<string, Transition>;
