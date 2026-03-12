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
          <h1 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-blue-400 via-blue-500 to-blue-600 bg-clip-text text-transparent">
            Can’t figure out what to major in at Stanford?
          </h1>
          <div className="text-lg text-gray-300 mt-6 max-w-3xl mx-auto leading-relaxed space-y-3">
            <p>
              If you've wasted hours searching online like I have, 
              you probably know that most “major quizzes” ask the 
              same fixed questions and give vague answers.
            </p>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <GlassCard variant="strong" className="mb-8">
            <h2 className="text-2xl font-semibold mb-6">Why This Quiz Is Different</h2>
            <div className="space-y-5 text-gray-300 text-sm leading-relaxed text-left">
              <div>
                <p className="font-semibold text-white mb-1">Stanford-Specific</p>
                <p>
                  Most quizzes recommend broad fields like “business” or “science.”
                  This system evaluates actual Stanford majors and interdisciplinary
                  programs, helping you explore options that exist here.
                </p>
              </div>

              <div>
                <p className="font-semibold text-white mb-1">Adaptive Questioning</p>
                <p>
                  The quiz pulls from a large bank of questions and dynamically chooses
                  the most informative next question based on your previous answers.
                  That means shorter quizzes and more precise results. Quizzes end 
                  early if the algorithm is confident!
                </p>
              </div>

              <div>
                <p className="font-semibold text-white mb-1">Information-Theoretic Design</p>
                <p>
                  Behind the scenes, the system models your responses probabilistically and
                  uses Shannon entropy and Bayesian updating to reduce uncertainty about
                  your best-fit major.
                </p>
              </div>
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
