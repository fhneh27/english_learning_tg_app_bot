import type { Transition, Variants } from "framer-motion";

/**
 * Shared Framer Motion variants and transitions for the premium redesign.
 * Centralized so every screen and component stays visually consistent.
 */

export const springSnappy: Transition = {
  type: "spring",
  stiffness: 520,
  damping: 34,
  mass: 0.8,
};

export const springSoft: Transition = {
  type: "spring",
  stiffness: 320,
  damping: 30,
};

/** Page / screen transition: opacity + y: 20 -> 0 over ~0.3s. */
export const pageVariants: Variants = {
  initial: { opacity: 0, y: 20 },
  animate: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.3, ease: [0.22, 0.9, 0.3, 1] },
  },
  exit: {
    opacity: 0,
    y: -12,
    transition: { duration: 0.2, ease: [0.4, 0, 0.6, 1] },
  },
};

/** Container that staggers its children on mount. */
export const listContainer: Variants = {
  hidden: { opacity: 1 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.05, delayChildren: 0.05 },
  },
};

/** Individual list item entrance. */
export const listItem: Variants = {
  hidden: { opacity: 0, y: 16 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.32, ease: [0.22, 0.9, 0.3, 1] },
  },
};

/** Interactive card hover / tap feedback. */
export const cardHover = { scale: 1.02 } as const;
export const cardTap = { scale: 0.98 } as const;
