import type { LucideIcon } from "lucide-react";

import { cn } from "@/lib/utils";

type StatCardProps = {
  label: string;
  value: string;
  hint?: string;
  icon: LucideIcon;
  trend?: string;
  accent?: "orange" | "emerald" | "blue" | "violet";
};

const accentStyles = {
  orange: "border-[#ff3c00]/20 bg-[#ff3c00]/10 text-[#ff3c00]",
  emerald: "border-emerald-500/20 bg-emerald-500/10 text-emerald-400",
  blue: "border-sky-500/20 bg-sky-500/10 text-sky-400",
  violet: "border-violet-500/20 bg-violet-500/10 text-violet-400",
};

export function StatCard({
  label,
  value,
  hint,
  icon: Icon,
  trend,
  accent = "orange",
}: StatCardProps) {
  return (
    <div className="group relative overflow-hidden rounded-2xl border border-white/5 bg-gray-950/70 p-5 backdrop-blur-sm transition-colors hover:border-white/10">
      <div className="pointer-events-none absolute -right-6 -top-6 h-24 w-24 rounded-full bg-[#ff3c00]/5 blur-2xl transition-opacity group-hover:opacity-100" />
      <div className="relative flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-xs font-medium uppercase tracking-wider text-gray-500 font-space">
            {label}
          </p>
          <p className="mt-2 text-3xl font-semibold tracking-tight text-white font-inter">
            {value}
          </p>
          {hint && (
            <p className="mt-1 text-xs text-gray-500 font-space">{hint}</p>
          )}
          {trend && (
            <p className="mt-2 text-xs font-medium text-emerald-400 font-space">{trend}</p>
          )}
        </div>
        <div
          className={cn(
            "flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border",
            accentStyles[accent],
          )}
        >
          <Icon className="h-5 w-5" />
        </div>
      </div>
    </div>
  );
}
