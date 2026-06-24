"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Loader2 } from "lucide-react";
import { useSearchParams } from "next/navigation";

import { AuthShell } from "@/components/auth/auth-shell";
import { useAuth } from "@/context/auth-context";
import { api } from "@/lib/api";

export default function AuthCallbackClient() {
  const searchParams = useSearchParams();
  const { completeOAuth } = useAuth();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = searchParams.get("token");
    const oauthError = searchParams.get("error");

    if (oauthError) {
      setError(oauthError);
      return;
    }

    if (!token) {
      setError("Missing sign-in token. Please try again.");
      return;
    }

    api
      .me(token)
      .then((user) => completeOAuth(token, user))
      .catch(() => setError("Could not verify your session. Please sign in again."));
  }, [searchParams, completeOAuth]);

  return (
    <AuthShell mode="login">
      <div className="w-full max-w-sm mx-auto rounded-2xl border border-gray-800 bg-gray-950/80 p-8 text-center shadow-xl">
        {error ? (
          <>
            <p className="mb-4 text-sm text-red-300 font-space">{error}</p>
            <Link
              href="/login"
              className="inline-flex rounded-xl bg-white px-4 py-2 text-sm font-semibold text-black hover:bg-gray-100 font-space"
            >
              Back to sign in
            </Link>
          </>
        ) : (
          <div className="flex flex-col items-center gap-3 text-gray-400">
            <Loader2 className="h-8 w-8 animate-spin text-[#ff3c00]" />
            <p className="text-sm font-space">Completing sign-in…</p>
          </div>
        )}
      </div>
    </AuthShell>
  );
}
