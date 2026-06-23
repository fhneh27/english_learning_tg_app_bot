import { useEffect } from "react";

export function useBodyScrollLock(active: boolean): void {
  useEffect(() => {
    if (!active) {
      return;
    }

    const html = document.documentElement;
    const body = document.body;
    const appFrame = document.querySelector<HTMLElement>(".app-frame");

    const previousHtmlOverflow = html.style.overflow;
    const previousBodyOverflow = body.style.overflow;
    const previousFrameOverflow = appFrame?.style.overflow ?? "";

    html.style.overflow = "hidden";
    body.style.overflow = "hidden";
    if (appFrame) {
      appFrame.style.overflow = "hidden";
    }

    return () => {
      html.style.overflow = previousHtmlOverflow;
      body.style.overflow = previousBodyOverflow;
      if (appFrame) {
        appFrame.style.overflow = previousFrameOverflow;
      }
    };
  }, [active]);
}
