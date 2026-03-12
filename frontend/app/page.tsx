"use client";

import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import { AnimatedBackground, Button, GlassCard, PageShell } from "@/components";

export default function LandingPage() {
  const router = useRouter();

  return (
    <>
      <AnimatedBackground />
      <PageShell centered maxWidth="4xl">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center mb-12"
          >
            <h1 className="text-5xl md:text-6xl font-bold mb-4 bg-gradient-to-r from-blue-400 via-blue-500 to-blue-600 bg-clip-text text-transparent">
              Which Stanford Major Should I Choose?
            </h1>
            <p className="text-xl text-gray-300 mt-6 max-w-2xl mx-auto leading-relaxed">
              Discover your ideal major using adaptive Bayesian inference and
              information theory. Answer questions personalized to you, and get
              recommendations based on probability and uncertainty reduction.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <GlassCard variant="strong" className="mb-8">
              <h2 className="text-2xl font-semibold mb-6">How It Works</h2>
              <div className="space-y-6 text-gray-300">
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 }}
                  className="flex items-start gap-4"
                >
                  <div className="flex-shrink-0 w-10 h-10 rounded-full bg-blue-600/20 flex items-center justify-center text-blue-400 font-semibold text-lg">
                    1
                  </div>
                  <div>
                    <p className="font-medium text-white mb-1">
                      Adaptive Question Selection
                    </p>
                    <p className="text-sm leading-relaxed">
                      Each question is chosen to maximize information gain,
                      reducing uncertainty about your best-fit major.
                    </p>
                  </div>
                </motion.div>
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4 }}
                  className="flex items-start gap-4"
                >
                  <div className="flex-shrink-0 w-10 h-10 rounded-full bg-blue-600/20 flex items-center justify-center text-blue-400 font-semibold text-lg">
                    2
                  </div>
                  <div>
                    <p className="font-medium text-white mb-1">
                      Bayesian Inference
                    </p>
                    <p className="text-sm leading-relaxed">
                      Your answers update probabilities using Bayes' Rule,
                      refining recommendations in real-time.
                    </p>
                  </div>
                </motion.div>
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5 }}
                  className="flex items-start gap-4"
                >
                  <div className="flex-shrink-0 w-10 h-10 rounded-full bg-blue-600/20 flex items-center justify-center text-blue-400 font-semibold text-lg">
                    3
                  </div>
                  <div>
                    <p className="font-medium text-white mb-1">
                      Personalized Results
                    </p>
                    <p className="text-sm leading-relaxed">
                      Get ranked major recommendations with confidence scores
                      and detailed insights into the algorithm's reasoning.
                    </p>
                  </div>
                </motion.div>
              </div>
            </GlassCard>

            <div className="flex justify-center">
              <Button
                onClick={() => router.push("/quiz")}
                variant="primary"
                className="text-lg px-8 py-4"
              >
                Start Quiz
              </Button>
            </div>
          </motion.div>
      </PageShell>
    </>
  );
}
