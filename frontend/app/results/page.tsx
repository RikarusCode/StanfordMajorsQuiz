"use client";

import { useState, useEffect, Suspense } from "react";
import { motion } from "framer-motion";
import { useRouter, useSearchParams } from "next/navigation";
import {
  Button,
  ErrorMessage,
  GlassCard,
  LoadingSpinner,
  EntropyChart,
  InfoGainChart,
  PageShell,
  TopMajorsEvolutionChart,
} from "@/components";
import { api, type Major } from "@/lib/api";

type ResultsState = {
  majors: Major[];
  majorOrder: string[];
  entropy: number;
  topProbability: number;
  questionsAsked: number;
  entropyHistory: number[];
  infoGainHistory: number[];
  posteriorHistory: number[][];
  questionNumberHistory: string[];
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
          majorOrder: response.major_order,
          entropy: response.entropy,
          topProbability: response.top_probability,
          questionsAsked: response.questions_asked,
          entropyHistory: response.entropy_history,
          infoGainHistory: response.info_gain_history,
          posteriorHistory: response.posterior_history,
          questionNumberHistory: response.question_number_history,
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
              Based on your responses, here are your top matches!
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
                <p className="text-sm text-gray-300 mb-2">
                   Click each program name to explore more
                </p>
              </div>

              <div className="space-y-4">
                {results.majors.slice(0, 10).map((major, index) => (
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

          {/* Educational / algorithm section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25 }}
          >
            <GlassCard variant="strong" className="mb-8">
              <h2 className="text-2xl font-semibold mb-2">
                What the algorithm did (Bayes + Information Theory)
              </h2>
              <p className="text-gray-300 leading-relaxed">
                Most quizzes, even famous ones like Myers Briggs, ask the same 
                fixed questions with broad matches.
                After each answer, we update a probability distribution over majors using{" "}
                <span className="text-white font-medium">Bayes’ Rule</span>. Then we pick the next
                question that maximizes expected{" "}
                <span className="text-white font-medium">information gain</span>—the expected
                reduction in{" "}
                <span className="text-white font-medium">Shannon entropy</span> of the posterior. 
                This means we can get more precise results in fewer questions.
                
              </p>
            </GlassCard>
          </motion.div>

          {/* Entropy reduction over time */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <GlassCard variant="strong" className="mb-8">
              <h3 className="text-xl font-semibold mb-2">
                Uncertainty Reduction (Entropy) Over Time
              </h3>
              <p className="text-gray-300 text-sm leading-relaxed mb-4">
                Entropy measures how uncertain we are about the best-fit major. Lower is more
                confident.
              </p>
              <EntropyChart entropyHistory={results.entropyHistory} />
            </GlassCard>
          </motion.div>

          {/* Information gain per question */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.35 }}
          >
            <GlassCard variant="strong" className="mb-8">
              <h3 className="text-xl font-semibold mb-2">
                Information Gain Per Question (Adaptive Selection)
              </h3>
              <p className="text-gray-300 text-sm leading-relaxed mb-4">
                Each bar is the expected entropy reduction for the chosen next question at that
                step.
              </p>
              <InfoGainChart infoGainHistory={results.infoGainHistory} />
            </GlassCard>
          </motion.div>

          {/* Probability evolution for top majors */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <GlassCard variant="strong" className="mb-8">
              <h3 className="text-xl font-semibold mb-2">
                Probability Evolution for Your Top Majors
              </h3>
              <p className="text-gray-300 text-sm leading-relaxed mb-4">
                Watch how Bayes updates shift probability mass as evidence accumulates.
              </p>
              {(() => {
                const topK = 5;
                const topMajors = results.majors.slice(0, topK);
                const idToIndex = new Map(
                  results.majorOrder.map((id, i) => [id, i])
                );
                const series = topMajors.map((m, i) => ({
                  name: m.name,
                  key: `m${i}`,
                  color: ["#3b82f6", "#22c55e", "#a855f7", "#f59e0b", "#ef4444"][i]!,
                  idx: idToIndex.get(m.id) ?? -1,
                }));

                const data = results.posteriorHistory.map((row, step) => {
                  const obj: Record<string, number | string> = { step };
                  series.forEach((s, i) => {
                    const p = s.idx >= 0 ? row[s.idx] ?? 0 : 0;
                    obj[`m${i}`] = p * 100;
                  });
                  return obj;
                });

                return (
                  <TopMajorsEvolutionChart
                    data={data}
                    series={series.map(({ name, key, color }) => ({ name, key, color }))}
                  />
                );
              })()}
            </GlassCard>
          </motion.div>

          {/* Adaptive vs linear comparison (hypothetical linear) */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.45 }}
          >
            <GlassCard variant="strong" className="mb-8">
              <h3 className="text-xl font-semibold mb-2">
                Adaptive vs Linear Test: A Direct Comparison
              </h3>
              <p className="text-gray-300 text-sm leading-relaxed mb-4">
                A fixed-order test can waste questions on things that don’t matter for you. Below we
                overlay your adaptive entropy curve with a hypothetical linear test that reduces
                uncertainty much more slowly.
              </p>
              {(() => {
                const adaptive = results.entropyHistory;
                const initial = adaptive[0] ?? 0;
                const linearSteps = 20;
                const target = initial * 0.8;
                const linear = [initial];
                for (let q = 1; q <= linearSteps; q++) {
                  const progress = q / linearSteps;
                  const ent = initial - (initial - target) * Math.pow(progress, 0.5);
                  linear.push(ent);
                }
                return <EntropyChart entropyHistory={adaptive} linearEntropyHistory={linear} />;
              })()}
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
                This quiz is for fun and educational purposes only. It is meant 
                to inspire curiosity and further exploration, not to be taken as 
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
