"use client";

import { useState, useEffect, Suspense } from "react";
import { motion } from "framer-motion";
import { useRouter, useSearchParams } from "next/navigation";
import {
  Button,
  CenteredContainer,
  ErrorMessage,
  GlassCard,
  LoadingSpinner,
  PageShell,
} from "@/components";
import { api, type Major } from "@/lib/api";

type ResultsState = {
  majors: Major[];
  entropy: number;
  topProbability: number;
  questionsAsked: number;
  entropyHistory: number[];
  infoGainHistory: number[];
};

function ResultsContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const sessionId = searchParams.get("session_id");

  const [results, setResults] = useState<ResultsState | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchResults() {
      if (!sessionId) {
        setError("No session ID provided");
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        setError(null);
        const response = await api.getResults(sessionId);
        if (cancelled) return;
        setResults({
          majors: response.majors,
          entropy: response.entropy,
          topProbability: response.top_probability,
          questionsAsked: response.questions_asked,
          entropyHistory: response.entropy_history,
          infoGainHistory: response.info_gain_history,
        });
      } catch (err) {
        if (cancelled) return;
        setError(
          err instanceof Error
            ? err.message
            : "Failed to load results. Please try again."
        );
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    fetchResults();
    return () => {
      cancelled = true;
    };
  }, [sessionId]);

  // Loading state
  if (isLoading) {
    return (
      <PageShell centered maxWidth="6xl">
        <div className="text-center">
          <LoadingSpinner size="lg" className="mb-4" />
          <p className="text-gray-300">Loading your results...</p>
        </div>
      </PageShell>
    );
  }

  // Error state
  if (error || !results) {
    return (
      <PageShell centered maxWidth="6xl">
        <ErrorMessage
          message={error || "No results available"}
          onRetry={() => router.push("/")}
        />
        <div className="mt-4 flex justify-center">
          <Button onClick={() => router.push("/")} variant="primary">
            Back to Home
          </Button>
        </div>
      </PageShell>
    );
  }

  return (
    <PageShell maxWidth="6xl">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-12"
          >
            <h1 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-blue-400 via-blue-500 to-blue-600 bg-clip-text text-transparent">
              Your Major Recommendations
            </h1>
            <p className="text-xl text-gray-300">
              Based on your responses, here are your top matches
            </p>
          </motion.div>

          {/* Results Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <GlassCard variant="strong" className="mb-8">
              <div className="mb-6">
                <p className="text-sm text-gray-400 mb-2">
                  Click each program name to explore more
                </p>
              </div>

              <div className="space-y-4">
                {results.majors.map((major, index) => (
                  <motion.div
                    key={major.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="glass rounded-xl p-5 hover:bg-white/5 transition-colors duration-150"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <a
                        href={major.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xl font-semibold text-blue-400 hover:text-blue-300 transition-colors"
                      >
                        {major.name}
                      </a>
                      <span className="text-blue-400 font-semibold text-xl min-w-[4rem] text-right">
                        {(major.probability * 100).toFixed(2)}%
                      </span>
                    </div>
                    <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${major.probability * 100}%` }}
                        transition={{
                          delay: index * 0.1 + 0.2,
                          duration: 0.6,
                          ease: [0.4, 0, 0.2, 1],
                        }}
                        className="h-full bg-gradient-to-r from-blue-500 to-blue-600 rounded-full"
                      />
                    </div>
                  </motion.div>
                ))}
              </div>
            </GlassCard>
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
          >
            <GlassCard>
              <div className="text-center">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.3, type: "spring" }}
                  className="text-4xl font-bold text-blue-400 mb-2"
                >
                  {results.questionsAsked}
                </motion.div>
                <div className="text-sm text-gray-400">Questions Asked</div>
              </div>
            </GlassCard>
            <GlassCard>
              <div className="text-center">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.4, type: "spring" }}
                  className="text-4xl font-bold text-blue-400 mb-2"
                >
                  {(results.topProbability * 100).toFixed(0)}%
                </motion.div>
                <div className="text-sm text-gray-400">Top Match Confidence</div>
              </div>
            </GlassCard>
            <GlassCard>
              <div className="text-center">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.5, type: "spring" }}
                  className="text-4xl font-bold text-blue-400 mb-2"
                >
                  {results.entropy.toFixed(2)}
                </motion.div>
                <div className="text-sm text-gray-400">Entropy (bits)</div>
              </div>
            </GlassCard>
          </motion.div>

          {/* Disclaimer */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            <GlassCard className="mb-8">
              <p className="text-sm text-gray-400 text-center leading-relaxed">
                This quiz is for fun and educational purposes only. It is not
                official academic advice. Please consult with academic advisors
                for guidance on major selection.
              </p>
            </GlassCard>
          </motion.div>

          {/* Actions */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="flex justify-center gap-4"
          >
            <Button onClick={() => router.push("/quiz")} variant="primary">
              Retake Quiz
            </Button>
            <Button onClick={() => router.push("/")} variant="secondary">
              Back to Home
            </Button>
          </motion.div>
    </PageShell>
  );
}

export default function ResultsPage() {
  return (
    <Suspense
      fallback={
        <PageShell centered maxWidth="6xl">
          <div className="text-center">
            <LoadingSpinner size="lg" className="mb-4" />
            <p className="text-gray-300">Loading...</p>
          </div>
        </PageShell>
      }
    >
      <ResultsContent />
    </Suspense>
  );
}
