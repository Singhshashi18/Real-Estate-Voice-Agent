"use client";

import { PhoneOutgoing } from "lucide-react";
import { motion } from "framer-motion";

export default function OutboundPage() {
  return (
    <div className="flex min-h-full flex-col items-center justify-center px-6 py-12 text-center">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="max-w-md"
      >
        <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-2xl border border-[#ff3c00]/20 bg-[#ff3c00]/10">
          <PhoneOutgoing className="h-8 w-8 text-[#ff3c00]" />
        </div>
        <p className="mb-4 inline-flex items-center gap-2 rounded-full border border-[#ff3c00]/25 bg-[#ff3c00]/10 px-3 py-1 text-xs font-medium text-[#ff3c00] font-space">
          Phase 2
        </p>
        <h1 className="mb-3 font-inter text-2xl font-medium sm:text-3xl">
          Outbound <span className="font-instrument italic text-[#ff3c00]">agent</span>
        </h1>
        <p className="leading-relaxed text-gray-500 font-space">
          Outbound calling — follow-ups, reminders, and proactive outreach — is
          coming soon. For now, use the Inbound Agent to handle scheduling.
        </p>
      </motion.div>
    </div>
  );
}
