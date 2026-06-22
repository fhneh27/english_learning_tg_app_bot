import { memo, ReactNode, useRef } from "react";
import { AnimatePresence, motion } from "framer-motion";

import BottomNav, { AppTab } from "./BottomNav";
import { useGsapAmbientBackground, useGsapTapFeedback } from "../hooks/useGsapMotion";
import { pageVariants } from "../lib/motion";
import { StreakVisualTier } from "../utils/streak";

type AppLayoutProps = {
  activeTab: AppTab;
  children: ReactNode;
  onTabChange: (tab: AppTab) => void;
  streakCount: number;
  streakTier: StreakVisualTier;
};

function AppLayout({ activeTab, children, onTabChange, streakCount }: AppLayoutProps) {
  const frameRef = useRef<HTMLDivElement>(null);
  const ambientRef = useRef<HTMLDivElement>(null);

  useGsapAmbientBackground(ambientRef, []);
  useGsapTapFeedback(frameRef, [activeTab]);

  return (
    <div className="app-frame" ref={frameRef}>
      <div className="app-ambient" aria-hidden="true" ref={ambientRef}>
        <span className="app-ambient-mesh" />
        <span className="app-ambient-flow app-ambient-flow-a" />
        <span className="app-ambient-flow app-ambient-flow-b" />
        <span className="app-ambient-flow app-ambient-flow-c" />
        <span className="app-ambient-glint app-ambient-glint-one" />
        <span className="app-ambient-glint app-ambient-glint-two" />
        <span className="app-ambient-vignette" />
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

      <AnimatePresence mode="wait">
        <motion.main
          key={activeTab}
          className="app-shell"
          variants={pageVariants}
          initial="initial"
          animate="animate"
          exit="exit"
        >
          {children}
        </motion.main>
      </AnimatePresence>

      <BottomNav activeTab={activeTab} onTabChange={onTabChange} streakCount={streakCount} />
    </div>
  );
}

function SettingsIcon() {
  return (
    <svg className="app-settings-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="3.1" stroke="currentColor" strokeWidth="1.8" />
      <path
        d="M12 2.6v2.6M12 18.8v2.6M21.4 12h-2.6M5.2 12H2.6M18.64 5.36l-1.84 1.84M7.2 16.8l-1.84 1.84M18.64 18.64 16.8 16.8M7.2 7.2 5.36 5.36"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
    </svg>
  );
}

export default memo(AppLayout);
