import { HTMLAttributes, ReactNode } from "react";
import { motion } from "framer-motion";

import { cardHover, cardTap, springSoft } from "../lib/motion";

type CardProps = Omit<
  HTMLAttributes<HTMLElement>,
  "onAnimationStart" | "onAnimationEnd" | "onAnimationIteration" | "onDrag" | "onDragStart" | "onDragEnd"
> & {
  as?: "article" | "section" | "div";
  children: ReactNode;
  /** Disable hover/tap motion (e.g. for purely static surfaces). */
  interactive?: boolean;
};

function Card({ as = "section", children, className = "", interactive = true, ...props }: CardProps) {
  const MotionElement = motion[as];
  const classes = ["card", className].filter(Boolean).join(" ");

  return (
    <MotionElement
      {...props}
      className={classes}
      whileHover={interactive ? cardHover : undefined}
      whileTap={interactive ? cardTap : undefined}
      transition={springSoft}
    >
      <span className="card-accent-bar" aria-hidden="true" />
      {children}
    </MotionElement>
  );
}

export default Card;
