"use client";

import React, { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import {
  Code2,
  Globe,
  Menu,
  Phone,
  Share2,
  X,
} from "lucide-react";

import { SlotMachineLabel, SlotMachineText } from "@/components/ui/slot-machine-text";

type AvatarProps = {
  imageSrc: string;
  delay: number;
};

const Avatar: React.FC<AvatarProps> = ({ imageSrc, delay }) => (
  <div
    className="relative h-6 w-6 sm:h-8 sm:w-8 md:h-10 md:w-10 rounded-full overflow-hidden border-2 border-gray-700 shadow-lg animate-fadeIn"
    style={{ animationDelay: `${delay}ms` }}
  >
    <Image src={imageSrc} alt="User avatar" fill className="object-cover" sizes="40px" />
    <div className="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent" />
  </div>
);

const TrustElements: React.FC = () => {
  const avatars = [
    "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&h=100&fit=crop",
    "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop",
    "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&h=100&fit=crop",
    "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop",
  ];

  return (
    <div className="inline-flex items-center space-x-3 bg-gray-900/60 backdrop-blur-sm rounded-full py-2 px-3 sm:py-2 sm:px-4 text-xs sm:text-sm border border-white/5">
      <div className="flex -space-x-2 sm:-space-x-3">
        {avatars.map((avatar, index) => (
          <Avatar key={index} imageSrc={avatar} delay={index * 200} />
        ))}
      </div>
      <p
        className="text-white animate-fadeIn whitespace-nowrap font-space"
        style={{ animationDelay: "800ms" }}
      >
        <span className="text-[#ff3c00] font-semibold">
          <SlotMachineText value="2.4K+" maskClassName="from-gray-900" duration={1.8} />
        </span>{" "}
        meetings booked
      </p>
    </div>
  );
};

const HeroCta: React.FC = () => (
  <div className="relative z-10 w-full flex flex-col sm:flex-row gap-3 justify-center animate-fadeIn animation-delay-300">
    <Link
      href="/signup"
      className="px-8 py-3.5 sm:py-4 rounded-full bg-white hover:bg-gray-100 text-black text-sm sm:text-base font-semibold font-space transition-all duration-300 transform hover:scale-105 text-center shadow-[0_0_30px_rgba(255,60,0,0.25)]"
    >
      Start free — voice agent
    </Link>
    <Link
      href="/login"
      className="px-8 py-3.5 sm:py-4 rounded-full bg-gray-900/60 border border-gray-700 hover:border-[#ff3c00]/50 text-white text-sm sm:text-base font-space transition-all duration-300 backdrop-blur-sm text-center"
    >
      Sign in
    </Link>
  </div>
);

const GradientBars: React.FC = () => {
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
    <div className="absolute inset-0 z-0 overflow-hidden">
      <div
        className="flex h-full"
        style={{
          width: "100%",
          transform: "translateZ(0)",
          backfaceVisibility: "hidden",
        }}
      >
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
                transition: "transform 0.5s ease-in-out",
                animation: "pulseBar 2s ease-in-out infinite alternate",
                animationDelay: `${index * 0.1}s`,
              }}
            />
          );
        })}
      </div>
      <div className="absolute inset-0 bg-gradient-to-b from-gray-950/40 via-transparent to-gray-950" />
    </div>
  );
};

const Navbar: React.FC = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const links = [
    { href: "#features", label: "Features" },
    { href: "#how-it-works", label: "How it works" },
    { href: "#testimonials", label: "Testimonials" },
    { href: "#stats", label: "Stats" },
  ];

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-transparent py-6 px-6 md:px-12">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center">
          <Link href="/" className="flex items-center gap-2 group">
            <Phone className="h-5 w-5 text-[#ff3c00]" />
            <span className="text-white font-bold text-xl tracking-tighter font-space">
              <SlotMachineLabel
                value="Inbound Agent"
                maskClassName="from-gray-950"
                duration={0.75}
                baseDelay={0.1}
              />
            </span>
          </Link>

          <div className="hidden md:flex items-center space-x-8">
            {links.map((link, i) => (
              <a
                key={link.href}
                href={link.href}
                className="text-gray-300 hover:text-[#ff3c00] transition-colors duration-300 font-space text-sm"
              >
                <SlotMachineLabel
                  value={link.label}
                  maskClassName="from-gray-950"
                  duration={0.7}
                  baseDelay={0.25 + i * 0.12}
                />
              </a>
            ))}
            <Link
              href="/login"
              className="text-gray-300 hover:text-white transition-colors font-space text-sm"
            >
              <SlotMachineLabel
                value="Sign in"
                maskClassName="from-gray-950"
                duration={0.7}
                baseDelay={0.75}
              />
            </Link>
            <Link
              href="/signup"
              className="bg-white hover:bg-gray-100 text-black px-5 py-2 rounded-full transition-all duration-300 transform hover:scale-105 font-space text-sm font-semibold"
            >
              <SlotMachineLabel
                value="Get started"
                maskClassName="from-white"
                duration={0.65}
                baseDelay={0.9}
                className="text-black"
              />
            </Link>
          </div>

          <div className="md:hidden">
            <button
              type="button"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="text-white"
              aria-label="Toggle menu"
            >
              {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>

        {isMenuOpen && (
          <div className="md:hidden mt-4 bg-gray-900/95 backdrop-blur-sm rounded-lg p-4 animate-fadeIn border border-white/10">
            <div className="flex flex-col space-y-4">
              {links.map((link, i) => (
                <a
                  key={link.href}
                  href={link.href}
                  onClick={() => setIsMenuOpen(false)}
                  className="text-gray-300 hover:text-white transition-colors py-2 font-space"
                >
                  <SlotMachineLabel
                    value={link.label}
                    maskClassName="from-gray-900"
                    duration={0.65}
                    baseDelay={0.1 + i * 0.08}
                  />
                </a>
              ))}
              <Link href="/login" className="text-gray-300 py-2 font-space">
                <SlotMachineLabel
                  value="Sign in"
                  maskClassName="from-gray-900"
                  duration={0.65}
                  baseDelay={0.45}
                />
              </Link>
              <Link
                href="/signup"
                className="bg-white text-black px-5 py-2 rounded-full text-center font-space font-semibold"
              >
                <SlotMachineLabel
                  value="Get started"
                  maskClassName="from-white"
                  duration={0.6}
                  baseDelay={0.55}
                  className="text-black"
                />
              </Link>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export function GradientBarHeroSection() {
  return (
    <section className="relative min-h-screen flex flex-col items-center px-6 sm:px-8 md:px-12 overflow-hidden">
      <div className="absolute inset-0 bg-gray-950" />
      <GradientBars />
      <Navbar />

      <div className="relative z-10 text-center w-full max-w-4xl mx-auto flex flex-col items-center justify-center min-h-screen py-8 sm:py-16">
        <div className="mb-6 sm:mb-8">
          <TrustElements />
        </div>

        <h1 className="w-full text-white leading-tight tracking-tight mb-6 sm:mb-8 animate-fadeIn px-4">
          <span className="block font-inter font-medium text-[clamp(1.75rem,6vw,3.75rem)]">
            Your AI receptionist,
          </span>
          <span className="block font-instrument italic text-[clamp(1.75rem,6vw,3.75rem)] text-[#ff3c00]">
            always on call.
          </span>
        </h1>

        <div className="mb-8 sm:mb-10 px-4 max-w-2xl">
          <p className="text-[clamp(1rem,2.5vw,1.25rem)] text-gray-400 leading-relaxed animate-fadeIn animation-delay-200 font-space">
            Answers inbound calls, checks your Google Calendar, books 30-minute
            meetings, and sends Meet invites — by voice.
          </p>
        </div>

        <div className="w-full max-w-2xl mb-8 px-4">
          <HeroCta />
        </div>

        <div className="flex justify-center space-x-6">
          <a
            href="#"
            className="text-gray-500 hover:text-[#ff3c00] transition-colors duration-300"
            aria-label="Share"
          >
            <Share2 className="w-5 h-5 sm:w-[22px] sm:h-[22px]" />
          </a>
          <a
            href="#"
            className="text-gray-500 hover:text-[#ff3c00] transition-colors duration-300"
            aria-label="Website"
          >
            <Globe className="w-5 h-5 sm:w-[22px] sm:h-[22px]" />
          </a>
          <a
            href="#"
            className="text-gray-500 hover:text-[#ff3c00] transition-colors duration-300"
            aria-label="GitHub"
          >
            <Code2 className="w-5 h-5 sm:w-[22px] sm:h-[22px]" />
          </a>
        </div>
      </div>
    </section>
  );
}

// shadcn-style export alias
export const Component = GradientBarHeroSection;
