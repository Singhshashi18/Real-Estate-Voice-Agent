"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  Calendar,
  Clock,
  Mail,
  Mic,
  Phone,
  Sparkles,
  Star,
  UserPlus,
  Zap,
} from "lucide-react";

const stats = [
  { value: "30s", label: "Response time", icon: Zap },
  { value: "24/7", label: "Voice availability", icon: Clock },
  { value: "100%", label: "Calendar sync", icon: Calendar },
  { value: "14d", label: "Booking window", icon: Sparkles },
];

const steps = [
  {
    step: "01",
    icon: UserPlus,
    title: "Create account",
    text: "Sign up and connect Google Calendar in one setup.",
  },
  {
    step: "02",
    icon: Mic,
    title: "Start voice session",
    text: "Open Inbound Agent and tap the orb to talk.",
  },
  {
    step: "03",
    icon: Calendar,
    title: "Pick a slot",
    text: "Agent checks live availability and confirms details.",
  },
  {
    step: "04",
    icon: Mail,
    title: "Invite sent",
    text: "Google Calendar + Meet link emailed instantly.",
  },
];

const features = [
  {
    icon: Mic,
    title: "Natural voice",
    text: "No menus. Callers speak like a real receptionist.",
  },
  {
    icon: Calendar,
    title: "Smart scheduling",
    text: "Mon–Fri 9 AM–9 PM IST · 30-min slots.",
  },
  {
    icon: Mail,
    title: "Auto invites",
    text: "Meet links and calendar invites on every booking.",
  },
  {
    icon: Phone,
    title: "Twilio-ready",
    text: "Browser today. Phone lines in Phase 2.",
  },
];

const testimonials = [
  {
    name: "Priya Sharma",
    role: "Founder, Nova Labs",
    quote:
      "Inbound Agent replaced our manual scheduling. Clients book while we're in meetings — zero back-and-forth.",
    stars: 5,
  },
  {
    name: "Arjun Mehta",
    role: "Sales Lead",
    quote:
      "The voice flow feels human. Real-time calendar checks mean we never double-book.",
    stars: 5,
  },
  {
    name: "Sneha Reddy",
    role: "Independent consultant",
    quote:
      "Setup took minutes. Google Meet invites go out automatically. Exactly what I needed.",
    stars: 5,
  },
  {
    name: "Rahul Verma",
    role: "Agency owner",
    quote:
      "The orange-gradient UI is slick, but the real win is bookings landing on my calendar without me lifting a finger.",
    stars: 5,
  },
];

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <p className="text-[#ff3c00] text-xs font-semibold uppercase tracking-[0.2em] mb-3 font-space">
      {children}
    </p>
  );
}

const itemVariants = {
  hidden: { opacity: 0, y: 28 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: {
      delay: i * 0.08,
      duration: 0.55,
      ease: [0.25, 0.1, 0.25, 1] as const,
    },
  }),
};

export function GradientLandingSections() {
  const doubled = [...testimonials, ...testimonials];

  return (
    <div className="bg-gray-950 text-white font-space">
      {/* Stats */}
      <section id="stats" className="relative py-24 px-6 md:px-12 border-t border-white/5">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_60%_40%_at_50%_0%,rgba(255,60,0,0.08),transparent)]" />
        <div className="relative max-w-6xl mx-auto">
          <div className="text-center mb-14">
            <SectionLabel>By the numbers</SectionLabel>
            <h2 className="text-3xl md:text-5xl font-inter font-medium tracking-tight">
              Built for{" "}
              <span className="font-instrument italic text-[#ff3c00]">speed</span>
            </h2>
          </div>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
            {stats.map((stat, i) => (
              <motion.div
                key={stat.label}
                custom={i}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true, margin: "-60px" }}
                variants={itemVariants}
                className="group rounded-2xl border border-white/10 bg-gray-900/50 p-6 md:p-8 text-center hover:border-[#ff3c00]/30 hover:bg-[#ff3c00]/5 transition-all duration-300"
              >
                <stat.icon className="h-5 w-5 text-[#ff3c00] mx-auto mb-4 opacity-80 group-hover:scale-110 transition-transform" />
                <p className="text-3xl md:text-4xl font-bold mb-1">{stat.value}</p>
                <p className="text-sm text-gray-400">{stat.label}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="py-24 px-6 md:px-12">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14">
            <SectionLabel>How it works</SectionLabel>
            <h2 className="text-3xl md:text-5xl font-inter font-medium tracking-tight">
              Live in{" "}
              <span className="font-instrument italic text-[#ff3c00]">four steps</span>
            </h2>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {steps.map((item, i) => (
              <motion.div
                key={item.step}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                variants={itemVariants}
                className="relative rounded-2xl border border-white/10 bg-gradient-to-b from-gray-900/80 to-gray-950 p-6 overflow-hidden"
              >
                <div className="absolute top-0 right-0 w-24 h-24 bg-[#ff3c00]/10 blur-2xl rounded-full" />
                <span className="text-xs font-mono text-[#ff3c00]">{item.step}</span>
                <item.icon className="h-7 w-7 text-white mt-4 mb-4" />
                <h3 className="font-semibold text-lg mb-2">{item.title}</h3>
                <p className="text-sm text-gray-400 leading-relaxed">{item.text}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-24 px-6 md:px-12 border-t border-white/5">
        <div className="max-w-6xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <SectionLabel>Features</SectionLabel>
              <h2 className="text-3xl md:text-5xl font-inter font-medium tracking-tight mb-6">
                Everything a receptionist does —{" "}
                <span className="font-instrument italic text-[#ff3c00]">automated</span>
              </h2>
              <p className="text-gray-400 text-lg leading-relaxed mb-8">
                Voice, calendar, and email wired together. Your callers get a
                premium experience; you get a full calendar without the admin.
              </p>
              <Link
                href="/signup"
                className="inline-flex items-center gap-2 rounded-full bg-[#ff3c00] hover:bg-[#ff5520] text-white px-8 py-3.5 font-semibold transition-all hover:scale-105"
              >
                Try it free
                <span aria-hidden>→</span>
              </Link>
            </div>
            <div className="grid sm:grid-cols-2 gap-4">
              {features.map((f, i) => (
                <motion.div
                  key={f.title}
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true }}
                  variants={itemVariants}
                  className="rounded-2xl border border-white/10 bg-gray-900/40 p-5 hover:border-[#ff3c00]/25 transition-colors"
                >
                  <f.icon className="h-6 w-6 text-[#ff3c00] mb-3" />
                  <h3 className="font-semibold mb-1">{f.title}</h3>
                  <p className="text-sm text-gray-500">{f.text}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials — marquee */}
      <section id="testimonials" className="py-24 overflow-hidden border-t border-white/5">
        <div className="text-center mb-12 px-6">
          <SectionLabel>Testimonials</SectionLabel>
          <h2 className="text-3xl md:text-5xl font-inter font-medium tracking-tight">
            Teams{" "}
            <span className="font-instrument italic text-[#ff3c00]">love it</span>
          </h2>
        </div>

        <div className="relative">
          <div className="absolute left-0 top-0 bottom-0 w-24 bg-gradient-to-r from-gray-950 to-transparent z-10" />
          <div className="absolute right-0 top-0 bottom-0 w-24 bg-gradient-to-l from-gray-950 to-transparent z-10" />
          <div className="flex animate-marquee w-max gap-6 px-3">
            {doubled.map((t, i) => (
              <div
                key={`${t.name}-${i}`}
                className="w-[320px] md:w-[380px] shrink-0 rounded-2xl border border-white/10 bg-gray-900/60 p-6 backdrop-blur-sm"
              >
                <div className="flex gap-1 mb-4">
                  {Array.from({ length: t.stars }).map((_, j) => (
                    <Star
                      key={j}
                      className="h-4 w-4 fill-[#ff3c00] text-[#ff3c00]"
                    />
                  ))}
                </div>
                <p className="text-gray-300 text-sm leading-relaxed mb-6">
                  &ldquo;{t.quote}&rdquo;
                </p>
                <p className="font-semibold text-sm">{t.name}</p>
                <p className="text-xs text-gray-500">{t.role}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-24 px-6 md:px-12">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-4xl mx-auto relative rounded-3xl overflow-hidden border border-white/10"
        >
          <div className="absolute inset-0 flex">
            {Array.from({ length: 9 }).map((_, i) => (
              <div
                key={i}
                className="flex-1 h-full opacity-30"
                style={{
                  background: "linear-gradient(to top, rgb(255, 60, 0), transparent)",
                  transform: `scaleY(${0.4 + (Math.abs(i - 4) / 4) * 0.6})`,
                  transformOrigin: "bottom",
                }}
              />
            ))}
          </div>
          <div className="relative bg-gray-950/80 backdrop-blur-xl p-10 md:p-16 text-center">
            <h2 className="text-3xl md:text-4xl font-inter font-medium mb-4">
              Ready to answer every call?
            </h2>
            <p className="text-gray-400 mb-8 max-w-lg mx-auto">
              Join founders using Inbound Agent to book meetings by voice — no
              code, no phone tree, no missed leads.
            </p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Link
                href="/signup"
                className="px-8 py-4 rounded-full bg-white text-black font-semibold hover:scale-105 transition-transform"
              >
                Get started free
              </Link>
              <Link
                href="/login"
                className="px-8 py-4 rounded-full border border-white/20 hover:border-[#ff3c00]/50 transition-colors"
              >
                Sign in
              </Link>
            </div>
          </div>
        </motion.div>
      </section>

      <footer className="border-t border-white/5 py-10 px-6 text-center text-sm text-gray-600">
        <p className="flex items-center justify-center gap-2 mb-2">
          <Phone className="h-4 w-4 text-[#ff3c00]" />
          <span className="text-white font-semibold">Inbound Agent</span>
        </p>
        © {new Date().getFullYear()} — AI receptionist for modern teams
      </footer>
    </div>
  );
}
