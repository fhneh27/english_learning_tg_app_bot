import { ButtonHTMLAttributes, ReactNode } from "react";

type ButtonVariant = "primary" | "secondary" | "ghost";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  children: ReactNode;
  isLoading?: boolean;
  variant?: ButtonVariant;
};

function Button({ children, className = "", isLoading = false, variant = "primary", ...props }: ButtonProps) {
  const classes = ["button", `button-${variant}`, className].filter(Boolean).join(" ");

  return (
    <button {...props} className={classes} disabled={props.disabled || isLoading}>
      {isLoading ? "Please wait..." : children}
    </button>
  );
}

export default Button;
