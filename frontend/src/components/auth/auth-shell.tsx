"use client";

import Link from "next/link";
import { Phone } from "lucide-react";

function GradientBars() {
  const numBars = 15;

  const calculateHeight = (index: number, total: number) => {
    const position = index / (total - 1);
    const maxHeight = 100;
    const minHeight = 30;
    const center = 0.5;
    const distanceFromCenter = Math.abs(position - center);
    const heightPercentage = Math.pow(distanceFromCenter * 2, 1.2);
    return minHeight + (maxHeight - minHeight) * heightPercentage;
  };

  return (
    <div className="absolute inset-x-0 bottom-0 h-[45%] z-0 overflow-hidden pointer-events-none">
      <div className="flex h-full">
        {Array.from({ length: numBars }).map((_, index) => {
          const height = calculateHeight(index, numBars);
          return (
            <div
              key={index}
              style={{
                flex: "1 0 calc(100% / 15)",
                maxWidth: "calc(100% / 15)",
                height: "100%",
                background: "linear-gradient(to top, rgb(255, 60, 0), transparent)",
                transform: `scaleY(${height / 100})`,
                transformOrigin: "bottom",
                animation: "pulseBar 2s ease-in-out infinite alternate",
                animationDelay: `${index * 0.1}s`,
              }}
            />
          );
        })}
      </div>
      <div className="absolute inset-0 bg-gradient-to-b from-gray-950 via-transparent to-gray-950/80" />
    </div>
  );
}

type AuthShellProps = {
  mode: "login" | "signup";
  children: React.ReactNode;
};

export function AuthShell({ mode, children }: AuthShellProps) {
  const isLogin = mode === "login";

  return (
    <div className="relative min-h-screen bg-gray-950 text-white overflow-hidden">
      <GradientBars />

      <header className="relative z-10 border-b border-white/5">
        <div className="mx-auto flex h-16 max-w-5xl items-center justify-between px-6">
          <Link href="/" className="flex items-center gap-2 font-bold tracking-tighter font-space">
            <Phone className="h-5 w-5 text-[#ff3c00]" />
            Inbound Agent
          </Link>
          <Link
            href="/"
            className="text-sm text-gray-400 hover:text-white transition-colors font-space"
          >
            Back to home
          </Link>
        </div>
      </header>

      <main className="relative z-10 mx-auto flex min-h-[calc(100vh-4rem)] max-w-lg flex-col justify-center px-6 py-10">
        <div className="w-full mx-auto text-center mb-6">
          <h1 className="mb-2 text-center font-inter text-3xl sm:text-4xl font-medium tracking-tight">
            {isLogin ? (
              <>
                Welcome{" "}
                <span className="font-instrument italic text-[#ff3c00]">back</span>
              </>
            ) : (
              <>
                Create your{" "}
                <span className="font-instrument italic text-[#ff3c00]">account</span>
              </>
            )}
          </h1>
          <p className="text-gray-400 text-sm font-space max-w-xs mx-auto">
            {isLogin
              ? "Sign in to run your voice receptionist and manage bookings."
              : "Set up your account to start scheduling meetings by voice."}
          </p>
        </div>
        <div className="w-full flex justify-center">
          {children}
        </div>
      </main>
    </div>
  );
}
