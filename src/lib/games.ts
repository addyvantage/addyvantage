// Game configuration - shared between server and client

export const GAME_SLUGS = ['blackjack'] as const;

export type GameSlug = (typeof GAME_SLUGS)[number];

export function isValidGame(slug: string): slug is GameSlug {
  return GAME_SLUGS.includes(slug as GameSlug);
}
