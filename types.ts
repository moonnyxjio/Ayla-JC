export interface Story {
  id: string;
  title: string;
  content: string[][];
  coverImage: string;
}

export interface WordAnalysis {
  koreanMeaning: string;
  phonics: string;
}

export type WordAnalyses = Record<string, WordAnalysis>;

export interface SentenceAnalysisData {
  wordAnalyses: WordAnalyses;
  chunkedTranslation: string;
}

export type SpellingQuestion = {
  word: string;
  phonics: string;
  koreanMeaning: string;
};

export type ScrambleQuestion = {
  sentence: string[];
  originalSentence: string;
  translationHint: string;
};

export type ReadingQuestion = {
  sentence: string;
};

export type Question =
  | { type: 'spelling'; data: SpellingQuestion }
  | { type: 'scramble'; data: ScrambleQuestion }
  | { type: 'reading'; data: ReadingQuestion };


export interface IncorrectAnswer {
  type: 'spelling' | 'scramble' | 'reading';
  question: string;
  userAnswer: string;
  correctAnswer: string;
}

export interface QuizResult {
  storyId: string;
  storyTitle: string;
  day: number;
  score: number;
  totalQuestions: number;
  spellingScore: { correct: number; total: number };
  scrambleScore: { correct: number; total: number };
  readingScore: { correct: number; total: number };
  incorrectAnswers: IncorrectAnswer[];
  studentName: string;
}

export interface UserProfile {
  name: string;
}

// e.g., { "robot-0": true, "robot-1": true }
export type ProgressData = Record<string, boolean>;

export type View = 'profiles' | 'home' | 'book' | 'learning' | 'quiz' | 'certification' | 'admin';