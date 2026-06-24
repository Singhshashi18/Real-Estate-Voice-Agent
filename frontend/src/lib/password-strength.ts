export type PasswordStrength = 0 | 1 | 2 | 3 | 4;

export function getPasswordStrength(password: string): {
  score: PasswordStrength;
  label: string;
  color: string;
} {
  if (!password) {
    return { score: 0, label: "", color: "bg-gray-700" };
  }

  let points = 0;
  if (password.length >= 8) points++;
  if (password.length >= 12) points++;
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) points++;
  if (/\d/.test(password)) points++;
  if (/[^a-zA-Z0-9]/.test(password)) points++;

  if (points <= 1) return { score: 1, label: "Weak", color: "bg-red-500" };
  if (points === 2) return { score: 2, label: "Fair", color: "bg-orange-500" };
  if (points === 3) return { score: 3, label: "Good", color: "bg-yellow-500" };
  return { score: 4, label: "Strong", color: "bg-emerald-500" };
}
