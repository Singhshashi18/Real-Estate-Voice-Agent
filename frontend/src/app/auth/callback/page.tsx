"use client";

import { Suspense } from "react";

import { AuthPageLoader } from "@/components/auth/auth-page-loader";
import AuthCallbackClient from "./callback-client";

export default function AuthCallbackPage() {
  return (
    <Suspense fallback={<AuthPageLoader />}>
      <AuthCallbackClient />
    </Suspense>
  );
}
