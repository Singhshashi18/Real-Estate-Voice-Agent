"use client";

import { useState } from "react";
import Link from "next/link";
import { Eye, EyeOff, Loader2, Lock, Mail, User } from "lucide-react";

import { PasswordStrengthBar } from "@/components/auth/password-strength-bar";
import { SocialAuthButtons } from "@/components/auth/social-auth-buttons";
import { useAuth } from "@/context/auth-context";
import { getPasswordStrength } from "@/lib/password-strength";
import { cn } from "@/lib/utils";

type AuthFormProps = {
  mode: "login" | "signup";
};

function AuthField({
  id,
  label,
  icon: Icon,
  children,
}: {
  id: string;
  label: string;
  icon: React.ElementType;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label htmlFor={id} className="mb-1.5 block text-xs font-medium text-gray-400 font-space">
        {label}
      </label>
      <div className="relative">
        <Icon className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-500" />
        {children}
      </div>
    </div>
  );
}

const fieldClass =
  "w-full rounded-xl border border-gray-700 bg-gray-900/60 py-2.5 pl-10 pr-4 text-sm text-white placeholder:text-gray-600 outline-none transition-colors focus:border-[#ff3c00]/50 focus:ring-1 focus:ring-[#ff3c00]/30 font-space";

export function AuthForm({ mode }: AuthFormProps) {
  const { login, register } = useAuth();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const isLogin = mode === "login";

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    if (!isLogin) {
      const strength = getPasswordStrength(password);
      if (password.length < 8 || strength.score < 2) {
        setError("Use at least 8 characters with mixed letters and numbers.");
        setLoading(false);
        return;
      }
    }

    try {
      if (isLogin) {
        await login(email, password);
      } else {
        await register(name, email, password);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="w-full max-w-sm mx-auto">
      <div className="rounded-2xl border border-gray-800 bg-gray-950/80 p-6 shadow-xl backdrop-blur-sm">
        <SocialAuthButtons />

        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-800" />
          </div>
          <p className="relative mx-auto w-fit bg-gray-950 px-3 text-xs text-gray-500 font-space">
            or continue with email
          </p>
        </div>

        {error && (
          <p className="mb-4 rounded-xl border border-red-500/30 bg-red-500/10 px-3 py-2.5 text-center text-xs text-red-300 font-space">
            {error}
          </p>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <AuthField id="name" label="Full name" icon={User}>
              <input
                id="name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="John Doe"
                className={fieldClass}
                autoComplete="name"
                required
              />
            </AuthField>
          )}

          <AuthField id="email" label="Email address" icon={Mail}>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@company.com"
              className={fieldClass}
              autoComplete="email"
              required
            />
          </AuthField>

          <AuthField id="password" label="Password" icon={Lock}>
            <input
              id="password"
              type={showPassword ? "text" : "password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={isLogin ? "Your password" : "Min. 8 characters recommended"}
              minLength={6}
              className={cn(fieldClass, "pr-10")}
              autoComplete={isLogin ? "current-password" : "new-password"}
              required
            />
            <button
              type="button"
              onClick={() => setShowPassword((v) => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300"
              aria-label={showPassword ? "Hide password" : "Show password"}
            >
              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </AuthField>
          {!isLogin && <PasswordStrengthBar password={password} />}

          {isLogin && (
            <div className="flex justify-end">
              <button
                type="button"
                className="text-xs text-gray-500 hover:text-[#ff3c00] transition-colors font-space"
                onClick={() =>
                  setError("Password reset is coming soon. Sign in with Google if enabled.")
                }
              >
                Forgot password?
              </button>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-white py-2.5 text-sm font-semibold text-black transition-colors hover:bg-gray-100 disabled:opacity-60 font-space"
          >
            {loading && <Loader2 className="h-4 w-4 animate-spin" />}
            {loading
              ? isLogin
                ? "Signing in…"
                : "Creating account…"
              : isLogin
                ? "Sign in"
                : "Create account"}
          </button>
        </form>
      </div>

      <p className="mt-5 text-center text-sm text-gray-500 font-space">
        {isLogin ? (
          <>
            Don&apos;t have an account?{" "}
            <Link href="/signup" className="font-medium text-[#ff3c00] hover:underline">
              Sign up
            </Link>
          </>
        ) : (
          <>
            Already have an account?{" "}
            <Link href="/login" className="font-medium text-[#ff3c00] hover:underline">
              Sign in
            </Link>
          </>
        )}
      </p>

      <p className="mt-4 text-center text-[11px] leading-relaxed text-gray-600 font-space px-2">
        By continuing, you agree to our Terms of Service and Privacy Policy.
      </p>
    </div>
  );
}
