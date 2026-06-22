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

export default memo(AppLayout);
