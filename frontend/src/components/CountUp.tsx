import { useEffect, useRef, useState } from "react";
import { animate, useReducedMotion } from "framer-motion";

type CountUpProps = {
  value: number;
  duration?: number;
};

/**
 * Animates a number counting up to `value` when it mounts or changes.
 * Respects reduced-motion preferences by rendering the final value instantly.
 */
function CountUp({ value, duration = 0.9 }: CountUpProps) {
  const reduceMotion = useReducedMotion();
  const [display, setDisplay] = useState(reduceMotion ? value : 0);
  const previous = useRef(reduceMotion ? value : 0);

  useEffect(() => {
    if (reduceMotion) {
      setDisplay(value);
      previous.current = value;
      return;
    }

    const controls = animate(previous.current, value, {
      duration,
      ease: [0.22, 0.9, 0.3, 1],
      onUpdate: (latest) => setDisplay(Math.round(latest)),
      onComplete: () => {
        previous.current = value;
      },
    });

    return () => controls.stop();
  }, [value, duration, reduceMotion]);

  return <>{display}</>;
}

export default CountUp;
