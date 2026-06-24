"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { AuthForm } from "@/components/auth/auth-form";
import { AuthPageLoader } from "@/components/auth/auth-page-loader";
import { AuthShell } from "@/components/auth/auth-shell";
import { useAuth } from "@/context/auth-context";

export default function LoginPage() {
  const router = useRouter();
  const { user, loading } = useAuth();

  useEffect(() => {
    if (!loading && user) router.replace("/inbound");
  }, [loading, user, router]);

  if (loading || user) return <AuthPageLoader />;

  return (
    <AuthShell mode="login">
      <AuthForm mode="login" />
    </AuthShell>
  );
}
