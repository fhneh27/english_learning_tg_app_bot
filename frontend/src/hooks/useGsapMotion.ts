import { RefObject } from "react";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";

gsap.registerPlugin(useGSAP);

function prefersReducedMotion(): boolean {
  return typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

function scopedTargets(scope: HTMLElement | null, selector: string): HTMLElement[] {
  if (!scope) {
    return [];
  }

  return Array.from(scope.querySelectorAll<HTMLElement>(selector));
}

function uniqueTargets(targets: HTMLElement[]): HTMLElement[] {
  return Array.from(new Set(targets));
}

export function useGsapScreenReveal(scope: RefObject<HTMLElement>, dependencies: unknown[] = []) {
  useGSAP(
    () => {
      if (prefersReducedMotion()) {
        return;
      }

      const root = scope.current;
      if (!root) {
        return;
      }

      const directChildren = Array.from(root.children).filter(
        (child): child is HTMLElement => child instanceof HTMLElement
      );
      const nestedChildren =
        directChildren.length === 1 && directChildren[0].classList.contains("streak-page")
          ? Array.from(directChildren[0].children).filter((child): child is HTMLElement => child instanceof HTMLElement)
          : [];
      const targets = uniqueTargets([...directChildren, ...nestedChildren])
        .filter((target) => !target.closest(".entry-modal, .source-picker-modal"))
        .slice(0, 10);

      if (targets.length === 0) {
        return;
      }

      gsap.fromTo(
        targets,
        { autoAlpha: 0, y: 12 },
        {
          autoAlpha: 1,
          y: 0,
          duration: 0.34,
          ease: "power3.out",
          stagger: { each: 0.026, from: "start" },
          clearProps: "opacity,visibility,transform",
        }
      );
    },
    { scope, dependencies, revertOnUpdate: true }
  );
}

export function useGsapRadialNav(scope: RefObject<HTMLElement>, dependencies: unknown[] = []) {
  useGSAP(
    () => {
      if (prefersReducedMotion()) {
        return;
      }

      const navItems = scopedTargets(scope.current, "[data-gsap-nav-item]");

      if (navItems.length > 0) {
        gsap.fromTo(
          navItems,
          { autoAlpha: 0, y: 8 },
          {
            autoAlpha: 1,
            y: 0,
            duration: 0.38,
            ease: "power3.out",
            stagger: 0.035,
            clearProps: "opacity,visibility,transform",
          }
        );
      }
    },
    { scope, dependencies, revertOnUpdate: true }
  );
}

export function useGsapActiveNav(scope: RefObject<HTMLElement>, dependencies: unknown[] = []) {
  useGSAP(
    () => {
      if (prefersReducedMotion()) {
        return;
      }

      const activeItems = scopedTargets(scope.current, ".radial-nav-center.active, .radial-nav-segment.active");
      if (activeItems.length === 0) {
        return;
      }

      gsap.fromTo(
        activeItems,
        { scale: 0.985 },
        {
          scale: 1,
          duration: 0.22,
          ease: "power2.out",
          clearProps: "transform",
        }
      );
    },
    { scope, dependencies, revertOnUpdate: true }
  );
}

export function useGsapModal(scope: RefObject<HTMLElement>, dependencies: unknown[] = []) {
  useGSAP(
    () => {
      if (prefersReducedMotion()) {
        return;
      }

      const modal = scope.current?.querySelector<HTMLElement>(".entry-modal, .source-picker-modal");
      const rows = scopedTargets(
        scope.current,
        ".entry-detail-grid > *, .example-item, .prompt-chip, .source-picker-row, .source-picker-selected"
      );

      if (scope.current) {
        gsap.fromTo(scope.current, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.18, ease: "power2.out" });
      }

      if (modal) {
        gsap.fromTo(
          modal,
          { y: 24, scale: 0.97, autoAlpha: 0 },
          {
            y: 0,
            scale: 1,
            autoAlpha: 1,
            duration: 0.34,
            ease: "power3.out",
            clearProps: "opacity,visibility,transform",
          }
        );
      }

      if (rows.length > 0) {
        gsap.fromTo(
          rows,
          { autoAlpha: 0, y: 10 },
          {
            autoAlpha: 1,
            y: 0,
            duration: 0.32,
            ease: "power2.out",
            stagger: 0.025,
            clearProps: "opacity,visibility,transform",
          }
        );
      }
    },
    { scope, dependencies, revertOnUpdate: true }
  );
}

export function useGsapProgress(scope: RefObject<HTMLElement>, dependencies: unknown[] = []) {
  useGSAP(
    () => {
      if (prefersReducedMotion()) {
        return;
      }

      const bars = scopedTargets(
        scope.current,
        ".streak-progress-bar-fill, .streak-diamond-goal-fill, .progress-bar-fill"
      );

      if (bars.length === 0) {
        return;
      }

      gsap.set(bars, { transformOrigin: "left center" });
      gsap.fromTo(
        bars,
        { scaleX: 0 },
        {
          scaleX: 1,
          duration: 0.72,
          ease: "power3.out",
          stagger: 0.06,
          clearProps: "transform",
        }
      );
    },
    { scope, dependencies, revertOnUpdate: true }
  );
}

export function useGsapTapFeedback(scope: RefObject<HTMLElement>, dependencies: unknown[] = []) {
  useGSAP(
    () => {
      if (prefersReducedMotion()) {
        return;
      }

      const root = scope.current;
      if (!root) {
        return;
      }

      const selector = [
        ".button",
        ".filter-chip",
        ".mode-option",
        ".destination-option",
        ".prompt-chip",
        ".recent-item",
        ".list-row-button",
        ".music-search-item",
        ".source-picker-row",
        ".radial-nav-center",
        ".radial-nav-segment",
      ].join(", ");

      const findTarget = (event: PointerEvent): HTMLElement | null => {
        if (!(event.target instanceof Element)) {
          return null;
        }
        const target = event.target.closest<HTMLElement>(selector);
        if (!target || !root.contains(target) || target.matches(":disabled")) {
          return null;
        }
        return target;
      };

      const press = (event: PointerEvent) => {
        const target = findTarget(event);
        if (!target) {
          return;
        }
        gsap.to(target, { scale: 0.985, duration: 0.1, ease: "power2.out", overwrite: true });
      };

      const release = (event: PointerEvent) => {
        const target = findTarget(event);
        if (!target) {
          return;
        }
        gsap.to(target, { scale: 1, duration: 0.16, ease: "power2.out", overwrite: true, clearProps: "transform" });
      };

      root.addEventListener("pointerdown", press);
      root.addEventListener("pointerup", release);
      root.addEventListener("pointerleave", release);
      root.addEventListener("pointercancel", release);

      return () => {
        root.removeEventListener("pointerdown", press);
        root.removeEventListener("pointerup", release);
        root.removeEventListener("pointerleave", release);
        root.removeEventListener("pointercancel", release);
      };
    },
    { scope, dependencies, revertOnUpdate: true }
  );
}
