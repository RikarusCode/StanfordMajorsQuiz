import { ReactNode } from "react";
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
      <CenteredContainer maxWidth={maxWidth}>{children}</CenteredContainer>
    </main>
  );
}

