"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { History, PhoneIncoming, PhoneOutgoing } from "lucide-react";

import {
  formatCallTime,
  formatDuration,
  getCallHistory,
  subscribeCallHistory,
  type CallRecord,
} from "@/lib/call-history";
import { cn } from "@/lib/utils";

function StatusBadge({ status }: { status: CallRecord["status"] }) {
  const styles = {
    completed: "bg-emerald-500/15 text-emerald-400 border-emerald-500/20",
    failed: "bg-red-500/15 text-red-400 border-red-500/20",
    "in-progress": "bg-[#ff3c00]/15 text-[#ff3c00] border-[#ff3c00]/20",
  };
  return (
    <span
      className={cn(
        "rounded-full border px-2.5 py-0.5 text-xs font-medium capitalize font-space",
        styles[status],
      )}
    >
      {status.replace("-", " ")}
    </span>
  );
}

export default function HistoryPage() {
  const [records, setRecords] = useState<CallRecord[]>([]);

  useEffect(() => {
    setRecords(getCallHistory());
    return subscribeCallHistory(() => setRecords(getCallHistory()));
  }, []);

  return (
    <div className="max-w-3xl px-6 py-10 md:px-10">
      <div className="mb-8">
        <div className="mb-2 flex items-center gap-2 text-[#ff3c00]">
          <History className="h-4 w-4" />
          <span className="text-xs font-semibold uppercase tracking-widest font-space">
            Activity
          </span>
        </div>
        <h1 className="font-inter text-2xl font-medium tracking-tight sm:text-3xl">
          Call <span className="font-instrument italic text-[#ff3c00]">history</span>
        </h1>
        <p className="mt-1 text-sm text-gray-500 font-space">
          Recent voice sessions from your agents
        </p>
      </div>

      {records.length === 0 ? (
        <div className="rounded-2xl border border-gray-800 bg-gray-950/60 p-12 text-center">
          <History className="mx-auto mb-4 h-10 w-10 text-gray-700" />
          <p className="text-gray-400 font-space">No calls yet</p>
          <p className="mt-1 text-sm text-gray-600 font-space">
            Start a session from the Inbound Agent to see history here
          </p>
        </div>
      ) : (
        <ul className="space-y-3">
          {records.map((record, i) => {
            const Icon = record.agent === "inbound" ? PhoneIncoming : PhoneOutgoing;
            return (
              <motion.li
                key={record.id}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.04 }}
                className="rounded-2xl border border-gray-800 bg-gray-950/60 p-4 transition-colors hover:border-gray-700"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex min-w-0 gap-3">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-[#ff3c00]/20 bg-[#ff3c00]/10">
                      <Icon className="h-4 w-4 text-[#ff3c00]" />
                    </div>
                    <div className="min-w-0">
                      <p className="font-medium capitalize font-space">
                        {record.agent} agent
                      </p>
                      <p className="truncate text-sm text-gray-500 font-space">
                        {record.summary || "Voice session"}
                      </p>
                      <p className="mt-1 text-xs text-gray-600 font-space">
                        {formatCallTime(record.startedAt)}
                        {record.durationSec != null &&
                          ` · ${formatDuration(record.durationSec)}`}
                      </p>
                    </div>
                  </div>
                  <StatusBadge status={record.status} />
                </div>
              </motion.li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
