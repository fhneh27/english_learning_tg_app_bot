import { memo, ReactNode, useRef } from "react";

import RadialNav, { AppTab } from "./RadialNav";
import { useGsapScreenReveal, useGsapTapFeedback } from "../hooks/useGsapMotion";
import { StreakVisualTier } from "../utils/streak";

type AppLayoutProps = {
  activeTab: AppTab;
  children: ReactNode;
  onTabChange: (tab: AppTab) => void;
  streakCount: number;
  streakTier: StreakVisualTier;
};

function AppLayout({ activeTab, children, onTabChange, streakCount, streakTier }: AppLayoutProps) {
  const frameRef = useRef<HTMLDivElement>(null);
  const shellRef = useRef<HTMLElement>(null);

  useGsapScreenReveal(shellRef, [activeTab]);
  useGsapTapFeedback(frameRef, [activeTab, streakCount, streakTier]);

  return (
    <div className="app-frame" ref={frameRef}>
      <div className="app-ambient" aria-hidden="true">
        <span className="app-ambient-orb app-ambient-orb-cyan" />
        <span className="app-ambient-orb app-ambient-orb-fire" />
        <span className="app-ambient-orb app-ambient-orb-violet" />
      </div>
      <div className="app-topbar">
        <button
          type="button"
          className={activeTab === "settings" ? "app-settings-button active" : "app-settings-button"}
          onClick={() => onTabChange("settings")}
          aria-label="Open settings"
          aria-current={activeTab === "settings" ? "page" : undefined}
        >
          <SettingsIcon />
        </button>
      </div>
      <RadialNav activeTab={activeTab} onTabChange={onTabChange} streakCount={streakCount} streakTier={streakTier} />
      <main className="app-shell" ref={shellRef}>
        {children}
      </main>
    </div>
  );
}

function SettingsIcon() {
  return (
    <svg className="app-settings-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M12 8.25a3.75 3.75 0 1 1 0 7.5a3.75 3.75 0 0 1 0-7.5z"
        stroke="currentColor"
        strokeWidth="1.7"
      />
      <path
        d="M19.1 13.15a1.05 1.05 0 0 0 .2 1.16l.04.04a1.5 1.5 0 1 1-2.12 2.12l-.04-.04a1.05 1.05 0 0 0-1.16-.2a1.05 1.05 0 0 0-.63.96v.11a1.5 1.5 0 1 1-3 0v-.11a1.05 1.05 0 0 0-.69-.98a1.05 1.05 0 0 0-1.1.22l-.08.08a1.5 1.5 0 1 1-2.12-2.12l.08-.08a1.05 1.05 0 0 0 .22-1.1a1.05 1.05 0 0 0-.98-.69h-.11a1.5 1.5 0 1 1 0-3h.11a1.05 1.05 0 0 0 .96-.63a1.05 1.05 0 0 0-.2-1.16l-.04-.04a1.5 1.5 0 1 1 2.12-2.12l.04.04a1.05 1.05 0 0 0 1.16.2h.04a1.05 1.05 0 0 0 .59-.95v-.11a1.5 1.5 0 1 1 3 0v.11a1.05 1.05 0 0 0 .63.96a1.05 1.05 0 0 0 1.16-.2l.04-.04a1.5 1.5 0 1 1 2.12 2.12l-.04.04a1.05 1.05 0 0 0-.2 1.16v.04a1.05 1.05 0 0 0 .95.59h.11a1.5 1.5 0 1 1 0 3h-.11a1.05 1.05 0 0 0-.96.63z"
        stroke="currentColor"
        strokeWidth="1.3"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export default memo(AppLayout);
