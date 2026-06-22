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
        d="M4 11.4 12 4.5l8 6.9"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M5.8 10v8.2a1.3 1.3 0 0 0 1.3 1.3h9.8a1.3 1.3 0 0 0 1.3-1.3V10"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill={active ? "currentColor" : "none"}
        fillOpacity={active ? 0.14 : 0}
      />
      <path d="M9.7 19.5V14a1 1 0 0 1 1-1h2.6a1 1 0 0 1 1 1v5.5" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
    </svg>
  );
}

function WordsIcon({ active }: { active: boolean }) {
  return (
    <svg className="tabbar-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M12 6.6C10.4 5.1 8.3 4.5 5.4 4.5v13c2.9 0 5 .6 6.6 2.1 1.6-1.5 3.7-2.1 6.6-2.1v-13c-2.9 0-5 .6-6.6 2.1Z"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinejoin="round"
        fill={active ? "currentColor" : "none"}
        fillOpacity={active ? 0.14 : 0}
      />
      <path d="M12 6.6v13" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function MediaIcon({ active }: { active: boolean }) {
  return (
    <svg className="tabbar-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect
        x="3.5"
        y="5.5"
        width="17"
        height="13"
        rx="3.2"
        stroke="currentColor"
        strokeWidth="1.8"
        fill={active ? "currentColor" : "none"}
        fillOpacity={active ? 0.14 : 0}
      />
      <path d="M10.5 9.6 14.8 12l-4.3 2.4z" fill="currentColor" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" />
    </svg>
  );
}

function MusicIcon({ active }: { active: boolean }) {
  return (
    <svg className="tabbar-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M9 17.5V6.6l9.5-2v10.4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
      <ellipse cx="6.7" cy="17.6" rx="2.3" ry="2" fill={active ? "currentColor" : "none"} fillOpacity={active ? 0.18 : 0} stroke="currentColor" strokeWidth="1.8" />
      <ellipse cx="16.2" cy="15.6" rx="2.3" ry="2" fill={active ? "currentColor" : "none"} fillOpacity={active ? 0.18 : 0} stroke="currentColor" strokeWidth="1.8" />
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
