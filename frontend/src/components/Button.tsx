import { ButtonHTMLAttributes, ReactNode } from "react";
import { motion } from "framer-motion";

import { springSnappy } from "../lib/motion";

type ButtonVariant = "primary" | "secondary" | "ghost";

type ButtonProps = Omit<
  ButtonHTMLAttributes<HTMLButtonElement>,
  "onAnimationStart" | "onAnimationEnd" | "onAnimationIteration" | "onDrag" | "onDragStart" | "onDragEnd"
> & {
  children: ReactNode;
  isLoading?: boolean;
  variant?: ButtonVariant;
};

function Button({ children, className = "", isLoading = false, variant = "primary", ...props }: ButtonProps) {
  const classes = ["button", `button-${variant}`, className].filter(Boolean).join(" ");
  const disabled = props.disabled || isLoading;

  return (
    <motion.button
      {...props}
      className={classes}
      disabled={disabled}
      whileTap={disabled ? undefined : { scale: 0.97 }}
      transition={springSnappy}
    >
      <span className="button-shimmer" aria-hidden="true" />
      <span className="button-label">{isLoading ? "Please wait..." : children}</span>
    </motion.button>
  );
}

export default Button;
