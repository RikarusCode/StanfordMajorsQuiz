import { ReactNode } from "react";
import Image from "next/image";
import CenteredContainer from "@/components/CenteredContainer";

type MaxWidth = "sm" | "md" | "lg" | "xl" | "2xl" | "4xl" | "6xl";

export default function PageShell({
  children,
  maxWidth = "6xl",
  centered = false,
  className = "",
}: {
  children: ReactNode;
  maxWidth?: MaxWidth;
  centered?: boolean;
  className?: string;
}) {
  return (
    <main
      className={[
        "min-h-screen relative z-10",
        centered ? "flex items-center justify-center p-4" : "p-4 md:p-8",
        className,
      ].join(" ")}
    >
      <CenteredContainer maxWidth={maxWidth}>
        <header className="mb-8 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Image
              src="/class-logo-gen.png"
              alt="Stanford Major Quiz logo"
              width={56}
              height={56}
              className="rounded-xl shadow-lg shadow-black/40 border border-white/15 bg-white/5"
              priority={false}
            />
            <div className="leading-tight">
              <p className="text-base sm:text-lg font-semibold text-white">
                Stanford Major Quiz
              </p>
              <p className="text-[11px] sm:text-xs text-gray-400">
                Adaptive Bayesian recommender for Stanford majors
              </p>
            </div>
          </div>
        </header>
        {children}
      </CenteredContainer>
    </main>
  );
}

