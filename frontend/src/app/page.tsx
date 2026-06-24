import { GradientLandingSections } from "@/components/gradient-landing-sections";
import { GradientBarHeroSection } from "@/components/ui/gradient-bar-hero-section";

export default function HomePage() {
  return (
    <main className="bg-gray-950">
      <GradientBarHeroSection />
      <GradientLandingSections />
    </main>
  );
}
