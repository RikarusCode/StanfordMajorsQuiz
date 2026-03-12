import { motion } from "framer-motion";

interface AnswerChoiceProps {
  value: number;
  label: string;
  isSelected: boolean;
  onClick: () => void;
}

export default function AnswerChoice({
  value,
  label,
  isSelected,
  onClick,
}: AnswerChoiceProps) {
  return (
    <motion.button
      whileHover={{ scale: 1.015, x: 2 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      style={{ willChange: "transform" }}
      className={`transform-gpu w-full p-5 rounded-xl text-left transition-colors duration-150 relative overflow-hidden ${
        isSelected
          ? "glass-strong bg-blue-600/30 border-2 border-blue-500/50 shadow-lg shadow-blue-500/20"
          : "glass hover:bg-white/10 border border-white/10 hover:border-white/20"
      }`}
    >
      {/* Selected indicator */}
      {isSelected && (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className="absolute top-0 left-0 w-full h-full bg-gradient-to-r from-blue-600/20 to-transparent"
        />
      )}
      
      <div className="relative flex items-center justify-between">
        <span
          className={`font-medium text-lg ${
            isSelected ? "text-white" : "text-gray-200"
          }`}
        >
          {label}
        </span>
        <div className="flex items-center gap-3">
          {/* Value badge */}
          <motion.span
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className={`px-3 py-1 rounded-full text-sm font-semibold ${
              isSelected
                ? "bg-blue-500 text-white"
                : "bg-white/10 text-gray-400"
            }`}
          >
            {value}
          </motion.span>
          
          {/* Checkmark for selected */}
          {isSelected && (
            <motion.svg
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              className="w-6 h-6 text-blue-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2.5}
                d="M5 13l4 4L19 7"
              />
            </motion.svg>
          )}
        </div>
      </div>
    </motion.button>
  );
}
