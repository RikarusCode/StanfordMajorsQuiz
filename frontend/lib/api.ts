/**
 * API client for the Stanford Major Quiz FastAPI backend.
 */

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "https://stanfordmajorsquiz-production.up.railway.app";

export interface Major {
  id: string;
  name: string;
  link: string;
  probability: number;
}

export interface StartQuizResponse {
  session_id: string;
  question_id: string;
  question_text: string;
  question_number: string;
  top_majors: Major[];
}

export interface AnswerRequest {
  session_id: string;
  question_id: string;
  answer: number;
}

export interface AnswerResponse {
  question_id: string | null;
  question_text: string | null;
  question_number: string | null;
  top_majors: Major[];
  entropy: number;
  top_probability: number;
  questions_asked: number;
  is_complete: boolean;
}

export interface ResultsResponse {
  session_id: string;
  majors: Major[];
  major_order: string[];
  entropy: number;
  top_probability: number;
  questions_asked: number;
  entropy_history: number[];
  info_gain_history: number[];
  posterior_history: number[][];
  question_number_history: string[];
}

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public response?: any
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const config: RequestInit = {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  };

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch {
        errorData = { detail: response.statusText };
      }

      throw new ApiError(
        errorData.detail || `HTTP ${response.status}`,
        response.status,
        errorData
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(
      `Network error: ${error instanceof Error ? error.message : "Unknown error"}`,
      0
    );
  }
}

export const api = {
  /**
   * Start a new quiz session.
   */
  async startQuiz(): Promise<StartQuizResponse> {
    return fetchApi<StartQuizResponse>("/start", {
      method: "POST",
    });
  },

  /**
   * Submit an answer to a question.
   */
  async submitAnswer(request: AnswerRequest): Promise<AnswerResponse> {
    return fetchApi<AnswerResponse>("/answer", {
      method: "POST",
      body: JSON.stringify(request),
    });
  },

  /**
   * Get final results for a completed quiz.
   */
  async getResults(sessionId: string): Promise<ResultsResponse> {
    return fetchApi<ResultsResponse>(`/results/${sessionId}`);
  },

  /**
   * Health check.
   */
  async healthCheck(): Promise<{ status: string }> {
    return fetchApi<{ status: string }>("/health");
  },
};
