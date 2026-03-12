import { motion } from "framer-motion";

interface ProgressBarProps {
  progress: number;
  max?: number;
  showLabel?: boolean;
  questionId?: string;
  className?: string;
}

export default function ProgressBar({
  progress,
  max = 20,
  showLabel = true,
  questionId,
  className = "",
}: ProgressBarProps) {
  const percentage = Math.min((progress / max) * 100, 100);

  return (
    <div className={`w-full ${className}`}>
      {showLabel && (
        <div className="flex justify-between items-center mb-3">
          <span className="text-sm font-mono text-gray-400">
            {questionId ? `Question #${questionId}` : `Question ${progress}`}
          </span>
          <span className="text-sm text-gray-400">
            {progress} / {max}
          </span>
        </div>
      )}
      <div className="w-full h-2.5 bg-white/10 rounded-full overflow-hidden backdrop-blur-sm">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.4, ease: [0.4, 0, 0.2, 1] }}
          className="h-full bg-gradient-to-r from-blue-500 via-blue-600 to-blue-500 rounded-full relative overflow-hidden"
        >
          {/* Shimmer effect */}
          <motion.div
            className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
            animate={{
              x: ["-100%", "100%"],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "linear",
            }}
          />
        </motion.div>
      </div>
    </div>
  );
}
