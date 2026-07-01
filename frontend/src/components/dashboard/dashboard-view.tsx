"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowRight,
  CalendarDays,
  CheckCircle2,
  Clock3,
  LayoutDashboard,
  Phone,
  PhoneIncoming,
  TrendingUp,
} from "lucide-react";

import { CallsChart } from "@/components/dashboard/calls-chart";
import { StatCard } from "@/components/dashboard/stat-card";
import { useAuth } from "@/context/auth-context";
import {
  computeCallAnalytics,
  formatTalkTime,
} from "@/lib/call-analytics";
import {
  formatCallTime,
  formatDuration,
  getCallHistory,
  subscribeCallHistory,
  type CallRecord,
} from "@/lib/call-history";
import { cn } from "@/lib/utils";
import { useEffect, useMemo, useState } from "react";

function StatusPill({ status }: { status: CallRecord["status"] }) {
  const styles = {
    completed: "bg-emerald-500/15 text-emerald-400",
    failed: "bg-red-500/15 text-red-400",
    "in-progress": "bg-[#ff3c00]/15 text-[#ff3c00]",
  };
  return (
    <span
      className={cn(
        "rounded-full px-2 py-0.5 text-[10px] font-medium capitalize font-space",
        styles[status],
      )}
    >
      {status.replace("-", " ")}
    </span>
  );
}

export function DashboardView() {
  const { user } = useAuth();
  const [records, setRecords] = useState<CallRecord[]>([]);

  useEffect(() => {
    setRecords(getCallHistory());
    return subscribeCallHistory(() => setRecords(getCallHistory()));
  }, []);

  const analytics = useMemo(() => computeCallAnalytics(records), [records]);
  const firstName = user?.name?.split(" ")[0] ?? "there";

  return (
    <div className="mx-auto max-w-6xl px-6 py-8 md:px-10 md:py-10">
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <div className="mb-2 flex items-center gap-2 text-[#ff3c00]">
            <LayoutDashboard className="h-4 w-4" />
            <span className="text-xs font-semibold uppercase tracking-widest font-space">
              Overview
            </span>
          </div>
          <h1 className="font-inter text-2xl font-medium tracking-tight sm:text-3xl">
            Welcome back,{" "}
            <span className="font-instrument italic text-[#ff3c00]">{firstName}</span>
          </h1>
          <p className="mt-1 text-sm text-gray-500 font-space">
            Call analytics and agent performance at a glance
          </p>
        </div>
        <Link
          href="/inbound"
          className="inline-flex h-10 items-center justify-center gap-2 rounded-full bg-[#ff3c00] px-5 text-sm font-semibold text-white transition-colors hover:bg-[#e63600] font-space"
        >
          <PhoneIncoming className="h-4 w-4" />
          Start inbound call
        </Link>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Total calls"
          value={String(analytics.totalCalls)}
          hint={`${analytics.callsThisWeek} this week`}
          icon={Phone}
          accent="orange"
        />
        <StatCard
          label="Success rate"
          value={`${analytics.successRate}%`}
          hint={`${analytics.completedCalls} completed`}
          icon={TrendingUp}
          accent="emerald"
        />
        <StatCard
          label="Avg duration"
          value={
            analytics.avgDurationSec > 0
              ? formatDuration(analytics.avgDurationSec)
              : "—"
          }
          hint={
            analytics.totalTalkTimeSec > 0
              ? `${formatTalkTime(analytics.totalTalkTimeSec)} total talk time`
              : "No completed calls yet"
          }
          icon={Clock3}
          accent="blue"
        />
        <StatCard
          label="Calls today"
          value={String(analytics.callsToday)}
          hint={`${analytics.inboundCalls} inbound · ${analytics.outboundCalls} outbound`}
          icon={CalendarDays}
          accent="violet"
        />
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-3">
        <motion.section
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-2xl border border-white/5 bg-gray-950/70 p-5 backdrop-blur-sm lg:col-span-2"
        >
          <div className="mb-5 flex items-center justify-between">
            <div>
              <h2 className="text-sm font-semibold text-white font-space">Call volume</h2>
              <p className="text-xs text-gray-500 font-space">Last 7 days</p>
            </div>
            <span className="rounded-full border border-white/10 bg-white/5 px-2.5 py-1 text-[10px] text-gray-400 font-space">
              Live from browser sessions
            </span>
          </div>
          <CallsChart data={analytics.callsByDay} />
        </motion.section>

        <motion.section
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05 }}
          className="rounded-2xl border border-white/5 bg-gray-950/70 p-5 backdrop-blur-sm"
        >
          <h2 className="text-sm font-semibold text-white font-space">Agent mix</h2>
          <p className="mb-5 text-xs text-gray-500 font-space">Inbound vs outbound</p>
          <div className="space-y-4">
            {[
              { label: "Inbound", count: analytics.inboundCalls, color: "bg-[#ff3c00]" },
              { label: "Outbound", count: analytics.outboundCalls, color: "bg-violet-500" },
            ].map((row) => {
              const pct =
                analytics.totalCalls > 0
                  ? Math.round((row.count / analytics.totalCalls) * 100)
                  : 0;
              return (
                <div key={row.label}>
                  <div className="mb-1.5 flex items-center justify-between text-xs font-space">
                    <span className="text-gray-400">{row.label}</span>
                    <span className="text-white">
                      {row.count} <span className="text-gray-600">({pct}%)</span>
                    </span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-gray-900">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${pct}%` }}
                      transition={{ duration: 0.5, ease: "easeOut" }}
                      className={cn("h-full rounded-full", row.color)}
                    />
                  </div>
                </div>
              );
            })}
          </div>
          <div className="mt-6 grid grid-cols-2 gap-3">
            <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-3">
              <div className="flex items-center gap-1.5 text-emerald-400">
                <CheckCircle2 className="h-3.5 w-3.5" />
                <span className="text-[10px] uppercase tracking-wider font-space">Completed</span>
              </div>
              <p className="mt-1 text-xl font-semibold text-white font-inter">
                {analytics.completedCalls}
              </p>
            </div>
            <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-3">
              <p className="text-[10px] uppercase tracking-wider text-red-400 font-space">Failed</p>
              <p className="mt-1 text-xl font-semibold text-white font-inter">
                {analytics.failedCalls}
              </p>
            </div>
          </div>
        </motion.section>
      </div>

      <motion.section
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="mt-6 rounded-2xl border border-white/5 bg-gray-950/70 backdrop-blur-sm"
      >
        <div className="flex items-center justify-between border-b border-white/5 px-5 py-4">
          <div>
            <h2 className="text-sm font-semibold text-white font-space">Recent calls</h2>
            <p className="text-xs text-gray-500 font-space">Latest voice sessions</p>
          </div>
          <Link
            href="/history"
            className="inline-flex items-center gap-1 text-xs font-medium text-[#ff3c00] transition-colors hover:text-orange-300 font-space"
          >
            View all
            <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>

        {analytics.recentCalls.length === 0 ? (
          <div className="px-5 py-12 text-center">
            <Phone className="mx-auto mb-3 h-8 w-8 text-gray-700" />
            <p className="text-sm text-gray-400 font-space">No calls recorded yet</p>
            <p className="mt-1 text-xs text-gray-600 font-space">
              Start an inbound session to populate your dashboard
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[520px] text-left text-sm">
              <thead>
                <tr className="border-b border-white/5 text-[10px] uppercase tracking-wider text-gray-600 font-space">
                  <th className="px-5 py-3 font-medium">Agent</th>
                  <th className="px-5 py-3 font-medium">Summary</th>
                  <th className="px-5 py-3 font-medium">When</th>
                  <th className="px-5 py-3 font-medium">Duration</th>
                  <th className="px-5 py-3 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {analytics.recentCalls.map((record) => (
                  <tr
                    key={record.id}
                    className="border-b border-white/[0.03] transition-colors last:border-0 hover:bg-white/[0.02]"
                  >
                    <td className="px-5 py-3 capitalize text-gray-300 font-space">
                      {record.agent}
                    </td>
                    <td className="max-w-[200px] truncate px-5 py-3 text-gray-400 font-space">
                      {record.summary || "Voice session"}
                    </td>
                    <td className="px-5 py-3 text-xs text-gray-500 font-space">
                      {formatCallTime(record.startedAt)}
                    </td>
                    <td className="px-5 py-3 text-gray-400 font-space">
                      {record.durationSec != null
                        ? formatDuration(record.durationSec)
                        : "—"}
                    </td>
                    <td className="px-5 py-3">
                      <StatusPill status={record.status} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </motion.section>
    </div>
  );
}
