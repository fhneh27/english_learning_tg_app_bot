import { StreakVisualTier } from "../utils/streak";

type StreakTierMarkProps = {
  tier: StreakVisualTier;
  className?: string;
};

function StreakTierMark({ tier, className = "" }: StreakTierMarkProps) {
  if (tier === "diamond") {
    return (
      <span className={["streak-tier-mark streak-tier-mark-diamond", className].filter(Boolean).join(" ")} aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none">
          <path
            d="M12 3.5 4.5 9.25 12 20.5 19.5 9.25 12 3.5Z"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinejoin="round"
          />
          <path d="M4.5 9.25h15M8.25 9.25 12 3.5l3.75 5.75M9.75 9.25 12 20.5l2.25-11.25" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
        </svg>
      </span>
    );
  }

  if (tier === "ember") {
    return (
      <span className={["streak-tier-mark streak-tier-mark-ember", className].filter(Boolean).join(" ")} aria-hidden="true">
        🔥
      </span>
    );
  }

  return (
    <span className={["streak-tier-mark streak-tier-mark-none", className].filter(Boolean).join(" ")} aria-hidden="true">
      ✦
    </span>
  );
}

export default StreakTierMark;
