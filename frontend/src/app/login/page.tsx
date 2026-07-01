"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { AuthForm } from "@/components/auth/auth-form";
import { AuthPageLoader } from "@/components/auth/auth-page-loader";
import { AuthShell } from "@/components/auth/auth-shell";
import { useAuth } from "@/context/auth-context";
import { POST_AUTH_ROUTE } from "@/lib/routes";

export default function LoginPage() {
  const router = useRouter();
  const { user, loading } = useAuth();

  useEffect(() => {
    if (!loading && user) router.replace(POST_AUTH_ROUTE);
  }, [loading, user, router]);

  if (loading || user) return <AuthPageLoader />;

  return (
    <AuthShell mode="login">
      <AuthForm mode="login" />
    </AuthShell>
  );
}
