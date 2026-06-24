"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";

import { AppSidebar } from "@/components/app/app-sidebar";
import { GradientBars } from "@/components/ui/gradient-bars";
import { useAuth } from "@/context/auth-context";

export function AppShell({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { user, loading } = useAuth();
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/login");
    }
  }, [loading, user, router]);

  if (loading || !user) {
    return (
      <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-gray-950 text-gray-400">
        <GradientBars />
        <div className="relative z-10 flex flex-col items-center gap-3">
          <Loader2 className="h-10 w-10 animate-spin text-[#ff3c00]" />
          <span className="text-sm font-space">Loading workspace…</span>
        </div>
      </div>
    );
  }

  return (
    <div className="relative flex h-screen overflow-hidden bg-gray-950 text-white">
      <AppSidebar collapsed={collapsed} onToggle={() => setCollapsed((c) => !c)} />
      <main className="relative min-w-0 flex-1 overflow-x-hidden overflow-y-auto bg-gray-950">
        <GradientBars />
        <div className="relative z-10 min-h-full">{children}</div>
      </main>
    </div>
  );
}
