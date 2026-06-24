import type { Metadata } from "next";
import { Instrument_Serif, Inter, Space_Grotesk } from "next/font/google";

import { AuthProvider } from "@/context/auth-context";
import "./globals.css";

const spaceGrotesk = Space_Grotesk({
  variable: "--font-space",
  subsets: ["latin"],
});

const instrumentSerif = Instrument_Serif({
  variable: "--font-instrument",
  subsets: ["latin"],
  weight: "400",
  style: ["italic", "normal"],
});

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Inbound Agent — AI Receptionist",
  description:
    "Voice-powered inbound agent that schedules meetings on Google Calendar and sends invites.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${spaceGrotesk.variable} ${instrumentSerif.variable} ${inter.variable}`}
    >
      <body className="min-h-screen antialiased font-space bg-gray-950 text-white">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
