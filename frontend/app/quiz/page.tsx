"use client";

import { useState, useEffect, useCallback } from "react";
import { AnimatePresence } from "framer-motion";
import { useRouter } from "next/navigation";
import {
  AnswerChoice,
  Button,
  ErrorMessage,
  LoadingSpinner,
  PageShell,
  ProgressBar,
  QuestionCard,
  TopResultsCard,
} from "@/components";
import { api, type Major } from "@/lib/api";

const LIKERT_OPTIONS = [
  { value: 1, label: "Strongly Disagree" },
  { value: 2, label: "Disagree" },
  { value: 3, label: "Neutral" },
  { value: 4, label: "Agree" },
  { value: 5, label: "Strongly Agree" },
];

type CurrentQuestion = {
  id: string;
  text: string;
  number: string;
};

export default function QuizPage() {
  const router = useRouter();
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<CurrentQuestion | null>(
    null
  );
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [topMajors, setTopMajors] = useState<Major[]>([]);
  const [questionsAsked, setQuestionsAsked] = useState(0);
  const [isStarting, setIsStarting] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const maxQuestions = 27;

  const startQuiz = useCallback(async () => {
    try {
      setIsStarting(true);
      setError(null);
      setSelectedAnswer(null);
      const response = await api.startQuiz();
      setSessionId(response.session_id);
      setCurrentQuestion({
        id: response.question_id,
        text: response.question_text,
        number: response.question_number,
      });
      setTopMajors(response.top_majors);
      setQuestionsAsked(0);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to start quiz. Please try again."
      );
    } finally {
      setIsStarting(false);
    }
  }, []);

  useEffect(() => {
    startQuiz();
  }, [startQuiz]);

  const handleAnswer = useCallback((value: number) => {
    setSelectedAnswer(value);
  }, []);

  const handleNext = useCallback(async () => {
    if (
      selectedAnswer === null ||
      !sessionId ||
      !currentQuestion ||
      isSubmitting
    ) {
      return;
    }

    try {
      setIsSubmitting(true);
      setError(null);

      const response = await api.submitAnswer({
        session_id: sessionId,
        question_id: currentQuestion.id,
        answer: selectedAnswer,
      });

      // Update state
      setTopMajors(response.top_majors);
      setQuestionsAsked(response.questions_asked);

      if (response.is_complete) {
        // Quiz is complete, navigate to results
        router.push(`/results?session_id=${sessionId}`);
      } else if (response.question_id && response.question_text) {
        // Update to next question
        setCurrentQuestion({
          id: response.question_id,
          text: response.question_text,
          number: response.question_number || "",
        });
        setSelectedAnswer(null);
      } else {
        // No more questions but not marked complete
        router.push(`/results?session_id=${sessionId}`);
      }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to submit answer. Please try again."
      );
    } finally {
      setIsSubmitting(false);
    }
  }, [selectedAnswer, sessionId, currentQuestion, isSubmitting, router]);

  const handleBack = useCallback(() => {
    router.push("/");
  }, [router]);

  // Loading state
  if (isStarting) {
    return (
      <PageShell centered maxWidth="4xl">
        <div className="text-center">
          <LoadingSpinner size="lg" className="mb-4" />
          <p className="text-gray-300">Starting quiz...</p>
        </div>
      </PageShell>
    );
  }

  // Error state
  if (error && !currentQuestion) {
    return (
      <PageShell centered maxWidth="4xl">
        <ErrorMessage message={error} onRetry={startQuiz} />
      </PageShell>
    );
  }

  return (
    <PageShell maxWidth="6xl">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Error message (if any) */}
          {error && (
            <ErrorMessage message={error} onRetry={handleNext} className="mb-4" />
          )}

          {/* Progress Bar */}
          <ProgressBar
            progress={questionsAsked + 1}
            max={maxQuestions}
            questionId={currentQuestion?.number}
          />

          {/* Question Card with Answer Choices */}
          {currentQuestion && (
            <AnimatePresence mode="wait">
              <QuestionCard
                key={currentQuestion.id}
                questionId={currentQuestion.number}
                questionText={currentQuestion.text}
              >
                {LIKERT_OPTIONS.map((option) => (
                  <AnswerChoice
                    key={option.value}
                    value={option.value}
                    label={option.label}
                    isSelected={selectedAnswer === option.value}
                    onClick={() => handleAnswer(option.value)}
                  />
                ))}
              </QuestionCard>
            </AnimatePresence>
          )}

          {/* Navigation Buttons */}
          <div className="flex justify-between items-center pt-4">
            <Button
              onClick={handleBack}
              variant="secondary"
              className="min-w-[120px]"
              disabled={isSubmitting}
            >
              Home
            </Button>
            <Button
              onClick={handleNext}
              variant="primary"
              disabled={selectedAnswer === null || isSubmitting}
              className="min-w-[120px]"
            >
              {isSubmitting ? (
                <span className="flex items-center gap-2">
                  <LoadingSpinner size="sm" />
                  Submitting...
                </span>
              ) : (
                "Next"
              )}
            </Button>
          </div>
        </div>

        {/* Sidebar - Top Results */}
        <div className="lg:col-span-1">
          <div className="lg:sticky lg:top-8">
            <TopResultsCard majors={topMajors} />
          </div>
        </div>
      </div>
    </PageShell>
  );
}
