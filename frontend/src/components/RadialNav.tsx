const APP_TABS = ["home", "words", "streak", "media", "music", "settings"] as const;

export type AppTab = (typeof APP_TABS)[number];

type RadialNavProps = {
  activeTab: AppTab;
  onTabChange: (tab: AppTab) => void;
  streakCount: number;
};

type OrbitTab = Exclude<AppTab, "streak" | "settings">;
type OrbitPosition = "top" | "right" | "bottom" | "left";

const TAB_META: Array<{
  tab: OrbitTab;
  label: string;
  position: OrbitPosition;
  accentClass: string;
  Icon: () => JSX.Element;
}> = [
  { tab: "words", label: "Words", position: "top", accentClass: "violet", Icon: WordsIcon },
  { tab: "media", label: "Media", position: "right", accentClass: "amber", Icon: MediaIcon },
  { tab: "music", label: "Music", position: "bottom", accentClass: "emerald", Icon: MusicIcon },
  { tab: "home", label: "Home", position: "left", accentClass: "cyan", Icon: HomeIcon },
];

function HomeIcon() {
  return (
    <svg className="radial-nav-segment-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M3.75 10.8L12 4l8.25 6.8v8.2a1.5 1.5 0 0 1-1.5 1.5h-4.5v-5.25h-4.5v5.25h-4.5a1.5 1.5 0 0 1-1.5-1.5v-8.2z"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function WordsIcon() {
  return (
    <svg className="radial-nav-segment-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M6 5.25A2.25 2.25 0 0 1 8.25 3h9.75v15H8.25A2.25 2.25 0 0 0 6 20.25V5.25zm0 0v15A2.25 2.25 0 0 1 3.75 18H6"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path d="M10 7.5h4.75M10 11h4.75" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
    </svg>
  );
}

function MediaIcon() {
  return (
    <svg className="radial-nav-segment-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect x="4" y="5" width="16" height="14" rx="3" stroke="currentColor" strokeWidth="1.7" />
      <path d="M8 5v14M16 5v14M4 9h16M4 15h16" stroke="currentColor" strokeWidth="1.4" opacity="0.8" />
    </svg>
  );
}

function MusicIcon() {
  return (
    <svg className="radial-nav-segment-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M15.5 5.5v9.2a2.8 2.8 0 1 1-1.6-2.54V7.5l6-1.7v7.4a2.8 2.8 0 1 1-1.6-2.54V3.75L15.5 5.5z"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function RadialNav({ activeTab, onTabChange, streakCount }: RadialNavProps) {
  return (
    <nav className="radial-nav" aria-label="Primary navigation">
      <div className="radial-nav-container">
        <div className="radial-nav-shell radial-nav-shell-outer" aria-hidden="true" />
        <div className="radial-nav-shell radial-nav-shell-inner" aria-hidden="true" />
        <div className="radial-nav-core-shadow" aria-hidden="true" />

        <button
          type="button"
          className={activeTab === "streak" ? "radial-nav-center active" : "radial-nav-center"}
          onClick={() => onTabChange("streak")}
          aria-label={`Streak - ${streakCount} days`}
          aria-current={activeTab === "streak" ? "page" : undefined}
        >
          <div className="radial-nav-center-glow" />
          <div className="radial-nav-center-inner">
            <span className="radial-nav-center-emoji" aria-hidden="true">🔥</span>
            <span className="radial-nav-center-value">{streakCount}</span>
            <span className="radial-nav-center-label">Streak</span>
          </div>
        </button>

        {TAB_META.map(({ tab, label, position, accentClass, Icon }) => {
          const isActive = tab === activeTab;

          return (
            <button
              key={tab}
              type="button"
              data-position={position}
              className={isActive ? `radial-nav-segment ${accentClass} active` : `radial-nav-segment ${accentClass}`}
              onClick={() => onTabChange(tab)}
              aria-label={label}
              aria-current={isActive ? "page" : undefined}
            >
              <span className="radial-nav-segment-accent" aria-hidden="true" />
              <span className="radial-nav-segment-inner">
                <Icon />
                <span className="radial-nav-segment-label">{label}</span>
              </span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}

export default RadialNav;
