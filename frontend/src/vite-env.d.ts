/// <reference types="vite/client" />

type TelegramWebAppUser = {
  id: number;
  username?: string;
  first_name?: string;
};

type TelegramWebAppInitDataUnsafe = {
  user?: TelegramWebAppUser;
};

type TelegramWebApp = {
  initData?: string;
  initDataUnsafe?: TelegramWebAppInitDataUnsafe;
  ready: () => void;
  expand: () => void;
};

interface Window {
  Telegram?: {
    WebApp?: TelegramWebApp;
  };
}
