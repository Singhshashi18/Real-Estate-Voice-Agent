"use client";

import { useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";

import type { TranscriptLine } from "@/lib/realtime-transcript";
import { cn } from "@/lib/utils";

type CallTranscriptProps = {
  lines: TranscriptLine[];
  agentName?: string;
  active: boolean;
  className?: string;
};

export function CallTranscript({
  lines,
  agentName = "Sara",
  active,
  className,
}: CallTranscriptProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    el.scrollTop = el.scrollHeight;
  }, [lines]);

  return (
    <div
      className={cn(
        "flex w-full max-w-xl flex-col overflow-hidden rounded-2xl border border-gray-800/80 bg-gray-950/50",
        className,
      )}
    >
      <div className="shrink-0 border-b border-gray-800/80 px-4 py-2.5">
        <p className="text-[10px] font-medium uppercase tracking-widest text-[#ff3c00]/70 font-space">
          Live transcript
        </p>
      </div>

      <div
        ref={scrollRef}
        className="min-h-0 flex-1 space-y-2.5 overflow-y-auto overscroll-contain px-4 py-3"
      >
        {!active && lines.length === 0 && (
          <p className="py-6 text-center text-sm text-gray-600 font-space">
            Your conversation with {agentName} will appear here.
          </p>
        )}

        <AnimatePresence initial={false}>
          {lines.map((line) => (
            <motion.div
              key={line.id}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              className={cn(
                "flex",
                line.role === "user" ? "justify-end" : "justify-start",
              )}
            >
              <div
                className={cn(
                  "max-w-[90%] rounded-2xl px-3 py-2 text-sm leading-relaxed font-space",
                  line.role === "user"
                    ? "bg-white/95 text-gray-950"
                    : "border border-[#ff3c00]/15 bg-[#ff3c00]/8 text-gray-100",
                )}
              >
                <p className="mb-0.5 text-[10px] font-semibold uppercase tracking-wider opacity-60">
                  {line.role === "user" ? "You" : agentName}
                  {line.streaming ? " · …" : ""}
                </p>
                <p>{line.text}</p>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}
