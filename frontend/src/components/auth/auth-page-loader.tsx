"use client";

import { Loader2 } from "lucide-react";

export function AuthPageLoader() {
  return (
    <div className="flex min-h-[50vh] items-center justify-center">
      <div className="flex flex-col items-center gap-3 text-gray-500">
        <Loader2 className="h-8 w-8 animate-spin text-[#ff3c00]" />
        <p className="text-sm font-space">Loading…</p>
      </div>
    </div>
  );
}
