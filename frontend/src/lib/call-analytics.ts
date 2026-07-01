import { formatDuration, type CallRecord } from "@/lib/call-history";

export type CallAnalytics = {
  totalCalls: number;
  completedCalls: number;
  failedCalls: number;
  inProgressCalls: number;
  successRate: number;
  avgDurationSec: number;
  totalTalkTimeSec: number;
  callsToday: number;
  callsThisWeek: number;
  inboundCalls: number;
  outboundCalls: number;
  callsByDay: { key: string; label: string; count: number }[];
  recentCalls: CallRecord[];
};

function startOfDay(date: Date) {
  const d = new Date(date);
  d.setHours(0, 0, 0, 0);
  return d;
}

function startOfWeek(date: Date) {
  const d = startOfDay(date);
  const day = d.getDay();
  const mondayOffset = day === 0 ? 6 : day - 1;
  d.setDate(d.getDate() - mondayOffset);
  return d;
}

function dayKey(date: Date) {
  return date.toISOString().slice(0, 10);
}

function formatDayLabel(date: Date) {
  return date.toLocaleDateString("en-IN", { weekday: "short" });
}

export function computeCallAnalytics(records: CallRecord[]): CallAnalytics {
  const now = new Date();
  const todayStart = startOfDay(now);
  const weekStart = startOfWeek(now);

  const finished = records.filter((r) => r.status !== "in-progress");
  const completed = records.filter((r) => r.status === "completed");
  const failed = records.filter((r) => r.status === "failed");
  const inProgress = records.filter((r) => r.status === "in-progress");

  const durations = completed
    .map((r) => r.durationSec)
    .filter((d): d is number => typeof d === "number" && d > 0);

  const totalTalkTimeSec = durations.reduce((sum, d) => sum + d, 0);
  const avgDurationSec =
    durations.length > 0 ? Math.round(totalTalkTimeSec / durations.length) : 0;

  const successRate =
    finished.length > 0 ? Math.round((completed.length / finished.length) * 100) : 0;

  const callsToday = records.filter(
    (r) => startOfDay(new Date(r.startedAt)) >= todayStart,
  ).length;

  const callsThisWeek = records.filter(
    (r) => startOfDay(new Date(r.startedAt)) >= weekStart,
  ).length;

  const dayBuckets: { key: string; label: string; count: number }[] = [];
  for (let i = 6; i >= 0; i -= 1) {
    const d = new Date(todayStart);
    d.setDate(d.getDate() - i);
    dayBuckets.push({ key: dayKey(d), label: formatDayLabel(d), count: 0 });
  }

  const bucketMap = new Map(dayBuckets.map((b) => [b.key, b]));
  for (const record of records) {
    const key = dayKey(new Date(record.startedAt));
    const bucket = bucketMap.get(key);
    if (bucket) bucket.count += 1;
  }

  return {
    totalCalls: records.length,
    completedCalls: completed.length,
    failedCalls: failed.length,
    inProgressCalls: inProgress.length,
    successRate,
    avgDurationSec,
    totalTalkTimeSec,
    callsToday,
    callsThisWeek,
    inboundCalls: records.filter((r) => r.agent === "inbound").length,
    outboundCalls: records.filter((r) => r.agent === "outbound").length,
    callsByDay: dayBuckets,
    recentCalls: records.slice(0, 8),
  };
}

export function formatTalkTime(totalSec: number) {
  if (totalSec < 60) return `${totalSec}s`;
  const hours = Math.floor(totalSec / 3600);
  const minutes = Math.floor((totalSec % 3600) / 60);
  if (hours > 0) return `${hours}h ${minutes}m`;
  return formatDuration(totalSec);
}
