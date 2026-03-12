import { motion } from "framer-motion";
import GlassCard from "./GlassCard";

interface MajorResult {
  id: string;
  name: string;
  probability: number;
}

interface TopResultsCardProps {
  majors: MajorResult[];
  className?: string;
}

function probToPct(probability: number): number {
  // API returns probability in [0, 1]. Guard against already-in-percent inputs.
  const p = probability > 1 ? probability / 100 : probability;
  if (!Number.isFinite(p)) return 0;
  const pct = Math.max(0, Math.min(1, p)) * 100;
  return pct;
}

export default function TopResultsCard({
  majors,
  className = "",
}: TopResultsCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.2 }}
      className={className}
    >
      <GlassCard>
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-semibold">Top 5 Majors</h3>
          <div className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
        </div>
        <div className="space-y-4">
          {majors.map((major, index) => {
            const pct = probToPct(major.probability);
            return (
            <motion.div
              key={major.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="space-y-2"
            >
              <div className="flex items-center justify-between">
                <span className="text-gray-300 font-medium">{major.name}</span>
                <span className="text-blue-400 font-semibold text-lg">
                  {pct.toFixed(2)}%
                </span>
              </div>
              {/* Progress bar */}
              <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${pct}%` }}
                  transition={{ delay: index * 0.1 + 0.2, duration: 0.5 }}
                  className="h-full bg-gradient-to-r from-blue-500 to-blue-600 rounded-full"
                />
              </div>
            </motion.div>
          )})}
        </div>
      </GlassCard>
    </motion.div>
  );
}
