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
        { autoAlpha: 0, y: 14, scale: 0.992 },
        {
          autoAlpha: 1,
          y: 0,
          scale: 1,
          duration: 0.42,
          ease: "power3.out",
          stagger: { each: 0.026, from: "start" },
          clearProps: "opacity,visibility,transform",
        }
      );
    },
    { scope, dependencies, revertOnUpdate: true }
  );
}

export function useGsapAmbientBackground(scope: RefObject<HTMLElement>, dependencies: unknown[] = []) {
  useGSAP(
    () => {
      if (prefersReducedMotion()) {
        return;
      }

      const root = scope.current;
      if (!root) {
        return;
      }

      const flowA = root.querySelector<HTMLElement>(".app-ambient-flow-a");
      const flowB = root.querySelector<HTMLElement>(".app-ambient-flow-b");
      const flowC = root.querySelector<HTMLElement>(".app-ambient-flow-c");
      const mesh = root.querySelector<HTMLElement>(".app-ambient-mesh");
      const glints = scopedTargets(root, ".app-ambient-glint");
      const tweens: gsap.core.Tween[] = [];

      if (flowA) {
        tweens.push(
          gsap.to(flowA, {
            x: 28,
            y: -34,
            scale: 1.1,
            rotation: 4,
            duration: 12,
            ease: "sine.inOut",
            repeat: -1,
            yoyo: true,
          })
        );
      }

      if (flowB) {
        tweens.push(
          gsap.to(flowB, {
            x: -24,
            y: 30,
            scale: 1.08,
            rotation: -5,
            duration: 14,
            ease: "sine.inOut",
            repeat: -1,
            yoyo: true,
          })
        );
      }

      if (flowC) {
        tweens.push(
          gsap.to(flowC, {
            x: 18,
            y: 24,
            scale: 1.12,
            rotation: 3,
            duration: 16,
            ease: "sine.inOut",
            repeat: -1,
            yoyo: true,
          })
        );
      }

      if (mesh) {
        tweens.push(
          gsap.to(mesh, {
            x: -18,
            y: 14,
            duration: 18,
            ease: "sine.inOut",
            repeat: -1,
            yoyo: true,
          })
        );
      }

      if (glints.length > 0) {
        tweens.push(
          gsap.to(glints, {
            autoAlpha: 0.65,
            y: -12,
            duration: 2.8,
            ease: "sine.inOut",
            stagger: { each: 0.7, repeat: -1, yoyo: true },
          })
        );
      }

      return () => {
        tweens.forEach((tween) => tween.kill());
      };
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

export function useGsapStreakReveal(scope: RefObject<HTMLElement>, dependencies: unknown[] = []) {
  useGSAP(
    () => {
      const root = scope.current;
      if (!root) {
        return;
      }

      const reduce = prefersReducedMotion();

      // Animated draw of the hero progress ring.
      const ring = root.querySelector<SVGCircleElement>(".streak-hero-ring-progress");
      if (ring) {
        const circ = Number(ring.dataset.circ) || 603.19;
        const pct = Math.max(0, Math.min(100, Number(ring.dataset.progress) || 0));
        const target = circ * (1 - pct / 100);

        if (reduce) {
          gsap.set(ring, { strokeDashoffset: target });
        } else {
          gsap.fromTo(
            ring,
            { strokeDashoffset: circ },
            { strokeDashoffset: target, duration: 1.25, ease: "power3.out", delay: 0.1 }
          );
        }
      }

      if (reduce) {
        return;
      }

      const center = root.querySelector<HTMLElement>(".streak-ring-center");
      if (center) {
        gsap.fromTo(
          center,
          { scale: 0.8, autoAlpha: 0 },
          {
            scale: 1,
            autoAlpha: 1,
            duration: 0.7,
            ease: "back.out(1.7)",
            delay: 0.12,
            clearProps: "transform,opacity,visibility",
          }
        );
      }

      const stats = scopedTargets(root, ".streak-stat-card");
      if (stats.length > 0) {
        gsap.fromTo(
          stats,
          { y: 18, autoAlpha: 0, scale: 0.97 },
          {
            y: 0,
            autoAlpha: 1,
            scale: 1,
            duration: 0.5,
            ease: "power3.out",
            stagger: 0.07,
            clearProps: "transform,opacity,visibility",
          }
        );
      }

      const dots = scopedTargets(root, ".streak-week-day");
      if (dots.length > 0) {
        gsap.fromTo(
          dots,
          { y: 10, autoAlpha: 0 },
          {
            y: 0,
            autoAlpha: 1,
            duration: 0.42,
            ease: "power2.out",
            stagger: 0.045,
            delay: 0.1,
            clearProps: "transform,opacity,visibility",
          }
        );
      }
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
        ".filter-chip",
        ".mode-option",
        ".destination-option",
        ".prompt-chip",
        ".recent-item",
        ".list-row-button",
        ".music-search-item",
        ".source-picker-row",
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
