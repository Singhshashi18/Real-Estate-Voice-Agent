"use client";

import { getPasswordStrength } from "@/lib/password-strength";

export function PasswordStrengthBar({ password }: { password: string }) {
  const { score, label, color } = getPasswordStrength(password);

  if (!password) return null;

  return (
    <div className="mt-2 space-y-1.5">
      <div className="flex gap-1">
        {[1, 2, 3, 4].map((level) => (
          <div
            key={level}
            className={`h-1 flex-1 rounded-full transition-colors ${
              score >= level ? color : "bg-gray-800"
            }`}
          />
        ))}
      </div>
      <p className="text-xs text-gray-500 font-space">
        Password strength:{" "}
        <span
          className={
            score <= 1
              ? "text-red-400"
              : score === 2
                ? "text-orange-400"
                : score === 3
                  ? "text-yellow-400"
                  : "text-emerald-400"
          }
        >
          {label}
        </span>
      </p>
    </div>
  );
}
