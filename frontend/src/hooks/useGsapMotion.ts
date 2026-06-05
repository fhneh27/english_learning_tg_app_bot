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

      const targets = uniqueTargets([
        ...scopedTargets(scope.current, ".page-header"),
        ...scopedTargets(scope.current, ".hero-card"),
        ...scopedTargets(scope.current, ".card"),
        ...scopedTargets(scope.current, ".word-card"),
        ...scopedTargets(scope.current, ".media-card"),
        ...scopedTargets(scope.current, ".streak-page > *"),
      ]).filter((target) => !target.closest(".entry-modal, .source-picker-modal"));

      if (targets.length === 0) {
        return;
      }

      gsap.fromTo(
        targets,
        { autoAlpha: 0, y: 18, scale: 0.985 },
        {
          autoAlpha: 1,
          y: 0,
          scale: 1,
          duration: 0.48,
          ease: "power3.out",
          stagger: { each: 0.045, from: "start" },
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
      const activeItems = scopedTargets(scope.current, ".radial-nav-center.active, .radial-nav-segment.active");

      if (navItems.length > 0) {
        gsap.fromTo(
          navItems,
          { autoAlpha: 0, y: 12, scale: 0.96 },
          {
            autoAlpha: 1,
            y: 0,
            scale: 1,
            duration: 0.5,
            ease: "expo.out",
            stagger: 0.045,
            clearProps: "opacity,visibility,transform",
          }
        );
      }

      if (activeItems.length > 0) {
        gsap.fromTo(
          activeItems,
          { scale: 0.94 },
          {
            scale: 1,
            duration: 0.42,
            ease: "elastic.out(1, 0.72)",
            clearProps: "transform",
          }
        );
      }
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

      const targets = scopedTargets(
        scope.current,
        [
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
        ].join(", ")
      );

      const press = (event: PointerEvent) => {
        const target = event.currentTarget as HTMLElement;
        if (target.matches(":disabled")) {
          return;
        }
        gsap.to(target, { scale: 0.975, duration: 0.12, ease: "power2.out", overwrite: true });
      };

      const release = (event: PointerEvent) => {
        const target = event.currentTarget as HTMLElement;
        gsap.to(target, { scale: 1, duration: 0.22, ease: "power3.out", overwrite: true, clearProps: "transform" });
      };

      targets.forEach((target) => {
        target.addEventListener("pointerdown", press);
        target.addEventListener("pointerup", release);
        target.addEventListener("pointerleave", release);
        target.addEventListener("pointercancel", release);
      });

      return () => {
        targets.forEach((target) => {
          target.removeEventListener("pointerdown", press);
          target.removeEventListener("pointerup", release);
          target.removeEventListener("pointerleave", release);
          target.removeEventListener("pointercancel", release);
        });
      };
    },
    { scope, dependencies, revertOnUpdate: true }
  );
}
