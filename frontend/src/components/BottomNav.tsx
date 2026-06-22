import { motion } from "framer-motion";

import CountUp from "./CountUp";
import { springSnappy } from "../lib/motion";

const APP_TABS = ["home", "words", "streak", "media", "music", "settings"] as const;

export type AppTab = (typeof APP_TABS)[number];

type BottomNavProps = {
  activeTab: AppTab;
  onTabChange: (tab: AppTab) => void;
  streakCount: number;
};

type NavTab = Exclude<AppTab, "streak" | "settings">;

const TAB_META: Array<{ tab: NavTab; label: string; Icon: (props: { active: boolean }) => JSX.Element }> = [
  { tab: "home", label: "Home", Icon: HomeIcon },
  { tab: "words", label: "Words", Icon: WordsIcon },
  { tab: "media", label: "Media", Icon: MediaIcon },
  { tab: "music", label: "Music", Icon: MusicIcon },
];

function HomeIcon({ active }: { active: boolean }) {
  return (
    <svg className="tabbar-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M3.75 10.8 12 4l8.25 6.8v8.2a1.5 1.5 0 0 1-1.5 1.5h-4.5v-5.25h-4.5v5.25h-4.5a1.5 1.5 0 0 1-1.5-1.5z"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinejoin="round"
        fill={active ? "currentColor" : "none"}
        fillOpacity={active ? 0.18 : 0}
      />
    </svg>
  );
}

function WordsIcon({ active }: { active: boolean }) {
  return (
    <svg className="tabbar-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M6 5.25A2.25 2.25 0 0 1 8.25 3H18v15H8.25A2.25 2.25 0 0 0 6 20.25z"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinejoin="round"
        fill={active ? "currentColor" : "none"}
        fillOpacity={active ? 0.18 : 0}
      />
      <path d="M10 7.5h4.75M10 11h4.75" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
    </svg>
  );
}

function MediaIcon({ active }: { active: boolean }) {
  return (
    <svg className="tabbar-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect
        x="4"
        y="5"
        width="16"
        height="14"
        rx="3"
        stroke="currentColor"
        strokeWidth="1.7"
        fill={active ? "currentColor" : "none"}
        fillOpacity={active ? 0.16 : 0}
      />
      <path d="M8 5v14M16 5v14M4 9h16M4 15h16" stroke="currentColor" strokeWidth="1.3" opacity="0.85" />
    </svg>
  );
}

function MusicIcon({ active }: { active: boolean }) {
  return (
    <svg className="tabbar-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M15.5 5.5v9.2a2.8 2.8 0 1 1-1.6-2.54V7.5l6-1.7v7.4a2.8 2.8 0 1 1-1.6-2.54V3.75z"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill={active ? "currentColor" : "none"}
        fillOpacity={active ? 0.16 : 0}
      />
    </svg>
  );
}

function TabButton({
  tab,
  label,
  Icon,
  active,
  onSelect,
}: {
  tab: NavTab;
  label: string;
  Icon: (props: { active: boolean }) => JSX.Element;
  active: boolean;
  onSelect: (tab: NavTab) => void;
}) {
  return (
    <motion.button
      type="button"
      className={active ? "tabbar-item active" : "tabbar-item"}
      onClick={() => onSelect(tab)}
      aria-label={label}
      aria-current={active ? "page" : undefined}
      whileTap={{ scale: 0.88 }}
      transition={springSnappy}
    >
      <span className="tabbar-icon-wrap">
        <Icon active={active} />
        {active ? <span className="tabbar-icon-glow" aria-hidden="true" /> : null}
      </span>
      <span className="tabbar-label">{label}</span>
      {active ? (
        <motion.span layoutId="tabbar-indicator" className="tabbar-indicator" transition={springSnappy} />
      ) : null}
    </motion.button>
  );
}

function BottomNav({ activeTab, onTabChange, streakCount }: BottomNavProps) {
  const streakActive = activeTab === "streak";

  return (
    <nav className="tabbar" aria-label="Primary navigation">
      <div className="tabbar-inner">
        <TabButton {...TAB_META[0]} active={activeTab === TAB_META[0].tab} onSelect={onTabChange} />
        <TabButton {...TAB_META[1]} active={activeTab === TAB_META[1].tab} onSelect={onTabChange} />

        <motion.button
          type="button"
          className={streakActive ? "tabbar-center active" : "tabbar-center"}
          onClick={() => onTabChange("streak")}
          aria-label={`Streak — ${streakCount} days`}
          aria-current={streakActive ? "page" : undefined}
          whileTap={{ scale: 0.9 }}
          transition={springSnappy}
        >
          <span className="tabbar-center-glow" aria-hidden="true" />
          <span className="tabbar-center-inner">
            <span className="tabbar-center-value">
              <CountUp value={streakCount} />
            </span>
            <span className="tabbar-center-label">Streak</span>
          </span>
        </motion.button>

        <TabButton {...TAB_META[2]} active={activeTab === TAB_META[2].tab} onSelect={onTabChange} />
        <TabButton {...TAB_META[3]} active={activeTab === TAB_META[3].tab} onSelect={onTabChange} />
      </div>
    </nav>
  );
}

export default BottomNav;
