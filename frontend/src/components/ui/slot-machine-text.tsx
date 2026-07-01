"use client";

import { useEffect, useRef, useState } from "react";
import { motion, useInView } from "framer-motion";

import { cn } from "@/lib/utils";

type SlotMachineTextProps = {
  value: string;
  className?: string;
  duration?: number;
  maskClassName?: string;
};

type SlotMachineLabelProps = {
  value: string;
  className?: string;
  duration?: number;
  maskClassName?: string;
  baseDelay?: number;
  replayOnHover?: boolean;
  autoPlay?: boolean;
};

const UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");
const LOWER = "abcdefghijklmnopqrstuvwxyz".split("");

function buildDigitSequence(target: number, cycles = 3) {
  const sequence: string[] = [];
  for (let c = 0; c < cycles; c += 1) {
    for (let d = 0; d <= 9; d += 1) sequence.push(String(d));
  }
  for (let d = 0; d <= target; d += 1) sequence.push(String(d));
  return sequence;
}

function buildLetterSequence(char: string, cycles = 2) {
  if (char === " ") return [" "];

  const isUpper = char === char.toUpperCase() && char !== char.toLowerCase();
  const letters = isUpper ? UPPER : LOWER;
  const targetIdx = letters.indexOf(char);
  if (targetIdx === -1) return [char];

  const sequence: string[] = [];
  for (let c = 0; c < cycles; c += 1) sequence.push(...letters);
  for (let i = 0; i <= targetIdx; i += 1) sequence.push(letters[i]);
  return sequence;
}

function SlotReel({
  sequence,
  index,
  active,
  duration,
  maskClassName,
  widthClass = "w-[0.62em]",
}: {
  sequence: string[];
  index: number;
  active: boolean;
  duration: number;
  maskClassName?: string;
  widthClass?: string;
}) {
  return (
    <span className={cn("relative inline-block h-[1em] overflow-hidden align-bottom", widthClass)}>
      <span
        className={cn(
          "pointer-events-none absolute inset-x-0 top-0 z-10 h-1/3 bg-gradient-to-b to-transparent",
          maskClassName ?? "from-gray-950",
        )}
      />
      <span
        className={cn(
          "pointer-events-none absolute inset-x-0 bottom-0 z-10 h-1/3 bg-gradient-to-t to-transparent",
          maskClassName ?? "from-gray-950",
        )}
      />
      <motion.span
        className="flex flex-col items-center"
        initial={{ y: 0 }}
        animate={active ? { y: `-${sequence.length - 1}em` } : { y: 0 }}
        transition={{
          delay: index * 0.04,
          duration: duration + index * 0.06,
          ease: [0.12, 0.85, 0.22, 1],
        }}
      >
        {sequence.map((item, i) => (
          <span
            key={i}
            className={cn("flex h-[1em] items-center justify-center", widthClass)}
          >
            {item}
          </span>
        ))}
      </motion.span>
    </span>
  );
}

function SlotDigit({
  digit,
  index,
  active,
  duration,
  maskClassName,
}: {
  digit: string;
  index: number;
  active: boolean;
  duration: number;
  maskClassName?: string;
}) {
  const target = parseInt(digit, 10);
  const sequence = buildDigitSequence(target);

  return (
    <SlotReel
      sequence={sequence}
      index={index}
      active={active}
      duration={duration}
      maskClassName={maskClassName}
    />
  );
}

function SlotLetter({
  letter,
  index,
  active,
  duration,
  maskClassName,
}: {
  letter: string;
  index: number;
  active: boolean;
  duration: number;
  maskClassName?: string;
}) {
  const sequence = buildLetterSequence(letter);

  if (letter === " ") {
    return <span className="inline-block w-[0.28em]" aria-hidden>&nbsp;</span>;
  }

  return (
    <SlotReel
      sequence={sequence}
      index={index}
      active={active}
      duration={duration}
      maskClassName={maskClassName}
      widthClass="w-[0.58em]"
    />
  );
}

function SlotChar({
  char,
  index,
  active,
  duration,
  maskClassName,
}: {
  char: string;
  index: number;
  active: boolean;
  duration: number;
  maskClassName?: string;
}) {
  if (/\d/.test(char)) {
    return (
      <SlotDigit
        digit={char}
        index={index}
        active={active}
        duration={duration}
        maskClassName={maskClassName}
      />
    );
  }

  return (
    <motion.span
      initial={{ opacity: 0, y: 10 }}
      animate={active ? { opacity: 1, y: 0 } : {}}
      transition={{ delay: index * 0.05 + 0.35, duration: 0.35 }}
      className="inline-block"
    >
      {char}
    </motion.span>
  );
}

export function SlotMachineText({
  value,
  className,
  duration = 1.6,
  maskClassName,
}: SlotMachineTextProps) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, margin: "-50px" });
  const [active, setActive] = useState(false);

  useEffect(() => {
    if (inView) setActive(true);
  }, [inView]);

  return (
    <span
      ref={ref}
      className={cn("inline-flex items-end tabular-nums leading-none", className)}
      aria-label={value}
    >
      {value.split("").map((char, i) => (
        <SlotChar
          key={`${i}-${char}`}
          char={char}
          index={i}
          active={active}
          duration={duration}
          maskClassName={maskClassName}
        />
      ))}
    </span>
  );
}

export function SlotMachineLabel({
  value,
  className,
  duration = 0.85,
  maskClassName,
  baseDelay = 0,
  replayOnHover = true,
  autoPlay = true,
}: SlotMachineLabelProps) {
  const [spin, setSpin] = useState(0);
  const [active, setActive] = useState(false);

  useEffect(() => {
    if (!autoPlay) return;
    setActive(false);
    const timer = window.setTimeout(() => setActive(true), baseDelay * 1000);
    return () => window.clearTimeout(timer);
  }, [autoPlay, baseDelay, spin]);

  return (
    <span
      className={cn("inline-flex items-end leading-none", className)}
      aria-label={value}
      onMouseEnter={replayOnHover ? () => setSpin((n) => n + 1) : undefined}
    >
      {value.split("").map((char, i) => (
        <SlotLetter
          key={`${spin}-${i}-${char}`}
          letter={char}
          index={i}
          active={active}
          duration={duration}
          maskClassName={maskClassName}
        />
      ))}
    </span>
  );
}
