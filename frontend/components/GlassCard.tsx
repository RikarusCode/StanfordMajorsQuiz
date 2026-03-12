import { motion } from "framer-motion";
import { ReactNode } from "react";

interface GlassCardProps {
  children: ReactNode;
  className?: string;
  variant?: "default" | "strong";
}

export default function GlassCard({
  children,
  className = "",
  variant = "default",
}: GlassCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={`rounded-2xl p-6 ${
        variant === "strong" ? "glass-strong" : "glass"
      } ${className}`}
    >
      {children}
    </motion.div>
  );
}
