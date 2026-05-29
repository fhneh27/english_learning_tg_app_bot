const APP_TABS = ["home", "words", "streak", "media", "music", "settings"] as const;

export type AppTab = (typeof APP_TABS)[number];

type BottomNavProps = {
  activeTab: AppTab;
  onTabChange: (tab: AppTab) => void;
  streakCount: number;
};

const TAB_LABELS: Record<AppTab, string> = {
  home: "Home",
  words: "Words",
  streak: "Streak",
  media: "Media",
  music: "Music",
  settings: "Settings",
};

const LEFT_TABS: AppTab[] = ["home", "words"];
const RIGHT_TABS: AppTab[] = ["media", "music"];

/* ─── SVG Icons ─────────────────────────────────────────────────────── */

function HomeIcon({ active }: { active: boolean }) {
  return (
    <svg className="bottom-nav-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      {active ? (
        <path
          d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"
          fill="currentColor"
        />
      ) : (
        <path
          d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8zm2-18.1L19.1 9H18v9h-4v-6H10v6H6V9H4.9L12 1.9z"
          fill="currentColor"
          fillOpacity={0}
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinejoin="round"
        />
      )}
      {!active && (
        <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
      )}
    </svg>
  );
}

function WordsIcon({ active }: { active: boolean }) {
  return (
    <svg className="bottom-nav-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      {active ? (
        <path
          d="M18 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM9 4h2v5l-1-.75L9 9V4zm9 16H6V4h1v9l3-2.25L13 13V4h5v16z"
          fill="currentColor"
        />
      ) : (
        <path
          d="M18 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM9 4h2v5l-1-.75L9 9V4zm9 16H6V4h1v9l3-2.25L13 13V4h5v16z"
          fill="none"
          stroke="currentColor"
          strokeWidth="0.6"
        />
      )}
    </svg>
  );
}

function MediaIcon({ active }: { active: boolean }) {
  return (
    <svg className="bottom-nav-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      {active ? (
        <path
          d="M18 4l2 4h-3l-2-4h-2l2 4h-3l-2-4H8l2 4H7L5 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4h-4z"
          fill="currentColor"
        />
      ) : (
        <path
          d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 14.5v-9l6 4.5-6 4.5z"
          fill={active ? "currentColor" : "none"}
          stroke="currentColor"
          strokeWidth="1.6"
        />
      )}
    </svg>
  );
}

function SettingsIcon({ active }: { active: boolean }) {
  return (
    <svg className="bottom-nav-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54C14.46 2.18 14.25 2 14 2h-4c-.25 0-.46.18-.49.42l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58C4.53 11.34 4.5 11.67 4.5 12s.02.64.07.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.04.24.24.42.49.42h4c.25 0 .46-.18.49-.42l.36-2.54c.59-.24 1.13-.57 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"
        fill={active ? "currentColor" : "none"}
        stroke="currentColor"
        strokeWidth={active ? "0" : "0.4"}
      />
    </svg>
  );
}

function MusicIcon({ active }: { active: boolean }) {
  return (
    <svg className="bottom-nav-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M15.5 5.5v9.2a2.8 2.8 0 1 1-1.6-2.54V7.5l6-1.7v7.4a2.8 2.8 0 1 1-1.6-2.54V3.75L15.5 5.5z"
        fill={active ? "currentColor" : "none"}
        stroke="currentColor"
        strokeWidth={active ? "0.8" : "1.6"}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

const NAV_ICONS: Partial<Record<AppTab, (props: { active: boolean }) => JSX.Element>> = {
  home: HomeIcon,
  words: WordsIcon,
  media: MediaIcon,
  music: MusicIcon,
  settings: SettingsIcon,
};

/* ─── Component ─────────────────────────────────────────────────────── */

function BottomNav({ activeTab, onTabChange, streakCount }: BottomNavProps) {
  return (
    <nav className="bottom-nav" aria-label="Primary navigation">
      <div className="bottom-nav-side">
        {LEFT_TABS.map((tab) => {
          const Icon = NAV_ICONS[tab];
          const isActive = tab === activeTab;
          return (
            <button
              key={tab}
              type="button"
              className={isActive ? "bottom-nav-item active" : "bottom-nav-item"}
              onClick={() => onTabChange(tab)}
              aria-label={TAB_LABELS[tab]}
              aria-current={isActive ? "page" : undefined}
            >
              {Icon ? <Icon active={isActive} /> : null}
              <span className="bottom-nav-label">{TAB_LABELS[tab]}</span>
            </button>
          );
        })}
      </div>

      <button
        type="button"
        className={activeTab === "streak" ? "bottom-nav-center active" : "bottom-nav-center"}
        onClick={() => onTabChange("streak")}
        aria-label={`Streak — ${streakCount} days`}
        aria-current={activeTab === "streak" ? "page" : undefined}
      >
        <span className="bottom-nav-center-value">{streakCount}</span>
        <span className="bottom-nav-center-label">Streak</span>
      </button>

      <div className="bottom-nav-side" style={{ justifyItems: "center" }}>
        {RIGHT_TABS.map((tab) => {
          const Icon = NAV_ICONS[tab];
          const isActive = tab === activeTab;
          return (
            <button
              key={tab}
              type="button"
              className={isActive ? "bottom-nav-item active" : "bottom-nav-item"}
              onClick={() => onTabChange(tab)}
              aria-label={TAB_LABELS[tab]}
              aria-current={isActive ? "page" : undefined}
            >
              {Icon ? <Icon active={isActive} /> : null}
              <span className="bottom-nav-label">{TAB_LABELS[tab]}</span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}

export default BottomNav;
