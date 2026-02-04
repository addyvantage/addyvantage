'use client';

import { MotionConfig as FramerMotionConfig } from 'framer-motion';

interface MotionConfigProps {
  children: React.ReactNode;
}

export function MotionConfig({ children }: MotionConfigProps) {
  return (
    <FramerMotionConfig reducedMotion="user">{children}</FramerMotionConfig>
  );
}
