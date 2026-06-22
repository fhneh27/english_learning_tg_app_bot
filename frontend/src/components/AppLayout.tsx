import { memo, ReactNode, useRef } from "react";
import { AnimatePresence, motion } from "framer-motion";

import BottomNav, { AppTab } from "./BottomNav";
import { useGsapAmbientBackground, useGsapTapFeedback } from "../hooks/useGsapMotion";
import { pageVariants, springSnappy } from "../lib/motion";
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

      <div className="app-topbar">
        <motion.button
          type="button"
          className={activeTab === "settings" ? "app-settings-button active" : "app-settings-button"}
          onClick={() => onTabChange("settings")}
          aria-label="Settings"
          whileTap={{ scale: 0.88 }}
          transition={springSnappy}
        >
          <svg className="tabbar-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <circle
              cx="12"
              cy="12"
              r="3.1"
              stroke="currentColor"
              strokeWidth="1.8"
              fill={activeTab === "settings" ? "currentColor" : "none"}
              fillOpacity={activeTab === "settings" ? 0.14 : 0}
            />
            <path
              d="M12 3.4v2.2M12 18.4v2.2M20.6 12h-2.2M5.6 12H3.4M18.08 5.92l-1.56 1.56M7.48 16.52l-1.56 1.56M18.08 18.08l-1.56-1.56M7.48 7.48 5.92 5.92"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
            />
          </svg>
        </motion.button>
      </div>
    </div>
  );
}

export default memo(AppLayout);
