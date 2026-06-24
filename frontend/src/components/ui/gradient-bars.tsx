"use client";

type GradientBarsProps = {
  className?: string;
};

export function GradientBars({ className = "" }: GradientBarsProps) {
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
    <div
      className={`pointer-events-none absolute inset-x-0 bottom-0 z-0 h-[min(42vh,360px)] overflow-hidden ${className}`}
    >
      <div
        className="flex h-full w-[calc(100%+2px)] -ml-px"
        style={{ transform: "translateZ(0)", backfaceVisibility: "hidden" }}
      >
        {Array.from({ length: numBars }).map((_, index) => {
          const height = calculateHeight(index, numBars);
          return (
            <div
              key={index}
              className="h-full shrink-0 grow"
              style={{
                width: `${100 / numBars}%`,
                background: "linear-gradient(to top, rgb(255, 60, 0), transparent)",
                transform: `scaleY(${height / 100})`,
                transformOrigin: "bottom",
                animation: "pulseBar 2s ease-in-out infinite alternate",
                animationDelay: `${index * 0.1}s`,
              }}
            />
          );
        })}
      </div>
      <div className="absolute inset-0 bg-gradient-to-t from-gray-950 via-gray-950/70 to-gray-950" />
    </div>
  );
}
