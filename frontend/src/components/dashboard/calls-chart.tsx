"use client";

import { motion } from "framer-motion";

type CallsChartProps = {
  data: { label: string; count: number }[];
};

export function CallsChart({ data }: CallsChartProps) {
  const max = Math.max(...data.map((d) => d.count), 1);

  return (
    <div className="flex h-44 items-end justify-between gap-2 sm:gap-3">
      {data.map((day, i) => {
        const heightPct = day.count > 0 ? Math.max((day.count / max) * 100, 12) : 4;
        return (
          <div key={day.label} className="flex min-w-0 flex-1 flex-col items-center gap-2">
            <span className="text-[10px] font-medium text-gray-500 font-space">
              {day.count > 0 ? day.count : ""}
            </span>
            <motion.div
              initial={{ height: 0, opacity: 0.4 }}
              animate={{ height: `${heightPct}%`, opacity: 1 }}
              transition={{ delay: i * 0.05, duration: 0.45, ease: "easeOut" }}
              className="w-full min-h-[4px] rounded-t-lg bg-gradient-to-t from-[#ff3c00]/80 to-orange-400/90 shadow-[0_0_20px_-6px_rgba(255,60,0,0.5)]"
            />
            <span className="truncate text-[10px] text-gray-600 font-space">{day.label}</span>
          </div>
        );
      })}
    </div>
  );
}
