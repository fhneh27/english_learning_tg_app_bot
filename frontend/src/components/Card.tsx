import { HTMLAttributes, ReactNode } from "react";

type CardProps = HTMLAttributes<HTMLElement> & {
  as?: "article" | "section" | "div";
  children: ReactNode;
};

function Card({ as = "section", children, className = "", ...props }: CardProps) {
  const Element = as;
  const classes = ["card", className].filter(Boolean).join(" ");

  return (
    <Element {...props} className={classes}>
      {children}
    </Element>
  );
}

export default Card;
