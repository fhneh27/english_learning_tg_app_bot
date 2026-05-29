import { ReactNode } from "react";

type BadgeTone = "neutral" | "status" | "source" | "success";

type BadgeProps = {
  children: ReactNode;
  tone?: BadgeTone;
};

function Badge({ children, tone = "neutral" }: BadgeProps) {
  return <span className={`badge badge-${tone}`}>{children}</span>;
}

export default Badge;
