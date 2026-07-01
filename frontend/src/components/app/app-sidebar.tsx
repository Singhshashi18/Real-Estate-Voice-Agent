"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  ChevronLeft,
  ChevronRight,
  History,
  LayoutDashboard,
  LogOut,
  Phone,
  PhoneIncoming,
  PhoneOutgoing,
} from "lucide-react";

import { useAuth } from "@/context/auth-context";
import { cn } from "@/lib/utils";

type AppSidebarProps = {
  collapsed: boolean;
  onToggle: () => void;
};

const overviewLink = {
  href: "/dashboard",
  label: "Dashboard",
  icon: LayoutDashboard,
  description: "Stats & analytics",
};

const agentLinks = [
  {
    href: "/inbound",
    label: "Inbound",
    icon: PhoneIncoming,
    description: "Receive & schedule",
    active: true,
  },
  {
    href: "/outbound",
    label: "Outbound",
    icon: PhoneOutgoing,
    description: "Coming soon",
    active: false,
  },
];

export function AppSidebar({ collapsed, onToggle }: AppSidebarProps) {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const OverviewIcon = overviewLink.icon;

  return (
    <motion.aside
      animate={{ width: collapsed ? 72 : 260 }}
      transition={{ duration: 0.25, ease: [0.25, 0.1, 0.25, 1] }}
      className="relative z-20 flex h-screen shrink-0 flex-col border-r border-white/5 bg-gray-950/95 backdrop-blur-sm"
    >
      <div className="flex h-16 items-center justify-between border-b border-white/5 px-3">
        <AnimatePresence mode="wait">
          {!collapsed && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex items-center gap-2 overflow-hidden pl-1"
            >
              <Phone className="h-5 w-5 shrink-0 text-[#ff3c00]" />
              <span className="whitespace-nowrap text-sm font-bold tracking-tighter font-space">
                Inbound Agent
              </span>
            </motion.div>
          )}
        </AnimatePresence>
        <button
          type="button"
          onClick={onToggle}
          className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-gray-500 transition-colors hover:bg-white/5 hover:text-white"
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </button>
      </div>

      <nav className="flex-1 space-y-6 overflow-y-auto p-3">
        <div>
          {!collapsed && (
            <p className="mb-2 px-3 text-[10px] font-semibold uppercase tracking-widest text-gray-600 font-space">
              Overview
            </p>
          )}
          <ul className="space-y-1">
            <li>
              <Link
                href={overviewLink.href}
                title={collapsed ? overviewLink.label : undefined}
                className={cn(
                  "flex items-center gap-3 rounded-xl px-3 py-2.5 transition-colors font-space",
                  collapsed && "justify-center px-0",
                  pathname === overviewLink.href
                    ? "border border-[#ff3c00]/25 bg-[#ff3c00]/10 text-[#ff3c00]"
                    : "text-gray-400 hover:bg-white/[0.04] hover:text-white",
                )}
              >
                <OverviewIcon className="h-4 w-4 shrink-0" />
                {!collapsed && (
                  <div className="min-w-0">
                    <p className="text-sm font-medium">{overviewLink.label}</p>
                    <p className="text-xs text-gray-500">{overviewLink.description}</p>
                  </div>
                )}
              </Link>
            </li>
          </ul>
        </div>

        <div>
          {!collapsed && (
            <p className="mb-2 px-3 text-[10px] font-semibold uppercase tracking-widest text-gray-600 font-space">
              Agents
            </p>
          )}
          <ul className="space-y-1">
            {agentLinks.map((item) => {
              const isActive = pathname === item.href;
              const Icon = item.icon;

              if (!item.active) {
                return (
                  <li key={item.href}>
                    <div
                      title={collapsed ? item.label : undefined}
                      className={cn(
                        "flex cursor-not-allowed items-center gap-3 rounded-xl px-3 py-2.5 text-gray-600",
                        collapsed && "justify-center px-0",
                      )}
                    >
                      <Icon className="h-4 w-4 shrink-0" />
                      {!collapsed && (
                        <div className="min-w-0">
                          <p className="text-sm font-medium font-space">{item.label}</p>
                          <p className="text-xs text-gray-600 font-space">{item.description}</p>
                        </div>
                      )}
                    </div>
                  </li>
                );
              }

              return (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    title={collapsed ? item.label : undefined}
                    className={cn(
                      "flex items-center gap-3 rounded-xl px-3 py-2.5 transition-colors font-space",
                      collapsed && "justify-center px-0",
                      isActive
                        ? "border border-[#ff3c00]/25 bg-[#ff3c00]/10 text-[#ff3c00]"
                        : "text-gray-400 hover:bg-white/[0.04] hover:text-white",
                    )}
                  >
                    <Icon className="h-4 w-4 shrink-0" />
                    {!collapsed && (
                      <div className="min-w-0">
                        <p className="text-sm font-medium">{item.label}</p>
                        <p className="text-xs text-gray-500">{item.description}</p>
                      </div>
                    )}
                  </Link>
                </li>
              );
            })}
          </ul>
        </div>

        <div>
          {!collapsed && (
            <p className="mb-2 px-3 text-[10px] font-semibold uppercase tracking-widest text-gray-600 font-space">
              Activity
            </p>
          )}
          <Link
            href="/history"
            title={collapsed ? "Call history" : undefined}
            className={cn(
              "flex items-center gap-3 rounded-xl px-3 py-2.5 transition-colors font-space",
              collapsed && "justify-center px-0",
              pathname === "/history"
                ? "border border-white/10 bg-white/[0.06] text-white"
                : "text-gray-400 hover:bg-white/[0.04] hover:text-white",
            )}
          >
            <History className="h-4 w-4 shrink-0" />
            {!collapsed && <span className="text-sm font-medium">Call history</span>}
          </Link>
        </div>
      </nav>

      <div className="border-t border-white/5 p-3">
        {!collapsed && user && (
          <div className="mb-2 rounded-xl border border-white/5 bg-gray-900/60 px-3 py-2">
            <p className="truncate text-sm font-medium text-white font-space">{user.name}</p>
            <p className="truncate text-xs text-gray-500 font-space">{user.email}</p>
          </div>
        )}
        <button
          type="button"
          onClick={logout}
          className={cn(
            "flex w-full items-center rounded-xl py-2.5 text-gray-400 transition-colors hover:bg-white/5 hover:text-white font-space",
            collapsed ? "justify-center px-0" : "justify-start gap-2 px-3",
          )}
        >
          <LogOut className="h-4 w-4 shrink-0" />
          {!collapsed && <span className="text-sm">Logout</span>}
        </button>
      </div>
    </motion.aside>
  );
}
