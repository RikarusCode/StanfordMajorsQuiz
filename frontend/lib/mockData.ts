import type { Major } from "./api";

// This file is kept as legacy mock data from early frontend development.
// It is not used in the production app, but it must typecheck for builds.
export type Question = {
  id: string;
  text: string;
};

export const mockQuestions: Question[] = [
  {
    id: "q1",
    text: "I enjoy using quantitative tools to understand social or economic behavior.",
  },
  {
    id: "q2",
    text: "I prefer working with concrete problems that have clear solutions.",
  },
  {
    id: "q3",
    text: "I find satisfaction in writing and debugging code.",
  },
  {
    id: "q4",
    text: "I enjoy reading dense academic texts and analyzing arguments.",
  },
  {
    id: "q5",
    text: "I'm interested in understanding how biological systems work.",
  },
  {
    id: "q6",
    text: "I prefer creative, open-ended projects over structured assignments.",
  },
  {
    id: "q7",
    text: "I'm comfortable with ambiguity and multiple valid interpretations.",
  },
  {
    id: "q8",
    text: "I want to work on problems that have direct real-world impact.",
  },
];

export const mockMajors: Major[] = [
  {
    id: "computer_science",
    name: "Computer Science",
    link: "https://majors.stanford.edu/opportunities/computer-science",
    probability: 0.42,
  },
  {
    id: "symbolic_systems",
    name: "Symbolic Systems",
    link: "https://majors.stanford.edu/opportunities/symbolic-systems",
    probability: 0.19,
  },
  {
    id: "mathematics",
    name: "Mathematics",
    link: "https://majors.stanford.edu/opportunities/mathematics",
    probability: 0.14,
  },
  {
    id: "data_science",
    name: "Data Science",
    link: "https://majors.stanford.edu/opportunities/data-science",
    probability: 0.09,
  },
  {
    id: "economics",
    name: "Economics",
    link: "https://majors.stanford.edu/opportunities/economics",
    probability: 0.06,
  },
];
