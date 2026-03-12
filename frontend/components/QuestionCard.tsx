import { ReactNode } from "react";
import { motion } from "framer-motion";
import GlassCard from "./GlassCard";

interface QuestionCardProps {
  questionId: string;
  questionText: string;
  children: ReactNode;
  className?: string;
}

export default function QuestionCard({
  questionId,
  questionText,
  children,
  className = "",
}: QuestionCardProps) {
  return (
    <motion.div
      key={questionId}
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -20, scale: 0.95 }}
      transition={{ duration: 0.4, ease: [0.4, 0, 0.2, 1] }}
      className={className}
    >
      <GlassCard variant="strong">
        <div className="mb-2">
          <span className="text-sm font-mono text-blue-400/70">
            Question #{questionId}
          </span>
        </div>
        <h2 className="text-2xl md:text-3xl font-semibold mb-8 text-center leading-tight">
          {questionText}
        </h2>
        <div className="space-y-3">{children}</div>
      </GlassCard>
    </motion.div>
  );
}
